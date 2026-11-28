"""Entités du domaine."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

NOM_EQUIPE = "Équipe Ligu'asso"

MOTIFS = {"spam": "Spam ou publicité", "propos": "Propos inappropriés",
          "faux": "Information fausse", "autre": "Autre"}

# Statuts d'un commentaire
ATTENTE, PUBLIE, MASQUE, REFUSE = "attente", "publie", "masque", "refuse"
# Statuts d'une proposition
P_ATTENTE, P_ACCEPTEE, P_REFUSEE = "attente", "acceptee", "refusee"
MODIFICATION, NOUVELLE = "modification", "nouvelle"


@dataclass
class Commentaire:
    id: int
    page: str
    pseudo: str
    texte: str
    statut: str
    cree_le: str
    parent_id: Optional[int] = None
    equipe: bool = False
    visiteur: Optional[str] = None
    likes: int = 0


@dataclass
class Signalement:
    motif: str
    precision: str
    cree_le: str


@dataclass
class Proposition:
    id: int
    type: str
    page: str
    chemin: str
    pseudo: str
    resume: str
    texte_avant: str
    texte: str
    statut: str
    cree_le: str
    titre: Optional[str] = None
    blob_sha: Optional[str] = None
    commit_sha: Optional[str] = None
    pr_url: Optional[str] = None


@dataclass
class Regles:
    """Seuils et limites, réglables pour les tests."""
    seuil_signalements: int = 3          # personnes différentes avant masquage automatique
    max_commentaires: tuple = (5, 600)   # par adresse IP : (nombre, fenêtre en secondes)
    max_actions: tuple = (60, 3600)      # likes et signalements
    max_propositions: tuple = (3, 3600)
    max_connexions_admin: tuple = (5, 900)
    taille_max_fiche: int = 100_000
    dossiers: dict = field(default_factory=lambda: {
        "association": "docs-association", "departemental": "docs-departemental", "test": "docs-test"})
