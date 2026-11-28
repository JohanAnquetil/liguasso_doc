#!/usr/bin/env python3
"""Crée le PDF de chaque page des guides construits, pour le bouton « PDF ».

    python generer-pdf.py site/association site/departemental

Chaque page index.html reçoit, dans son dossier, un fichier page.pdf : même mise en page
que l'impression depuis le navigateur (entête du guide, chapitre et numéros de page),
mais identique pour tout le monde, quel que soit le navigateur.

Le bouton (javascripts/impression.js) télécharge ce fichier s'il existe et revient à
l'impression du navigateur sinon (rédaction locale, échec de cette étape).

Adresse publique affichée en bas des PDF : premier domaine de la variable DOMAINE.
"""
import os
import sys
import time
from pathlib import Path
from urllib.parse import quote

from playwright.sync_api import sync_playwright

# DOMAINE peut lister plusieurs domaines pour Caddy (« a.fr, b.fr ») : on garde le premier.
DOMAINE = (os.environ.get("DOMAINE") or "").replace(",", " ").split()
DOMAINE = DOMAINE[0] if DOMAINE else "guide-liguasso.laligue.org"


def pages_du_site(racine: Path):
    for page in sorted(racine.rglob("index.html")):
        # Pages techniques de MkDocs, sans intérêt en PDF
        if page.parent.name in ("search", "assets"):
            continue
        yield page


def main(sites):
    debut = time.time()
    total = 0
    with sync_playwright() as p:
        navigateur = p.chromium.launch()
        onglet = navigateur.new_page()
        for site in map(Path, sites):
            guide = site.name  # association, departemental
            for page in pages_du_site(site):
                chemin = page.parent.relative_to(site).as_posix()
                adresse = f"https://{DOMAINE}/{guide}/" + (f"{chemin}/" if chemin != "." else "")
                onglet.goto(page.resolve().as_uri() + "?pdf=" + quote(adresse, safe=""))
                onglet.evaluate("document.fonts.ready")
                if not onglet.locator(".impression-entete").count():
                    print(f"  ignorée (pas d'entête) : {guide}/{chemin}")
                    continue
                onglet.pdf(path=str(page.parent / "page.pdf"), format="A4", print_background=True)
                total += 1
        navigateur.close()
    print(f"{total} PDF créés en {time.time() - debut:.0f} s.")


if __name__ == "__main__":
    main(sys.argv[1:] or ["site/association", "site/departemental"])
