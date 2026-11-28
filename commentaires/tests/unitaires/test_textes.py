"""Règles pures du domaine."""
import pytest

from liguasso_contrib.domaine.erreurs import Invalide
from liguasso_contrib.domaine.textes import (differences, fichier_de_page, nettoyer, nom_de_fiche,
                                             normaliser_fiche, verifier_page)

DOSSIERS = {"association": "docs-association", "departemental": "docs-departemental"}


@pytest.mark.parametrize("brut, attendu", [
    ("  Bonjour  ", "Bonjour"),
    ("a\r\nb", "a\nb"),
    ("a\n\n\n\n\nb", "a\n\nb"),
    ("bip\x07bip\x00", "bipbip"),               # caractères de contrôle retirés
    ("été", "été"),                  # forme normalisée (NFC)
])
def test_nettoyer(brut, attendu):
    assert nettoyer(brut, 100) == attendu


def test_nettoyer_tronque():
    assert nettoyer("x" * 50, 10) == "x" * 10


@pytest.mark.parametrize("page", ["departemental", "departemental/adhesions-lots", "test/a_b-c"])
def test_pages_valides(page):
    assert verifier_page(page) == page


@pytest.mark.parametrize("page", ["", "../etc/passwd", "/racine", "Majuscules", "a" * 201, "espace ici"])
def test_pages_invalides(page):
    with pytest.raises(Invalide):
        verifier_page(page)


@pytest.mark.parametrize("page, fichier", [
    ("departemental/adhesions-lots", "docs-departemental/adhesions-lots.md"),
    ("association", "docs-association/index.md"),
])
def test_fichier_de_page(page, fichier):
    assert fichier_de_page(page, DOSSIERS) == fichier


@pytest.mark.parametrize("page", ["autre/fiche", "departemental/../secret"])
def test_fichier_de_page_hors_guide(page):
    with pytest.raises(Invalide):
        fichier_de_page(page, DOSSIERS)


@pytest.mark.parametrize("titre, nom", [
    ("Gérer les remboursements", "gerer-les-remboursements"),
    ("  Ré-affiliation : étape n°2 ! ", "re-affiliation-etape-n2"),
    ("!!!", "nouvelle-fiche"),
])
def test_nom_de_fiche(titre, nom):
    assert nom_de_fiche(titre) == nom


def test_normaliser_fiche_finit_par_une_ligne():
    assert normaliser_fiche("\n# Titre\r\n\r\nTexte  \n\n") == "# Titre\n\nTexte\n"


def test_differences_avec_contexte():
    avant = "a\nb\nc\nd\ne\nf\n"
    apres = "a\nb\nc\nD\ne\nf\n"
    lignes = differences(avant, apres)
    assert lignes[0] == {"type": "@", "texte": "…"}
    assert [(l["type"], l["texte"]) for l in lignes[1:]] == [
        (" ", "b"), (" ", "c"), ("-", "d"), ("+", "D"), (" ", "e"), (" ", "f")]


def test_aucune_difference():
    assert differences("a\n", "a\n") == []
