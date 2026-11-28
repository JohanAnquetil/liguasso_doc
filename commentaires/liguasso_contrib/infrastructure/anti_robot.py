"""Anti-robot ALTCHA : preuve de travail calculée par le navigateur, sans service tiers."""
from __future__ import annotations

import secrets
import time

import altcha

from ..domaine.erreurs import Invalide
from .sqlite import DefisUtilisesSQLite


class AntiRobotAltcha:
    def __init__(self, secret: str, cout: int, defis_utilises: DefisUtilisesSQLite, duree: int = 600):
        self.secret, self.cout, self.defis_utilises, self.duree = secret, cout, defis_utilises, duree

    def creer_defi(self) -> dict:
        return altcha.create_challenge(
            algorithm="PBKDF2/SHA-256", cost=self.cout, counter=secrets.randbelow(40) + 10,
            expires_at=int(time.time()) + self.duree, hmac_secret=self.secret,
            hmac_key_secret=self.secret + ":cle").to_dict()

    def verifier(self, preuve: str) -> None:
        if not preuve:
            raise Invalide("Vérification anti-robot manquante.")
        try:
            resultat = altcha.verify_solution(preuve, self.secret, hmac_key_secret=self.secret + ":cle")
            nonce = altcha.Payload.from_base64(preuve).challenge.parameters.nonce
        except Exception:
            raise Invalide("Vérification anti-robot invalide.")
        if not resultat.verified:
            raise Invalide("Vérification anti-robot expirée ou invalide. Réessayez.")
        if not self.defis_utilises.premiere_utilisation(nonce, self.duree):
            raise Invalide("Vérification anti-robot déjà utilisée. Réessayez.")
