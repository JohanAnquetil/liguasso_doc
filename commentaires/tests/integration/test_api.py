"""L'API HTTP de bout en bout : vrais SQLite et ALTCHA, faux dépôt de fiches."""
import altcha
import pytest
from fastapi.testclient import TestClient

from liguasso_contrib.composition import creer_app
from liguasso_contrib.config import Reglages
from tests.doublures import FichesEnMemoire

VISITEUR = {"X-Visiteur": "visiteur-de-test-0001"}
AUTRE = {"X-Visiteur": "visiteur-de-test-0002"}
PAGE = "departemental/lots"
FICHE = "# Lots\n\nUn lot regroupe des adhésions.\n"


@pytest.fixture
def fiches():
    return FichesEnMemoire({"docs-departemental/lots.md": FICHE,
                            "mkdocs.departemental.yml": "nav:\n  - Démarrer:\n      - Bienvenue: index.md\n"})


@pytest.fixture
def client(tmp_path, fiches):
    reglages = Reglages(donnees=tmp_path, admin_mot_de_passe="mdp-test", altcha_cout=10,
                        cors_origines=["http://localhost:8001"])
    return TestClient(creer_app(reglages, fiches=fiches))


def preuve(client):
    d = altcha.Challenge.from_dict(client.get("/api/commentaires/defi").json())
    return altcha.Payload(d, altcha.solve_challenge(d)).to_base64()


def commenter(client, entetes=VISITEUR, **champs):
    corps = {"page": PAGE, "pseudo": "Camille", "texte": "Bonjour", "altcha": preuve(client), **champs}
    return client.post("/api/commentaires", json=corps, headers=entetes)


def connecter(client):
    assert client.post("/api/commentaires/admin/connexion", json={"mot_de_passe": "mdp-test"}).status_code == 200


def test_parcours_d_un_commentaire(client):
    r = commenter(client)
    assert r.status_code == 201 and r.json()["en_attente"] is True
    cid = r.json()["id"]
    assert client.get("/api/commentaires", params={"page": PAGE}, headers=AUTRE).json() == []
    connecter(client)
    assert client.get("/api/commentaires/admin/liste").json()["compteurs"]["attente"] == 1
    assert client.post(f"/api/commentaires/admin/{cid}/publier").status_code == 200
    assert client.post(f"/api/commentaires/{cid}/like", headers=AUTRE).json() == {"aime": True, "likes": 1}
    r = client.post(f"/api/commentaires/{cid}/signaler", json={"motif": "spam", "altcha": preuve(client)}, headers=AUTRE)
    assert r.json() == {"deja_signale": False}
    assert client.post(f"/api/commentaires/admin/{cid}/repondre", json={"texte": "Merci"}).status_code == 200
    vu = client.get("/api/commentaires", params={"page": PAGE}, headers=AUTRE).json()
    assert [(c["pseudo"], c["likes"], c["aime"]) for c in vu] == [("Camille", 1, True), ("Équipe Ligu'asso", 0, False)]


@pytest.mark.parametrize("requete, code", [
    (lambda c: c.post("/api/commentaires", json={"page": PAGE, "pseudo": "B", "texte": "x"}, headers=VISITEUR), 400),
    (lambda c: c.post("/api/commentaires", json={"page": PAGE, "pseudo": "B", "texte": "x", "altcha": "x"}), 400),
    (lambda c: c.post("/api/commentaires", json={"page": PAGE, "pseudo": "", "texte": "x"}, headers=VISITEUR), 422),
    (lambda c: c.get("/api/commentaires", params={"page": "../secret"}), 400),
    (lambda c: c.post("/api/commentaires/999/like", headers=VISITEUR), 404),
    (lambda c: c.get("/api/commentaires/admin/liste"), 401),
    (lambda c: c.post("/api/commentaires/admin/1/publier"), 401),
    (lambda c: c.get("/api/commentaires/admin/propositions"), 401),
    (lambda c: c.post("/api/commentaires/admin/connexion", json={"mot_de_passe": "faux"}), 401),
])
def test_erreurs_traduites_en_codes_http(client, requete, code):
    r = requete(client)
    assert r.status_code == code and r.json()["detail"]


def test_preuve_anti_robot_non_rejouable(client):
    p = preuve(client)
    corps = {"page": PAGE, "pseudo": "B", "texte": "x", "altcha": p}
    assert client.post("/api/commentaires", json=corps, headers=VISITEUR).status_code == 201
    assert client.post("/api/commentaires", json=corps, headers=VISITEUR).status_code == 400


def test_cookie_de_session_protege(client):
    r = client.post("/api/commentaires/admin/connexion", json={"mot_de_passe": "mdp-test"})
    cookie = r.headers["set-cookie"].lower()
    assert "httponly" in cookie and "samesite=strict" in cookie and "path=/api/commentaires" in cookie
    client.post("/api/commentaires/admin/deconnexion")
    assert client.get("/api/commentaires/admin/liste").status_code == 401


def test_page_de_moderation(client):
    r = client.get("/api/commentaires/admin")
    assert r.status_code == 200 and "Modération" in r.text and r.headers["x-robots-tag"] == "noindex"


def test_cors_pour_la_redaction_locale(client):
    r = client.options("/api/commentaires", headers={"Origin": "http://localhost:8001",
                                                     "Access-Control-Request-Method": "POST",
                                                     "Access-Control-Request-Headers": "x-visiteur"})
    assert r.headers["access-control-allow-origin"] == "http://localhost:8001"
    r = client.options("/api/commentaires", headers={"Origin": "https://ailleurs.example",
                                                     "Access-Control-Request-Method": "POST"})
    assert "access-control-allow-origin" not in r.headers


def test_parcours_d_une_proposition(client, fiches):
    source = client.get("/api/commentaires/propositions/source", params={"page": PAGE}).json()
    assert source["texte"] == FICHE
    r = client.post("/api/commentaires/propositions", headers=VISITEUR, json={
        "type": "modification", "page": PAGE, "pseudo": "Sam", "resume": "Précision",
        "texte": FICHE.replace("adhésions.", "adhésions importées."), "blob_sha": source["blob_sha"],
        "commit_sha": source["commit_sha"], "altcha": preuve(client)})
    assert r.status_code == 201
    connecter(client)
    liste = client.get("/api/commentaires/admin/propositions").json()
    assert liste["github"] is True and len(liste["propositions"]) == 1
    r = client.post(f"/api/commentaires/admin/propositions/{r.json()['id']}/accepter")
    assert r.json() == {"pr_url": "https://github.com/exemple/pull/1"}
    assert "importées" in fiches.pull_requests[0]["texte"]


def test_sante(client):
    assert client.get("/sante").json() == {"ok": True}


def test_menu_et_nouvelle_fiche_placee(client, fiches):
    assert client.get("/api/commentaires/propositions/menu", params={"page": PAGE}).json() == [
        {"titre": "Démarrer", "sous_rubriques": []}]
    r = client.post("/api/commentaires/propositions", headers=VISITEUR, json={
        "type": "nouvelle", "page": PAGE, "titre": "Rembourser", "pseudo": "Sam", "resume": "Fiche manquante",
        "texte": "Étapes", "menu_rubrique": "Facturation", "menu_libelle": "Rembourser une adhésion", "altcha": preuve(client)})
    assert r.status_code == 201
    connecter(client)
    assert client.get("/api/commentaires/admin/propositions").json()["propositions"][0]["menu"] == "Facturation › Rembourser une adhésion"
    client.post(f"/api/commentaires/admin/propositions/{r.json()['id']}/accepter")
    assert [f.chemin for f in fiches.pull_requests[0]["fichiers"]] == ["docs-departemental/rembourser.md", "mkdocs.departemental.yml"]


def test_refuser_une_proposition(client):
    source = client.get("/api/commentaires/propositions/source", params={"page": PAGE}).json()
    r = client.post("/api/commentaires/propositions", headers=VISITEUR, json={
        "type": "modification", "page": PAGE, "pseudo": "Sam", "resume": "R", "texte": "# Autre\n",
        "blob_sha": source["blob_sha"], "commit_sha": source["commit_sha"], "altcha": preuve(client)})
    connecter(client)
    assert client.post(f"/api/commentaires/admin/propositions/{r.json()['id']}/refuser").json() == {"ok": True}
    assert client.get("/api/commentaires/admin/propositions", params={"filtre": "refusees"}).json()["propositions"]
