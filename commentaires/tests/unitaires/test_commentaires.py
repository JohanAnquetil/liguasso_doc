"""Cas d'usage des commentaires, avec des doublures en mémoire."""
import pytest

from liguasso_contrib.application.commentaires import GestionCommentaires, NouveauCommentaire
from liguasso_contrib.domaine import modeles as m
from liguasso_contrib.domaine.erreurs import Introuvable, Invalide, TropDeDemandes
from tests.doublures import AntiRobotFactice, DepotCommentairesMemoire, HorlogeFixe, LimiteurMemoire

PAGE = "departemental/adhesions-lots"
CAMILLE, DOMINIQUE = "visiteur-camille", "visiteur-dominique"


@pytest.fixture
def depot():
    return DepotCommentairesMemoire()


@pytest.fixture
def anti_robot():
    return AntiRobotFactice()


@pytest.fixture
def service(depot, anti_robot):
    return GestionCommentaires(depot, LimiteurMemoire(), anti_robot, HorlogeFixe(), m.Regles())


def commenter(service, texte="Bonjour", visiteur=CAMILLE, ip="ip-1", **champs):
    return service.commenter(NouveauCommentaire(page=PAGE, pseudo="Camille", texte=texte, preuve="ok", **champs),
                             visiteur, ip)


def publie(service, **champs):
    cid = commenter(service, **champs)
    service.moderer(cid, "publier")
    return cid


class TestPublication:
    def test_un_commentaire_attend_la_validation(self, service):
        cid = commenter(service)
        assert [c["id"] for c in service.lister(PAGE, CAMILLE)] == [cid]
        assert service.lister(PAGE, CAMILLE)[0]["en_attente"] is True
        assert service.lister(PAGE, DOMINIQUE) == []
        assert service.lister(PAGE, None) == []

    def test_visible_par_tous_une_fois_publie(self, service):
        cid = publie(service)
        vu = service.lister(PAGE, DOMINIQUE)
        assert [(c["id"], c["en_attente"], c["de_moi"]) for c in vu] == [(cid, False, False)]
        assert service.lister(PAGE, CAMILLE)[0]["de_moi"] is True

    def test_refuse_n_est_plus_visible(self, service):
        cid = commenter(service)
        service.moderer(cid, "refuser")
        assert service.lister(PAGE, CAMILLE) == []

    def test_texte_et_pseudo_nettoyes(self, service, depot):
        cid = service.commenter(NouveauCommentaire(page=PAGE, pseudo="  Cam\x07ille ", texte="a\n\n\n\nb", preuve="ok"),
                                CAMILLE, "ip")
        assert (depot.trouver(cid).pseudo, depot.trouver(cid).texte) == ("Camille", "a\n\nb")

    def test_pseudo_vide_refuse(self, service):
        with pytest.raises(Invalide):
            service.commenter(NouveauCommentaire(page=PAGE, pseudo="  ", texte="x", preuve="ok"), CAMILLE, "ip")


class TestAntiRobot:
    def test_preuve_obligatoire(self, service):
        with pytest.raises(Invalide):
            service.commenter(NouveauCommentaire(page=PAGE, pseudo="Bot", texte="Spam"), CAMILLE, "ip")

    def test_preuve_a_usage_unique(self, service):
        demande = NouveauCommentaire(page=PAGE, pseudo="Camille", texte="x", preuve="ok-42")
        service.commenter(demande, CAMILLE, "ip")
        with pytest.raises(Invalide):
            service.commenter(demande, CAMILLE, "ip")

    def test_champ_piege_ignore_sans_rien_enregistrer(self, service, depot):
        assert commenter(service, piege="http://spam.example") == 0
        assert depot.commentaires == {}

    def test_limite_de_debit_par_adresse_ip(self, service):
        for _ in range(5):
            commenter(service, ip="ip-bavarde")
        with pytest.raises(TropDeDemandes):
            commenter(service, ip="ip-bavarde")
        commenter(service, ip="autre-ip")      # les autres ne sont pas pénalisés


class TestReponses:
    def test_une_reponse_se_rattache_au_premier_niveau(self, service):
        parent = publie(service)
        reponse = publie(service, parent_id=parent)
        sous_reponse = publie(service, parent_id=reponse)
        parents = {c["id"]: c["parent_id"] for c in service.lister(PAGE, None)}
        assert parents == {parent: None, reponse: parent, sous_reponse: parent}

    def test_on_ne_repond_pas_a_un_commentaire_en_attente(self, service):
        parent = commenter(service)
        with pytest.raises(Invalide):
            commenter(service, parent_id=parent)

    def test_reponse_masquee_si_le_parent_ne_l_est_plus(self, service):
        parent = publie(service)
        publie(service, parent_id=parent)
        service.moderer(parent, "refuser")
        assert service.lister(PAGE, None) == []


class TestLikes:
    def test_un_like_se_bascule(self, service):
        cid = publie(service)
        assert service.liker(cid, DOMINIQUE, "ip") == {"aime": True, "likes": 1}
        assert service.lister(PAGE, DOMINIQUE)[0]["aime"] is True
        assert service.liker(cid, DOMINIQUE, "ip") == {"aime": False, "likes": 0}

    def test_on_ne_like_pas_un_commentaire_en_attente(self, service):
        cid = commenter(service)
        with pytest.raises(Introuvable):
            service.liker(cid, DOMINIQUE, "ip")


class TestSignalements:
    def signaler(self, service, cid, n):
        return service.signaler(cid, "spam", "", f"ok-{n}", f"visiteur-{n}", f"ip-{n}")

    def test_masque_apres_trois_personnes_differentes(self, service):
        cid = publie(service)
        for n in range(2):
            self.signaler(service, cid, n)
        assert len(service.lister(PAGE, None)) == 1
        self.signaler(service, cid, 2)
        assert service.lister(PAGE, None) == []
        signale = service.pour_admin("signales")["commentaires"][0]
        assert signale["statut"] == m.MASQUE and len(signale["signalements"]) == 3

    def test_meme_adresse_ip_compte_une_fois(self, service):
        cid = publie(service)
        for n in range(3):
            service.signaler(cid, "spam", "", f"ok-{n}", f"visiteur-{n}", "meme-ip")
        assert len(service.lister(PAGE, None)) == 1

    def test_un_visiteur_ne_signale_qu_une_fois(self, service):
        cid = publie(service)
        assert service.signaler(cid, "spam", "", "ok-1", DOMINIQUE, "ip") == {"deja_signale": False}
        assert service.signaler(cid, "spam", "", "ok-2", DOMINIQUE, "ip") == {"deja_signale": True}

    def test_motif_inconnu(self, service):
        with pytest.raises(Invalide):
            service.signaler(publie(service), "pas-un-motif", "", "ok", DOMINIQUE, "ip")

    def test_retablir_efface_les_signalements(self, service):
        cid = publie(service)
        for n in range(3):
            self.signaler(service, cid, n)
        service.moderer(cid, "publier")
        assert len(service.lister(PAGE, None)) == 1
        assert service.pour_admin("signales")["commentaires"] == []


class TestModeration:
    def test_reponse_de_l_equipe_publie_aussi_le_commentaire(self, service):
        cid = commenter(service)
        service.repondre_au_nom_de_l_equipe(cid, "Merci !")
        assert [(c["pseudo"], c["equipe"], c["parent_id"]) for c in service.lister(PAGE, None)] == [
            ("Camille", False, None), (m.NOM_EQUIPE, True, cid)]

    def test_supprimer_retire_aussi_les_reponses(self, service, depot):
        parent = publie(service)
        publie(service, parent_id=parent)
        service.moderer(parent, "supprimer")
        assert depot.commentaires == {}

    def test_action_inconnue(self, service):
        with pytest.raises(Invalide):
            service.moderer(commenter(service), "effacer")

    def test_commentaire_introuvable(self, service):
        with pytest.raises(Introuvable):
            service.moderer(999, "publier")

    def test_compteurs(self, service):
        commenter(service)
        publie(service)
        assert service.pour_admin("attente")["compteurs"] == {"attente": 1, "signales": 0, "publies": 1, "refuses": 0}
