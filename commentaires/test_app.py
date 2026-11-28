"""Tests du service de commentaires :  pytest commentaires/"""
import importlib
import os

import altcha
import pytest
from fastapi.testclient import TestClient

VISITEUR = {"X-Visiteur": "visiteur-de-test-0001"}
AUTRE = {"X-Visiteur": "visiteur-de-test-0002"}


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("DONNEES", str(tmp_path))
    monkeypatch.setenv("ADMIN_MOT_DE_PASSE", "mot-de-passe-test")
    monkeypatch.setenv("ALTCHA_COUT", "10")   # défis rapides à résoudre dans les tests
    import app as module
    module = importlib.reload(module)
    return TestClient(module.app)


def solution(client):
    defi = altcha.Challenge.from_dict(client.get("/api/commentaires/defi").json())
    sol = altcha.solve_challenge(defi)
    return altcha.Payload(defi, sol).to_base64()


def commenter(client, texte="Bonjour", page="departemental/lots", entetes=VISITEUR, **extra):
    corps = {"page": page, "pseudo": "Camille", "texte": texte, "altcha": solution(client), **extra}
    return client.post("/api/commentaires", json=corps, headers=entetes)


def admin(client):
    r = client.post("/api/commentaires/admin/connexion", json={"mot_de_passe": "mot-de-passe-test"})
    assert r.status_code == 200


def publier(client, cid):
    admin(client)
    assert client.post(f"/api/commentaires/admin/{cid}/publier").status_code == 200


def test_commentaire_en_attente_visible_seulement_par_son_auteur(client):
    cid = commenter(client).json()["id"]
    a_moi = client.get("/api/commentaires", params={"page": "departemental/lots"}, headers=VISITEUR).json()
    aux_autres = client.get("/api/commentaires", params={"page": "departemental/lots"}, headers=AUTRE).json()
    assert [c["id"] for c in a_moi] == [cid] and a_moi[0]["en_attente"]
    assert aux_autres == []


def test_publication_par_admin(client):
    cid = commenter(client).json()["id"]
    publier(client, cid)
    liste = client.get("/api/commentaires", params={"page": "departemental/lots"}, headers=AUTRE).json()
    assert [c["id"] for c in liste] == [cid] and not liste[0]["en_attente"]


def test_antirobot_obligatoire_et_a_usage_unique(client):
    corps = {"page": "departemental/lots", "pseudo": "Bot", "texte": "Spam"}
    assert client.post("/api/commentaires", json=corps, headers=VISITEUR).status_code == 400
    corps["altcha"] = solution(client)
    assert client.post("/api/commentaires", json=corps, headers=VISITEUR).status_code == 201
    assert client.post("/api/commentaires", json=corps, headers=VISITEUR).status_code == 400  # rejeu


def test_champ_piege_ignore_silencieusement(client):
    r = commenter(client, site_web="http://spam.example")
    assert r.status_code == 201 and r.json()["id"] == 0
    admin(client)
    assert client.get("/api/commentaires/admin/liste").json()["commentaires"] == []


def test_limite_de_debit(client):
    for _ in range(5):
        assert commenter(client).status_code == 201
    assert commenter(client).status_code == 429


def test_like_bascule(client):
    cid = commenter(client).json()["id"]
    publier(client, cid)
    assert client.post(f"/api/commentaires/{cid}/like", headers=AUTRE).json() == {"aime": True, "likes": 1}
    assert client.post(f"/api/commentaires/{cid}/like", headers=AUTRE).json() == {"aime": False, "likes": 0}


def test_reponse_rattachee_au_premier_niveau(client):
    parent = commenter(client).json()["id"]
    publier(client, parent)
    reponse = commenter(client, "Réponse", parent_id=parent).json()["id"]
    publier(client, reponse)
    sous_reponse = commenter(client, "Réponse à la réponse", parent_id=reponse).json()["id"]
    publier(client, sous_reponse)
    liste = {c["id"]: c for c in client.get("/api/commentaires", params={"page": "departemental/lots"}).json()}
    assert liste[reponse]["parent_id"] == parent and liste[sous_reponse]["parent_id"] == parent


def test_signalements_masquent_apres_trois_personnes(client, monkeypatch):
    cid = commenter(client).json()["id"]
    publier(client, cid)
    import app as module
    for i in range(3):
        monkeypatch.setattr(module, "ip_client", lambda request, i=i: f"ip-{i}")
        r = client.post(f"/api/commentaires/{cid}/signaler", json={"motif": "spam", "altcha": solution(client)},
                        headers={"X-Visiteur": f"signaleur-numero-{i:04d}"})
        assert r.status_code == 200
    assert client.get("/api/commentaires", params={"page": "departemental/lots"}).json() == []
    signales = client.get("/api/commentaires/admin/liste", params={"filtre": "signales"}).json()["commentaires"]
    assert signales[0]["statut"] == "masque" and len(signales[0]["signalements"]) == 3


def test_reponse_equipe_publie_aussi_le_commentaire(client):
    cid = commenter(client).json()["id"]
    admin(client)
    assert client.post(f"/api/commentaires/admin/{cid}/repondre", json={"texte": "Merci !"}).status_code == 200
    liste = client.get("/api/commentaires", params={"page": "departemental/lots"}).json()
    assert [(c["pseudo"], c["equipe"]) for c in liste] == [("Camille", False), ("Équipe Ligu'asso", True)]


def test_admin_protege(client):
    assert client.get("/api/commentaires/admin/liste").status_code == 401
    assert client.post("/api/commentaires/admin/connexion", json={"mot_de_passe": "faux"}).status_code == 401


def test_page_invalide_refusee(client):
    assert commenter(client, page="../etc/passwd").status_code == 400
