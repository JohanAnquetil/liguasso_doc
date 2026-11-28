"""Secret du service, empreintes (adresses IP, visiteurs) et sessions de modération."""
from __future__ import annotations

import datetime as dt
import hashlib
import hmac
import secrets
from pathlib import Path

from itsdangerous import BadSignature, SignatureExpired, TimestampSigner


def charger_secret(fourni: str, dossier: Path) -> str:
    """Le secret fourni, sinon un secret créé une fois et gardé avec les données."""
    if fourni:
        return fourni
    dossier.mkdir(parents=True, exist_ok=True)
    fichier = dossier / "secret"
    if not fichier.exists():
        fichier.write_text(secrets.token_hex(32))
        fichier.chmod(0o600)
    return fichier.read_text().strip()


class Empreintes:
    """Rien n'est stocké en clair : seulement une empreinte salée et tronquée."""

    def __init__(self, secret: str):
        self.secret = secret.encode()

    def de(self, valeur: str, sel: str) -> str:
        return hmac.new(self.secret, f"{sel}:{valeur}".encode(), hashlib.sha256).hexdigest()[:32]


class SessionsSignees:
    def __init__(self, secret: str, duree: int = 8 * 3600):
        self.signeur, self.duree = TimestampSigner(secret, salt="admin"), duree

    def creer(self) -> str:
        return self.signeur.sign(b"admin").decode()

    def valide(self, jeton: str) -> bool:
        try:
            self.signeur.unsign(jeton, max_age=self.duree)
            return True
        except (BadSignature, SignatureExpired):
            return False


class HorlogeSysteme:
    def maintenant(self) -> str:
        return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
