"""Ports : ce dont les cas d'usage ont besoin, sans dire comment c'est fait.

Implémentés par infrastructure/ (production) et par les doublures des tests unitaires.
"""
from __future__ import annotations

from typing import Optional, Protocol

from ..domaine.modeles import Commentaire, FichierPropose, Proposition, Signalement


class DepotCommentaires(Protocol):
    def visibles(self, page: str, visiteur: Optional[str]) -> list[Commentaire]:
        """Publiés, plus ceux en attente du visiteur, dans l'ordre de création (likes comptés)."""
    def aimes_par(self, visiteur: str, ids: list[int]) -> set[int]: ...
    def trouver(self, cid: int) -> Optional[Commentaire]: ...
    def ajouter(self, c: Commentaire, ip: Optional[str]) -> int: ...
    def basculer_like(self, cid: int, visiteur: str) -> tuple[bool, int]: ...
    def ajouter_signalement(self, cid: int, visiteur: str, ip: str, motif: str, precision: str, quand: str) -> bool:
        """False si ce visiteur a déjà signalé ce commentaire."""
    def nombre_signaleurs(self, cid: int) -> int:
        """Adresses IP différentes parmi les signalements non traités."""
    def changer_statut(self, cid: int, statut: str, quand: str, signalements_traites: bool = False) -> None: ...
    def publier_si_attente(self, cid: int, quand: str) -> None: ...
    def supprimer(self, cid: int) -> None: ...
    def pour_admin(self, filtre: str) -> list[tuple[Commentaire, Optional[Commentaire], list[Signalement]]]:
        """(commentaire, parent, signalements non traités), du plus récent au plus ancien."""
    def compteurs(self) -> dict[str, int]: ...


class DepotPropositions(Protocol):
    def ajouter(self, p: Proposition, visiteur: str, ip: str) -> int: ...
    def trouver(self, pid: int) -> Optional[Proposition]: ...
    def lister(self, statut: str) -> list[Proposition]: ...
    def accepter(self, pid: int, pr_url: str, quand: str) -> None: ...
    def refuser(self, pid: int, quand: str) -> bool:
        """False si introuvable ou déjà traitée."""


class Limiteur(Protocol):
    def consommer(self, cle: str, maximum: int, fenetre: int) -> None:
        """Lève TropDeDemandes au-delà de *maximum* appels par *fenetre* secondes."""


class AntiRobot(Protocol):
    def creer_defi(self) -> dict: ...
    def verifier(self, preuve: str) -> None:
        """Lève Invalide si la preuve manque, est fausse, expirée ou déjà utilisée."""


class Fiches(Protocol):
    """Les fiches du guide dans le dépôt Git (GitHub)."""
    ecriture_possible: bool
    def version_actuelle(self) -> str: ...
    def lire(self, chemin: str, version: str) -> tuple[str, str]:
        """(texte, blob_sha). Lève Introuvable si le fichier n'existe pas."""
    def existe(self, chemin: str, version: str) -> bool: ...
    def proposer(self, branche: str, depart: str, fichiers: list[FichierPropose],
                 message: str, titre_pr: str, corps_pr: str) -> str:
        """Crée la branche, y écrit les fichiers, ouvre la pull request ; renvoie son adresse."""


class Horloge(Protocol):
    def maintenant(self) -> str: ...


class Sessions(Protocol):
    def creer(self) -> str: ...
    def valide(self, jeton: str) -> bool: ...
