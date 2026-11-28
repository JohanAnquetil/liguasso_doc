"""Règle métier du menu : lire les rubriques, ajouter une fiche sans toucher au reste."""
from pathlib import Path

import pytest

from liguasso_contrib.domaine.erreurs import Invalide
from liguasso_contrib.domaine.menu import ajouter_au_menu, lire_menu

RACINE = Path(__file__).resolve().parents[3]
MENUS = ["mkdocs.association.yml", "mkdocs.departemental.yml", "mkdocs.test.yml"]

YML = """INHERIT: ./mkdocs.base.yml
site_name: Essai

nav:
  - Démarrer:
      - Bienvenue: index.md
  - Adhésions:
      - Gérer: gerer.md
      - Import:
          - Fichier: import.md
  - Statistiques: statistiques.md

extra:
  cle: valeur
"""


def ajoutees(avant: str, apres: str) -> list[str]:
    a = avant.split("\n")
    b = apres.split("\n")
    assert [l for l in b if l not in a or b.count(l) > a.count(l)] is not None
    restantes = list(b)
    for l in a:
        restantes.remove(l)          # chaque ligne d'origine est toujours là
    return restantes


def test_lire_les_rubriques():
    assert [(r.titre, r.sous_rubriques) for r in lire_menu(YML)] == [
        ("Démarrer", []), ("Adhésions", ["Import"])]


@pytest.mark.parametrize("fichier", MENUS)
def test_lire_les_vrais_menus(fichier):
    rubriques = [r.titre for r in lire_menu((RACINE / fichier).read_text())]
    assert "Démarrer" in rubriques and len(rubriques) >= 3


def test_ajouter_dans_une_rubrique_existante():
    apres = ajouter_au_menu(YML, "Démarrer", None, "Glossaire", "glossaire.md")
    assert ajoutees(YML, apres) == ["      - Glossaire: glossaire.md"]
    assert apres.index("Glossaire") < apres.index("  - Adhésions:")


def test_ajouter_dans_une_sous_rubrique_existante():
    apres = ajouter_au_menu(YML, "adhésions", "import", "Erreurs", "erreurs.md")   # sans tenir compte des majuscules
    assert ajoutees(YML, apres) == ["          - Erreurs: erreurs.md"]
    assert apres.index("Erreurs") < apres.index("Statistiques")


def test_creer_une_sous_rubrique():
    apres = ajouter_au_menu(YML, "Adhésions", "Lots", "Valider", "valider.md")
    assert ajoutees(YML, apres) == ["      - Lots:", "          - Valider: valider.md"]


def test_creer_une_rubrique_a_la_fin_du_menu():
    apres = ajouter_au_menu(YML, "Remboursements", "Cas particuliers", "Rembourser", "rembourser.md")
    assert ajoutees(YML, apres) == ["  - Remboursements:", "      - Cas particuliers:", "          - Rembourser: rembourser.md"]
    assert apres.index("Rembourser") < apres.index("extra:")       # avant la section suivante du fichier


def test_libelles_speciaux_entre_guillemets():
    apres = ajouter_au_menu(YML, "Démarrer", None, 'Statut : « à valider » #2', "statut.md")
    assert '      - "Statut : « à valider » #2": statut.md' in apres


def test_une_fiche_n_est_pas_une_rubrique():
    with pytest.raises(Invalide):
        ajouter_au_menu(YML, "Statistiques", None, "X", "x.md")
    with pytest.raises(Invalide):
        ajouter_au_menu(YML, "Adhésions", "Gérer", "X", "x.md")


def test_champs_obligatoires_et_menu_absent():
    with pytest.raises(Invalide):
        ajouter_au_menu(YML, " ", None, "X", "x.md")
    with pytest.raises(Invalide):
        ajouter_au_menu("site_name: x\n", "A", None, "X", "x.md")


@pytest.mark.parametrize("fichier", MENUS)
@pytest.mark.parametrize("rubrique, sous", [("Démarrer", None), ("Nouvelle rubrique", None), ("Démarrer", "Nouvelle sous-rubrique"),
                                            ("Nouvelle rubrique", "Sous : rubrique")])
def test_le_yaml_reste_valide_et_contient_la_fiche(fichier, rubrique, sous):
    yaml = pytest.importorskip("yaml")
    texte = (RACINE / fichier).read_text()
    nav = yaml.safe_load(ajouter_au_menu(texte, rubrique, sous, "Fiche ajoutée", "fiche-ajoutee.md"))["nav"]
    groupe = next(e[rubrique] for e in nav if isinstance(e, dict) and rubrique in e)
    if sous:
        groupe = next(e[sous] for e in groupe if isinstance(e, dict) and sous in e)
    assert {"Fiche ajoutée": "fiche-ajoutee.md"} in groupe
