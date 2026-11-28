"""Connexion à la modération."""
import pytest

from liguasso_contrib.application.administration import Administration
from liguasso_contrib.domaine.erreurs import Indisponible, NonAutorise, TropDeDemandes
from liguasso_contrib.domaine.modeles import Regles
from tests.doublures import LimiteurMemoire, SessionsFactices


@pytest.fixture
def admin():
    return Administration("bon-mot-de-passe", SessionsFactices(), LimiteurMemoire(), Regles())


def test_bon_mot_de_passe(admin):
    jeton = admin.connecter("bon-mot-de-passe", "ip")
    admin.verifier(jeton)


def test_mauvais_mot_de_passe(admin):
    with pytest.raises(NonAutorise):
        admin.connecter("faux", "ip")


def test_jeton_invalide(admin):
    for jeton in ("", "jeton-forge"):
        with pytest.raises(NonAutorise):
            admin.verifier(jeton)


def test_tentatives_limitees(admin):
    for _ in range(5):
        with pytest.raises(NonAutorise):
            admin.connecter("faux", "ip")
    with pytest.raises(TropDeDemandes):
        admin.connecter("bon-mot-de-passe", "ip")


def test_desactivee_sans_mot_de_passe():
    with pytest.raises(Indisponible):
        Administration("", SessionsFactices(), LimiteurMemoire(), Regles()).connecter("x", "ip")
