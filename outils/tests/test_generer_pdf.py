"""Générateur de PDF : quelles pages, quelle adresse, et la boucle de rendu (sans navigateur)."""
from pathlib import Path


def site_construit(tmp_path: Path) -> Path:
    site = tmp_path / "site" / "departemental"
    for page in ["index.html", "adhesions-lots/index.html", "search/index.html", "assets/x/index.html", "a/b/index.html"]:
        (site / page).parent.mkdir(parents=True, exist_ok=True)
        (site / page).write_text("<html></html>")
    return site


def test_premier_domaine(pdf):
    assert pdf.premier_domaine("guide.example.org, vps-123.ovh.net") == "guide.example.org"
    assert pdf.premier_domaine("  a.fr  b.fr ") == "a.fr"
    assert pdf.premier_domaine("") == pdf.premier_domaine(None) == "guide-liguasso.laligue.org"


def test_adresse_publique(pdf):
    assert pdf.adresse_publique("g.fr", "departemental", "adhesions-lots") == "https://g.fr/departemental/adhesions-lots/"
    assert pdf.adresse_publique("g.fr", "association", ".") == "https://g.fr/association/"


def test_pages_a_rendre_sans_les_pages_techniques(pdf, tmp_path):
    site = site_construit(tmp_path)
    pages = list(pdf.pages_a_rendre(site, "g.fr"))
    assert [p.adresse for p in pages] == [
        "https://g.fr/departemental/a/b/", "https://g.fr/departemental/adhesions-lots/", "https://g.fr/departemental/"]
    assert all(p.sortie == p.fichier.parent / "page.pdf" for p in pages)
    assert pages[1].url.endswith("adhesions-lots/index.html?pdf=https%3A%2F%2Fg.fr%2Fdepartemental%2Fadhesions-lots%2F")


def test_generer_compte_et_signale_les_pages_sans_entete(pdf, tmp_path):
    site = site_construit(tmp_path)

    class MoteurFactice:
        def __init__(self):
            self.rendues = []

        def rendre(self, page):
            self.rendues.append(page.adresse)
            if page.adresse.endswith("/a/b/"):
                return False                       # pas d'entête d'impression : pas de PDF
            page.sortie.write_text("%PDF")
            return True

    moteur, journal = MoteurFactice(), []
    assert pdf.generer([site], "g.fr", moteur, journal.append) == 2
    assert len(moteur.rendues) == 3
    assert journal == ["  ignorée (pas d'entête) : https://g.fr/departemental/a/b/"]
    assert (site / "adhesions-lots" / "page.pdf").read_text() == "%PDF"


def test_les_regles_se_chargent_sans_playwright(tmp_path):
    """Playwright n'est installé que dans l'image Docker de rendu : il ne doit pas être importé au chargement."""
    import subprocess, sys
    from conftest import RACINE
    code = ("import sys, builtins; vrai = builtins.__import__\n"
            "def bloque(nom, *a, **k):\n"
            "    if nom.startswith('playwright'): raise ImportError('playwright absent')\n"
            "    return vrai(nom, *a, **k)\n"
            "builtins.__import__ = bloque\n"
            f"import importlib.util; s = importlib.util.spec_from_file_location('g', r'{RACINE / 'generer-pdf.py'}')\n"
            "m = importlib.util.module_from_spec(s); sys.modules['g'] = m; s.loader.exec_module(m)\n"
            "print(m.premier_domaine('a.fr'))")
    resultat = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
    assert resultat.stdout.strip() == "a.fr", resultat.stderr
