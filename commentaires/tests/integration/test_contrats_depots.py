"""Tests de contrat : l'adaptateur SQLite et la doublure en mémoire se comportent pareil.

Chaque test tourne deux fois. Si la doublure s'écarte du vrai stockage, les tests
unitaires (qui l'utilisent) ne peuvent plus mentir.
"""
import pytest

from liguasso_contrib.domaine import modeles as m
from liguasso_contrib.domaine.erreurs import TropDeDemandes
from liguasso_contrib.infrastructure.sqlite import (Base, DepotCommentairesSQLite, DepotPropositionsSQLite,
                                                    LimiteurSQLite)
from tests.doublures import DepotCommentairesMemoire, DepotPropositionsMemoire, LimiteurMemoire


@pytest.fixture(params=["sqlite", "memoire"])
def commentaires(request, tmp_path):
    return DepotCommentairesSQLite(Base(tmp_path / "c.sqlite3")) if request.param == "sqlite" else DepotCommentairesMemoire()


@pytest.fixture(params=["sqlite", "memoire"])
def propositions(request, tmp_path):
    return DepotPropositionsSQLite(Base(tmp_path / "p.sqlite3")) if request.param == "sqlite" else DepotPropositionsMemoire()


def nouveau(statut=m.PUBLIE, page="g/p", visiteur="v1", parent_id=None, quand="2026-01-01T00:00:01"):
    return m.Commentaire(id=0, page=page, pseudo="P", texte="T", statut=statut, cree_le=quand,
                         visiteur=visiteur, parent_id=parent_id)


def test_visibles(commentaires):
    publie = commentaires.ajouter(nouveau(), "ip")
    a_moi = commentaires.ajouter(nouveau(m.ATTENTE, visiteur="moi", quand="2026-01-01T00:00:02"), "ip")
    commentaires.ajouter(nouveau(m.ATTENTE, visiteur="autre"), "ip")
    commentaires.ajouter(nouveau(m.REFUSE), "ip")
    commentaires.ajouter(nouveau(page="g/autre-page"), "ip")
    assert [c.id for c in commentaires.visibles("g/p", "moi")] == [publie, a_moi]
    assert [c.id for c in commentaires.visibles("g/p", None)] == [publie]


def test_likes(commentaires):
    cid = commentaires.ajouter(nouveau(), "ip")
    assert commentaires.basculer_like(cid, "a") == (True, 1)
    assert commentaires.basculer_like(cid, "b") == (True, 2)
    assert commentaires.aimes_par("a", [cid]) == {cid}
    assert commentaires.visibles("g/p", None)[0].likes == 2
    assert commentaires.basculer_like(cid, "a") == (False, 1)


def test_signalements(commentaires):
    cid = commentaires.ajouter(nouveau(), "ip")
    assert commentaires.ajouter_signalement(cid, "a", "ip-1", "spam", "", "t")
    assert not commentaires.ajouter_signalement(cid, "a", "ip-1", "spam", "", "t")
    commentaires.ajouter_signalement(cid, "b", "ip-1", "faux", "précision", "t")
    commentaires.ajouter_signalement(cid, "c", "ip-2", "spam", "", "t")
    assert commentaires.nombre_signaleurs(cid) == 2
    (_, _, signalements), = commentaires.pour_admin("signales")
    assert {s.motif for s in signalements} == {"spam", "faux"} and len(signalements) == 3
    commentaires.changer_statut(cid, m.PUBLIE, "t", signalements_traites=True)
    assert commentaires.nombre_signaleurs(cid) == 0 and commentaires.pour_admin("signales") == []


def test_moderation_et_compteurs(commentaires):
    attente = commentaires.ajouter(nouveau(m.ATTENTE), "ip")
    publie = commentaires.ajouter(nouveau(), "ip")
    reponse = commentaires.ajouter(nouveau(parent_id=publie), "ip")
    assert commentaires.compteurs() == {"attente": 1, "signales": 0, "publies": 2, "refuses": 0}
    commentaires.publier_si_attente(attente, "t")
    assert commentaires.trouver(attente).statut == m.PUBLIE
    (c, parent, _), = [x for x in commentaires.pour_admin("publies") if x[0].id == reponse]
    assert parent.id == publie
    commentaires.supprimer(publie)
    assert commentaires.trouver(publie) is None and commentaires.trouver(reponse) is None


def test_propositions(propositions):
    p = m.Proposition(id=0, type=m.MODIFICATION, page="g/p", chemin="docs/p.md", pseudo="S", resume="R",
                      texte_avant="a", texte="b", statut=m.P_ATTENTE, cree_le="t", blob_sha="b" * 40,
                      commit_sha="c" * 40)
    pid = propositions.ajouter(p, "v", "ip")
    assert propositions.trouver(pid).texte == "b"
    assert [x.id for x in propositions.lister(m.P_ATTENTE)] == [pid]
    propositions.accepter(pid, "https://pr", "t")
    assert (propositions.trouver(pid).statut, propositions.trouver(pid).pr_url) == (m.P_ACCEPTEE, "https://pr")
    assert not propositions.refuser(pid, "t")
    autre = propositions.ajouter(p, "v", "ip")
    assert propositions.refuser(autre, "t") and propositions.lister(m.P_REFUSEE)[0].id == autre


@pytest.mark.parametrize("limiteur", ["sqlite", "memoire"])
def test_limiteur(limiteur, tmp_path):
    l = LimiteurSQLite(Base(tmp_path / "l.sqlite3")) if limiteur == "sqlite" else LimiteurMemoire()
    for _ in range(2):
        l.consommer("cle", 2, 60)
    with pytest.raises(TropDeDemandes):
        l.consommer("cle", 2, 60)
    l.consommer("autre-cle", 2, 60)


def test_limiteur_sqlite_oublie_apres_la_fenetre(tmp_path):
    t = [1000.0]
    l = LimiteurSQLite(Base(tmp_path / "l.sqlite3"), horloge=lambda: t[0])
    l.consommer("cle", 1, 60)
    with pytest.raises(TropDeDemandes):
        l.consommer("cle", 1, 60)
    t[0] += 61
    l.consommer("cle", 1, 60)


def test_base_existante_reutilisee(tmp_path):
    """Le schéma est compatible avec la base de la première version (déjà en production)."""
    fichier = tmp_path / "commentaires.sqlite3"
    cid = DepotCommentairesSQLite(Base(fichier)).ajouter(nouveau(), "ip")
    assert DepotCommentairesSQLite(Base(fichier)).trouver(cid).texte == "T"
