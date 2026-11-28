"""Connexion à la page de modération."""
from __future__ import annotations

import hmac

from ..domaine.erreurs import Indisponible, NonAutorise
from ..domaine.modeles import Regles
from .ports import Limiteur, Sessions


class Administration:
    def __init__(self, mot_de_passe: str, sessions: Sessions, limiteur: Limiteur, regles: Regles):
        self.mot_de_passe, self.sessions, self.limiteur, self.regles = mot_de_passe, sessions, limiteur, regles

    def connecter(self, mot_de_passe: str, ip: str) -> str:
        """Renvoie un jeton de session si le mot de passe est bon."""
        if not self.mot_de_passe:
            raise Indisponible("Administration désactivée : ADMIN_MOT_DE_PASSE n'est pas défini.")
        self.limiteur.consommer(f"connexion:{ip}", *self.regles.max_connexions_admin)
        if not hmac.compare_digest(mot_de_passe.encode(), self.mot_de_passe.encode()):
            raise NonAutorise("Mot de passe incorrect.")
        return self.sessions.creer()

    def verifier(self, jeton: str) -> None:
        if not jeton or not self.sessions.valide(jeton):
            raise NonAutorise("Connexion requise.")
