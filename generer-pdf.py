#!/usr/bin/env python3
"""Crée le PDF de chaque page des guides construits, pour le bouton « PDF ».

    python generer-pdf.py site/association site/departemental

Chaque page index.html reçoit, dans son dossier, un fichier page.pdf : même mise en page
que l'impression depuis le navigateur (entête du guide, chapitre et numéros de page),
mais identique pour tout le monde, quel que soit le navigateur.

Le bouton (javascripts/impression.js) télécharge ce fichier s'il existe et revient à
l'impression du navigateur sinon (rédaction locale, échec de cette étape).

Adresse publique affichée en bas des PDF : premier domaine de la variable DOMAINE.

Organisation : les règles (quelles pages, quelle adresse) sont des fonctions pures,
testées dans outils/tests ; le rendu passe par un « moteur » (Chromium via Playwright
en production, une doublure dans les tests).
"""
from __future__ import annotations

import os
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Iterator, Protocol
from urllib.parse import quote

DOMAINE_PAR_DEFAUT = "guide-liguasso.laligue.org"
DOSSIERS_TECHNIQUES = ("search", "assets")


# --- Règles -----------------------------------------------------------------------------

def premier_domaine(valeur: str | None) -> str:
    """DOMAINE peut lister plusieurs domaines pour Caddy (« a.fr, b.fr ») : on garde le premier."""
    domaines = (valeur or "").replace(",", " ").split()
    return domaines[0] if domaines else DOMAINE_PAR_DEFAUT


def adresse_publique(domaine: str, guide: str, chemin: str) -> str:
    """Adresse de la page sur le site publié, affichée en bas du PDF."""
    return f"https://{domaine}/{guide}/" + (f"{chemin}/" if chemin not in (".", "") else "")


@dataclass(frozen=True)
class PageARendre:
    fichier: Path          # .../site/departemental/adhesions-lots/index.html
    sortie: Path           # .../site/departemental/adhesions-lots/page.pdf
    adresse: str           # https://domaine/departemental/adhesions-lots/

    @property
    def url(self) -> str:
        """Adresse locale ouverte par le navigateur : la page indique l'adresse publique par ?pdf="""
        return self.fichier.resolve().as_uri() + "?pdf=" + quote(self.adresse, safe="")


def pages_a_rendre(site: Path, domaine: str) -> Iterator[PageARendre]:
    """Les pages d'un guide construit, sans les pages techniques de MkDocs."""
    for page in sorted(site.rglob("index.html")):
        relatif = page.parent.relative_to(site)
        if any(dossier in DOSSIERS_TECHNIQUES for dossier in relatif.parts):   # y compris les sous-dossiers
            continue
        chemin = relatif.as_posix()
        yield PageARendre(page, page.parent / "page.pdf", adresse_publique(domaine, site.name, chemin))


# --- Rendu --------------------------------------------------------------------------------

class Moteur(Protocol):
    def rendre(self, page: PageARendre) -> bool:
        """Écrit page.sortie ; False si la page n'a pas l'entête d'impression (pas de PDF)."""


class MoteurChromium:
    """Rendu par Chromium (Playwright), importé seulement ici : les règles restent testables sans lui."""

    def __enter__(self):
        from playwright.sync_api import sync_playwright
        self._playwright = sync_playwright().start()
        self._navigateur = self._playwright.chromium.launch()
        self._onglet = self._navigateur.new_page()
        return self

    def __exit__(self, *erreur):
        self._navigateur.close()
        self._playwright.stop()

    def rendre(self, page: PageARendre) -> bool:
        self._onglet.goto(page.url)
        self._onglet.evaluate("document.fonts.ready")
        if not self._onglet.locator(".impression-entete").count():
            return False
        self._onglet.pdf(path=str(page.sortie), format="A4", print_background=True)
        return True


def generer(sites: Iterable[Path], domaine: str, moteur: Moteur, journal=print) -> int:
    """Rend toutes les pages ; renvoie le nombre de PDF créés."""
    total = 0
    for site in sites:
        for page in pages_a_rendre(Path(site), domaine):
            if moteur.rendre(page):
                total += 1
            else:
                journal(f"  ignorée (pas d'entête) : {page.adresse}")
    return total


def main(arguments: list[str]) -> None:
    debut = time.time()
    sites = [Path(s) for s in (arguments or ["site/association", "site/departemental"])]
    with MoteurChromium() as moteur:
        total = generer(sites, premier_domaine(os.environ.get("DOMAINE")), moteur)
    print(f"{total} PDF créés en {time.time() - debut:.0f} s.")


if __name__ == "__main__":
    main(sys.argv[1:])
