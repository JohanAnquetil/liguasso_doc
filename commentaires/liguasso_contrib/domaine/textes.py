"""Règles pures sur les textes, les pages et les fiches."""
from __future__ import annotations

import difflib
import re
import unicodedata

from .erreurs import Invalide

PAGE_VALIDE = re.compile(r"^[a-z0-9][a-z0-9/_-]{0,199}$")
VISITEUR_VALIDE = re.compile(r"^[A-Za-z0-9_-]{16,64}$")
SHA_VALIDE = re.compile(r"^[0-9a-f]{40}$")


def nettoyer(texte: str, maximum: int) -> str:
    """Normalise, retire les caractères de contrôle et les lignes vides en trop, tronque."""
    texte = unicodedata.normalize("NFC", texte or "")
    texte = "".join(c for c in texte if c in "\n\t" or unicodedata.category(c)[0] != "C")
    texte = re.sub(r"\n{3,}", "\n\n", texte.replace("\r", "")).strip()
    return texte[:maximum]


def verifier_page(page: str) -> str:
    if not PAGE_VALIDE.match(page or ""):
        raise Invalide("Page invalide.")
    return page


def fichier_de_page(page: str, dossiers: dict) -> str:
    """departemental/adhesions-lots -> docs-departemental/adhesions-lots.md"""
    verifier_page(page)
    guide, _, relatif = page.partition("/")
    if guide not in dossiers or ".." in relatif.split("/"):
        raise Invalide("Page inconnue.")
    return f"{dossiers[guide]}/{relatif or 'index'}.md"


def nom_de_fiche(titre: str) -> str:
    """« Gérer les remboursements » -> gerer-les-remboursements"""
    nom = unicodedata.normalize("NFKD", titre).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", nom).strip("-")[:60] or "nouvelle-fiche"


def normaliser_fiche(texte: str) -> str:
    return unicodedata.normalize("NFC", (texte or "").replace("\r", "")).strip() + "\n"


def differences(avant: str, apres: str) -> list:
    """Lignes modifiées avec 2 lignes de contexte : [{"type": "+" | "-" | " " | "@", "texte": ...}]"""
    lignes = []
    for ligne in difflib.unified_diff(avant.splitlines(), apres.splitlines(), lineterm="", n=2):
        if ligne.startswith(("---", "+++")):
            continue
        if ligne.startswith("@@"):
            lignes.append({"type": "@", "texte": "…"})
        else:
            lignes.append({"type": ligne[:1] or " ", "texte": ligne[1:]})
    return lignes
