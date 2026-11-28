"""L'adaptateur GitHub face à un faux serveur HTTP local (aucun appel au vrai GitHub)."""
import base64
import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest

from liguasso_contrib.domaine.erreurs import Introuvable, ServiceExterne
from liguasso_contrib.infrastructure.github import FichesGitHub

FICHE = "# Lots\n"


@pytest.fixture
def serveur():
    recu = []

    class Faux(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def repondre(self, code, corps):
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(corps).encode())

        def do_GET(self):
            recu.append(("GET", self.path, self.headers.get("Authorization")))
            if self.path.endswith("/git/ref/heads/main"):
                return self.repondre(200, {"object": {"sha": "c" * 40}})
            if "/contents/docs/lots.md" in self.path:
                return self.repondre(200, {"sha": "b" * 40, "content": base64.b64encode(FICHE.encode()).decode()})
            if "/contents/docs/erreur.md" in self.path:
                return self.repondre(500, {})
            self.repondre(404, {})

        def ecrire(self):
            corps = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            recu.append((self.command, self.path, corps))
            self.repondre(201, {"html_url": "https://github.com/o/d/pull/7"} if self.path.endswith("/pulls") else {})

        do_POST = do_PUT = ecrire

    httpd = HTTPServer(("127.0.0.1", 0), Faux)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{httpd.server_port}", recu
    httpd.shutdown()


def test_lecture_sans_jeton(serveur):
    api, recu = serveur
    fiches = FichesGitHub("o/d", api=api)
    version = fiches.version_actuelle()
    assert fiches.lire("docs/lots.md", version) == (FICHE, "b" * 40)
    assert not fiches.ecriture_possible and recu[0][2] is None


def test_lecture_mise_en_cache(serveur):
    api, recu = serveur
    fiches = FichesGitHub("o/d", api=api)
    for _ in range(3):
        fiches.lire("docs/lots.md", fiches.version_actuelle())
    assert len(recu) == 2


def test_fiche_absente_et_erreur(serveur):
    api, _ = serveur
    fiches = FichesGitHub("o/d", api=api)
    with pytest.raises(Introuvable):
        fiches.lire("docs/absente.md", "c" * 40)
    assert not fiches.existe("docs/absente.md", "c" * 40)
    with pytest.raises(ServiceExterne):
        fiches.lire("docs/erreur.md", "c" * 40)


def test_proposer_cree_branche_fichier_et_pull_request(serveur):
    api, recu = serveur
    fiches = FichesGitHub("o/d", jeton="jeton", api=api)
    from liguasso_contrib.domaine.modeles import FichierPropose
    url = fiches.proposer("proposition-1-lots", "c" * 40, [FichierPropose("docs/lots.md", "# Lots modifié\n", "b" * 40)],
                          "Message", "Titre", "Corps")
    assert url == "https://github.com/o/d/pull/7"
    (m1, c1, ref), (m2, c2, fichier), (m3, c3, pr) = recu
    assert (m1, c1, ref) == ("POST", "/repos/o/d/git/refs", {"ref": "refs/heads/proposition-1-lots", "sha": "c" * 40})
    assert (m2, c2, fichier["sha"], fichier["branch"]) == ("PUT", "/repos/o/d/contents/docs/lots.md", "b" * 40, "proposition-1-lots")
    assert base64.b64decode(fichier["content"]).decode() == "# Lots modifié\n"
    assert (m3, pr["head"], pr["base"], pr["title"]) == ("POST", "proposition-1-lots", "main", "Titre")
