"""Cas limites et messages d'erreur des cas d'usage et des règles."""
import pytest

from liguasso_contrib.application.commentaires import GestionCommentaires
from liguasso_contrib.application.propositions import GestionPropositions, NouvelleProposition
from liguasso_contrib.domaine import modeles as m
from liguasso_contrib.domaine.erreurs import Introuvable, Invalide
from liguasso_contrib.domaine.menu import ajouter_au_menu, lire_menu
from tests.doublures import (AntiRobotFactice, DepotCommentairesMemoire, DepotPropositionsMemoire, FichesEnMemoire,
                             HorlogeFixe, LimiteurMemoire)


@pytest.fixture
def commentaires():
    return GestionCommentaires(DepotCommentairesMemoire(), LimiteurMemoire(), AntiRobotFactice(), HorlogeFixe(), m.Regles())


@pytest.fixture
def propositions():
    fiches = FichesEnMemoire({"docs-departemental/lots.md": "# Lots\n", "mkdocs.departemental.yml": "nav:\n  - A:\n      - B: b.md\n"})
    return GestionPropositions(DepotPropositionsMemoire(), fiches, LimiteurMemoire(), AntiRobotFactice(), HorlogeFixe(),
                               m.Regles(), "https://exemple.org")


def nouvelle(**champs):
    valeurs = dict(type=m.NOUVELLE, page="departemental/lots", pseudo="Sam", resume="R", texte="T", titre="Titre", preuve="ok")
    valeurs.update(champs)
    return NouvelleProposition(**valeurs)


class TestCommentaires:
    def test_repondre_a_un_commentaire_inexistant(self, commentaires):
        with pytest.raises(Introuvable):
            commentaires.repondre_au_nom_de_l_equipe(42, "Merci")

    def test_reponse_vide(self, commentaires):
        from liguasso_contrib.application.commentaires import NouveauCommentaire
        cid = commentaires.commenter(NouveauCommentaire(page="g/p", pseudo="A", texte="x", preuve="ok"), "v", "ip")
        with pytest.raises(Invalide):
            commentaires.repondre_au_nom_de_l_equipe(cid, "   ")

    def test_filtre_admin_inconnu(self, commentaires):
        with pytest.raises(Invalide):
            commentaires.pour_admin("tout")


class TestPropositions:
    @pytest.mark.parametrize("champs, message", [
        ({"type": "suppression"}, "invalide"),
        ({"pseudo": "  "}, "obligatoires"),
        ({"texte": "x" * 100_001}, "trop long"),
        ({"page": "inconnu/x"}, "Guide inconnu"),
        ({"titre": " "}, "titre"),
    ])
    def test_propositions_refusees(self, propositions, champs, message):
        with pytest.raises(Invalide, match=message):
            propositions.proposer(nouvelle(**champs), "v", "ip")

    def test_champ_piege(self, propositions):
        assert propositions.proposer(nouvelle(piege="robot"), "v", "ip") == 0

    def test_menu_d_un_guide_inconnu(self, propositions):
        with pytest.raises(Invalide):
            propositions.menu("inconnu/page")

    def test_filtre_admin_inconnu(self, propositions):
        with pytest.raises(Invalide):
            propositions.pour_admin("toutes")

    def test_menu_avec_libelle_sur_plusieurs_lignes(self, propositions, monkeypatch):
        import liguasso_contrib.application.propositions as module
        monkeypatch.setattr(module, "nettoyer", lambda t, n: t)        # le nettoyage laisse passer un saut de ligne
        with pytest.raises(Invalide, match="une ligne"):
            propositions.proposer(nouvelle(menu_rubrique="A", menu_libelle="Deux\nlignes"), "v", "ip")


class TestMenu:
    def test_libelles_entre_guillemets_relus(self):
        yml = 'nav:\n  - "Rubrique : spéciale":\n      - \'Sous\':\n          - F: f.md\n'
        assert [(r.titre, r.sous_rubriques) for r in lire_menu(yml)] == [("Rubrique : spéciale", ["Sous"])]
        apres = ajouter_au_menu(yml, "Rubrique : spéciale", "Sous", "G", "g.md")
        assert apres.endswith("          - F: f.md\n          - G: g.md\n")

    def test_menu_vide(self):
        assert lire_menu("nav:\n") == []
        assert ajouter_au_menu("nav:\n", "A", None, "F", "f.md") == "nav:\n  - A:\n      - F: f.md\n"

    def test_lignes_vides_dans_une_rubrique(self):
        yml = "nav:\n  - A:\n      - F: f.md\n\n  - B:\n      - G: g.md\n"
        assert "      - F: f.md\n      - H: h.md\n\n  - B:" in ajouter_au_menu(yml, "A", None, "H", "h.md")
