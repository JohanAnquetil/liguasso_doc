"""Les fiches du guide sur GitHub (lecture publique, écriture avec un jeton)."""
from __future__ import annotations

import base64
import json
import time
import urllib.error
import urllib.request
from typing import Optional

from ..domaine.erreurs import Introuvable, ServiceExterne


class _Absent(Exception):
    pass


class FichesGitHub:
    def __init__(self, depot: str, branche: str = "main", jeton: str = "",
                 api: str = "https://api.github.com", duree_cache: int = 300):
        self.depot, self.branche, self.jeton, self.api = depot, branche, jeton, api.rstrip("/")
        self.duree_cache = duree_cache
        self._cache: dict = {}

    @property
    def ecriture_possible(self) -> bool:
        return bool(self.jeton)

    def _appel(self, methode: str, chemin: str, corps: Optional[dict] = None) -> dict:
        entetes = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28",
                   "User-Agent": "guide-liguasso-contributions"}
        if self.jeton:
            entetes["Authorization"] = f"Bearer {self.jeton}"
        requete = urllib.request.Request(
            f"{self.api}/repos/{self.depot}{chemin}", method=methode, headers=entetes,
            data=json.dumps(corps).encode() if corps is not None else None)
        try:
            with urllib.request.urlopen(requete, timeout=20) as r:
                return json.loads(r.read() or b"{}")
        except urllib.error.HTTPError as e:
            if e.code == 404:
                raise _Absent(chemin)
            raise ServiceExterne(f"GitHub a refusé la demande ({e.code}).")
        except urllib.error.URLError:
            raise ServiceExterne("GitHub ne répond pas. Réessayez plus tard.")

    def version_actuelle(self) -> str:
        en_cache = self._cache.get("version")
        if en_cache and en_cache[1] > time.time() - self.duree_cache:
            return en_cache[0]
        version = self._appel("GET", f"/git/ref/heads/{self.branche}")["object"]["sha"]
        self._cache["version"] = (version, time.time())
        return version

    def lire(self, chemin: str, version: str) -> tuple[str, str]:
        cle = (chemin, version)
        if len(self._cache) > 500:
            self._cache.clear()
        if cle not in self._cache:      # un fichier à une version donnée ne change jamais
            try:
                f = self._appel("GET", f"/contents/{chemin}?ref={version}")
            except _Absent:
                raise Introuvable("Cette fiche n'existe pas dans le dépôt.")
            self._cache[cle] = (base64.b64decode(f["content"]).decode(), f["sha"])
        return self._cache[cle]

    def existe(self, chemin: str, version: str) -> bool:
        try:
            self.lire(chemin, version)
            return True
        except Introuvable:
            return False

    def proposer(self, branche, depart, fichiers, message, titre_pr, corps_pr) -> str:
        self._appel("POST", "/git/refs", {"ref": f"refs/heads/{branche}", "sha": depart})
        for f in fichiers:   # un commit par fichier, sur la même branche
            corps = {"message": message, "content": base64.b64encode(f.texte.encode()).decode(), "branch": branche}
            if f.blob_sha:
                corps["sha"] = f.blob_sha
            self._appel("PUT", f"/contents/{f.chemin}", corps)
        pr = self._appel("POST", "/pulls", {"title": titre_pr, "head": branche, "base": self.branche, "body": corps_pr})
        return pr.get("html_url", "")
