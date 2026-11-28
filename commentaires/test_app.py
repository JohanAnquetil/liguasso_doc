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


# --- Propositions de modification ---------------------------------------------------------

import base64

COMMIT = "a" * 40
BLOB = "b" * 40
FICHE = "# Lots\n\nUn lot regroupe des adhésions.\n"


class FauxGitHub:
    """Remplace l'API GitHub : garde les appels, renvoie des réponses plausibles."""
    def __init__(self):
        self.appels = []

    def __call__(self, methode, chemin, corps=None):
        self.appels.append((methode, chemin, corps))
        if chemin.startswith("/git/ref/heads/"):
            return {"object": {"sha": COMMIT}}
        if methode == "GET" and chemin.startswith("/contents/docs-departemental/lots.md"):
            return {"sha": BLOB, "content": base64.b64encode(FICHE.encode()).decode()}
        if methode == "GET" and chemin.startswith("/contents/"):
            raise FileNotFoundError(chemin)
        if chemin == "/pulls":
            return {"html_url": "https://github.com/exemple/pull/42"}
        return {}


@pytest.fixture()
def gh(client, monkeypatch):
    import app as module
    faux = FauxGitHub()
    monkeypatch.setattr(module, "github", faux)
    monkeypatch.setattr(module, "GITHUB_TOKEN", "jeton-de-test")
    module._cache_sources.clear()
    return faux


def proposer(client, **champs):
    corps = {"type": "modification", "page": "departemental/lots", "pseudo": "Sam",
             "resume": "Précision sur les lots", "texte": FICHE.replace("adhésions.", "adhésions importées."),
             "blob_sha": BLOB, "commit_sha": COMMIT, "altcha": solution(client), **champs}
    return client.post("/api/commentaires/propositions", json=corps, headers=VISITEUR)


def test_source_d_une_fiche(client, gh):
    r = client.get("/api/commentaires/propositions/source", params={"page": "departemental/lots"}).json()
    assert r == {"texte": FICHE, "blob_sha": BLOB, "commit_sha": COMMIT}


def test_proposition_puis_pull_request(client, gh):
    pid = proposer(client).json()["id"]
    admin(client)
    liste = client.get("/api/commentaires/admin/propositions").json()["propositions"]
    assert [l["texte"] for l in liste[0]["differences"] if l["type"] in "+-"] == [
        "Un lot regroupe des adhésions.", "Un lot regroupe des adhésions importées."]
    r = client.post(f"/api/commentaires/admin/propositions/{pid}/accepter")
    assert r.json() == {"pr_url": "https://github.com/exemple/pull/42"}
    branche = [c for c in gh.appels if c[1] == "/git/refs"][0][2]
    assert branche["sha"] == COMMIT and branche["ref"].startswith("refs/heads/proposition-")
    fichier = [c for c in gh.appels if c[0] == "PUT"][0]
    assert fichier[1] == "/contents/docs-departemental/lots.md" and fichier[2]["sha"] == BLOB
    assert "importées" in base64.b64decode(fichier[2]["content"]).decode()
    assert client.get("/api/commentaires/admin/propositions", params={"filtre": "acceptees"}).json()["propositions"][0]["pr_url"]


def test_nouvelle_fiche(client, gh):
    pid = proposer(client, type="nouvelle", titre="Gérer les remboursements", texte="Étapes à suivre…").json()["id"]
    admin(client)
    client.post(f"/api/commentaires/admin/propositions/{pid}/accepter")
    fichier = [c for c in gh.appels if c[0] == "PUT"][0]
    assert fichier[1] == "/contents/docs-departemental/gerer-les-remboursements.md" and "sha" not in fichier[2]
    assert base64.b64decode(fichier[2]["content"]).decode().startswith("# Gérer les remboursements\n")


def test_proposition_sans_changement_refusee(client, gh):
    assert proposer(client, texte=FICHE).status_code == 400


def test_fiche_modifiee_entre_temps(client, gh):
    assert proposer(client, blob_sha="c" * 40).status_code == 409


def test_proposition_refusee_par_admin(client, gh):
    pid = proposer(client).json()["id"]
    admin(client)
    assert client.post(f"/api/commentaires/admin/propositions/{pid}/refuser").status_code == 200
    assert not [c for c in gh.appels if c[0] in ("POST", "PUT")]


def test_page_hors_guide_refusee(client, gh):
    assert client.get("/api/commentaires/propositions/source", params={"page": "autre/x"}).status_code == 400
    assert client.get("/api/commentaires/propositions/source", params={"page": "departemental/../secret"}).status_code == 400
