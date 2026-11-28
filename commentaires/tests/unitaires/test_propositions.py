"""Cas d'usage des propositions de fiches, avec un dépôt de fiches en mémoire."""
import pytest

from liguasso_contrib.application.propositions import GestionPropositions, NouvelleProposition
from liguasso_contrib.domaine import modeles as m
from liguasso_contrib.domaine.erreurs import Conflit, Indisponible, Introuvable, Invalide, TropDeDemandes
from tests.doublures import (V1, AntiRobotFactice, DepotPropositionsMemoire, FichesEnMemoire, HorlogeFixe,
                             LimiteurMemoire)

PAGE = "departemental/lots"
CHEMIN = "docs-departemental/lots.md"
FICHE = "# Lots\n\nUn lot regroupe des adhésions.\n"


@pytest.fixture
def fiches():
    return FichesEnMemoire({CHEMIN: FICHE})


@pytest.fixture
def depot():
    return DepotPropositionsMemoire()


@pytest.fixture
def service(depot, fiches):
    return GestionPropositions(depot, fiches, LimiteurMemoire(), AntiRobotFactice(), HorlogeFixe(),
                               m.Regles(), "https://guide.exemple.org/")


def modification(service, texte=FICHE.replace("adhésions.", "adhésions importées."), ip="ip", **champs):
    source = service.source(PAGE)
    valeurs = dict(type=m.MODIFICATION, page=PAGE, pseudo="Sam", resume="Précision", texte=texte,
                   blob_sha=source["blob_sha"], commit_sha=source["commit_sha"], preuve="ok")
    valeurs.update(champs)
    return service.proposer(NouvelleProposition(**valeurs), "visiteur", ip)


def nouvelle(service, titre="Gérer les remboursements", texte="Étapes à suivre…"):
    return service.proposer(NouvelleProposition(type=m.NOUVELLE, page=PAGE, pseudo="Sam", resume="Fiche manquante",
                                                texte=texte, titre=titre, preuve="ok"), "visiteur", "ip")


class TestSource:
    def test_texte_et_versions_de_la_fiche(self, service, fiches):
        assert service.source(PAGE) == {"texte": FICHE, "blob_sha": fiches.sha(FICHE), "commit_sha": V1}

    def test_fiche_absente(self, service):
        with pytest.raises(Introuvable):
            service.source("departemental/inexistante")


class TestProposerUneModification:
    def test_enregistree_en_attente_avec_le_texte_de_depart(self, service, depot):
        p = depot.trouver(modification(service))
        assert (p.statut, p.chemin, p.texte_avant, p.commit_sha) == (m.P_ATTENTE, CHEMIN, FICHE, V1)

    def test_rien_de_modifie(self, service):
        with pytest.raises(Invalide):
            modification(service, texte=FICHE + "\n\n")

    def test_version_manquante(self, service):
        with pytest.raises(Invalide):
            modification(service, blob_sha="")

    def test_la_fiche_a_change_entre_temps(self, service, fiches):
        source = service.source(PAGE)
        fiches.modifier(CHEMIN, FICHE + "Ajout de quelqu'un d'autre.\n")
        with pytest.raises(Conflit):
            service.proposer(NouvelleProposition(type=m.MODIFICATION, page=PAGE, pseudo="Sam", resume="R",
                                                 texte="# Lots\n\nAutre\n", blob_sha="0" * 40,
                                                 commit_sha=source["commit_sha"], preuve="ok"), "v", "ip")

    def test_partir_d_une_ancienne_version_reste_possible(self, service, fiches, depot):
        """La PR partira de cette version : c'est GitHub qui signalera un éventuel conflit."""
        source = service.source(PAGE)
        fiches.modifier(CHEMIN, FICHE + "Ajout de quelqu'un d'autre.\n")
        pid = service.proposer(NouvelleProposition(type=m.MODIFICATION, page=PAGE, pseudo="Sam", resume="R",
                                                   texte="# Lots\n\nAutre\n", blob_sha=source["blob_sha"],
                                                   commit_sha=source["commit_sha"], preuve="ok"), "v", "ip")
        assert depot.trouver(pid).commit_sha == V1

    def test_anti_robot_et_limite(self, service):
        with pytest.raises(Invalide):
            modification(service, preuve="")
        for _ in range(3):
            modification(service, ip="ip-pressee")
        with pytest.raises(TropDeDemandes):
            modification(service, ip="ip-pressee")

    def test_champ_piege(self, service, depot):
        assert modification(service, piege="robot") == 0
        assert depot.propositions == {}


class TestProposerUneNouvelleFiche:
    def test_chemin_tire_du_titre_et_titre_ajoute(self, service, depot):
        p = depot.trouver(nouvelle(service))
        assert p.chemin == "docs-departemental/gerer-les-remboursements.md"
        assert p.texte.startswith("# Gérer les remboursements\n\nÉtapes")
        assert (p.texte_avant, p.blob_sha, p.commit_sha) == ("", None, None)

    def test_titre_obligatoire(self, service):
        with pytest.raises(Invalide):
            nouvelle(service, titre="  ")


class TestModeration:
    def test_accepter_cree_une_pull_request(self, service, fiches, depot):
        pid = modification(service)
        url = service.accepter(pid)
        pr = fiches.pull_requests[0]
        assert url == "https://github.com/exemple/pull/1"
        assert (pr["depart"], pr["chemin"], pr["blob_sha"]) == (V1, CHEMIN, fiches.sha(FICHE))
        assert pr["branche"] == f"proposition-{pid}-lots" and "importées" in pr["texte"]
        assert "https://guide.exemple.org/departemental/lots/" in pr["corps"]
        assert (depot.trouver(pid).statut, depot.trouver(pid).pr_url) == (m.P_ACCEPTEE, url)

    def test_nouvelle_fiche_part_de_la_version_actuelle(self, service, fiches):
        pid = nouvelle(service)
        fiches.modifier("docs-departemental/autre.md", "x")
        service.accepter(pid)
        pr = fiches.pull_requests[0]
        assert (pr["depart"], pr["blob_sha"]) == (fiches.actuelle, None)
        assert "ajouter au menu" in pr["corps"]

    def test_nouvelle_fiche_deja_existante(self, service, fiches):
        pid = nouvelle(service, titre="Lots")
        with pytest.raises(Conflit):
            service.accepter(pid)

    def test_sans_jeton_github(self, depot):
        service = GestionPropositions(depot, FichesEnMemoire({CHEMIN: FICHE}, ecriture_possible=False),
                                      LimiteurMemoire(), AntiRobotFactice(), HorlogeFixe(), m.Regles(), "x")
        with pytest.raises(Indisponible):
            service.accepter(modification(service))

    def test_une_proposition_ne_se_traite_qu_une_fois(self, service):
        pid = modification(service)
        service.refuser(pid)
        with pytest.raises(Introuvable):
            service.accepter(pid)
        with pytest.raises(Introuvable):
            service.refuser(pid)

    def test_differences_pour_l_admin(self, service):
        modification(service)
        p = service.pour_admin("attente")["propositions"][0]
        assert [(l["type"], l["texte"]) for l in p["differences"] if l["type"] in "+-"] == [
            ("-", "Un lot regroupe des adhésions."), ("+", "Un lot regroupe des adhésions importées.")]
