"""Adaptateurs : cas d'erreur et réglages."""
import pytest

from liguasso_contrib.config import Reglages
from liguasso_contrib.domaine.erreurs import ServiceExterne
from liguasso_contrib.infrastructure.github import FichesGitHub
from liguasso_contrib.infrastructure.securite import SessionsSignees, charger_secret


def test_github_injoignable():
    fiches = FichesGitHub("o/d", api="http://127.0.0.1:9")     # port fermé
    with pytest.raises(ServiceExterne, match="ne répond pas"):
        fiches.version_actuelle()


def test_cache_github_vide_au_dela_de_500_fichiers(monkeypatch):
    fiches = FichesGitHub("o/d")
    fiches._cache = {(f"f{i}.md", "v"): ("t", "s") for i in range(501)}
    monkeypatch.setattr(fiches, "_appel", lambda *a, **k: {"content": "VA==", "sha": "x"})
    assert fiches.lire("nouveau.md", "v") == ("T", "x")
    assert len(fiches._cache) == 1
    assert fiches.existe("nouveau.md", "v")


def test_secret_fourni_ou_cree_une_fois(tmp_path):
    assert charger_secret("fourni", tmp_path) == "fourni"
    cree = charger_secret("", tmp_path)
    assert charger_secret("", tmp_path) == cree and len(cree) == 64
    assert oct((tmp_path / "secret").stat().st_mode)[-3:] == "600"


def test_session_expiree_ou_falsifiee():
    sessions = SessionsSignees("secret", duree=-1)
    assert not sessions.valide(sessions.creer())                    # expirée aussitôt
    assert not SessionsSignees("secret").valide("jeton-falsifie")
    assert not SessionsSignees("autre").valide(SessionsSignees("secret").creer())


def test_reglages_depuis_l_environnement(monkeypatch, tmp_path):
    for cle, valeur in {"DONNEES": str(tmp_path), "ADMIN_MOT_DE_PASSE": "mdp", "CORS_ORIGINES": "http://a, http://b",
                        "ALTCHA_COUT": "42", "GITHUB_TOKEN": "jeton", "LIMITES_RELACHEES": "1"}.items():
        monkeypatch.setenv(cle, valeur)
    r = Reglages.depuis_environnement()
    assert (r.donnees, r.admin_mot_de_passe, r.cors_origines, r.altcha_cout, r.github_jeton, r.limites_relachees) == (
        tmp_path, "mdp", ["http://a", "http://b"], 42, "jeton", True)
