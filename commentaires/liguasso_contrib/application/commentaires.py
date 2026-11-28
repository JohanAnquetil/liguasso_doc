"""Cas d'usage des commentaires."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from ..domaine import modeles as m
from ..domaine.erreurs import Introuvable, Invalide
from ..domaine.textes import nettoyer, verifier_page
from .ports import AntiRobot, DepotCommentaires, Horloge, Limiteur


@dataclass
class NouveauCommentaire:
    page: str
    pseudo: str
    texte: str
    parent_id: Optional[int] = None
    preuve: str = ""        # anti-robot
    piege: str = ""         # champ invisible : rempli seulement par les robots


class GestionCommentaires:
    def __init__(self, depot: DepotCommentaires, limiteur: Limiteur, anti_robot: AntiRobot,
                 horloge: Horloge, regles: m.Regles):
        self.depot, self.limiteur, self.anti_robot = depot, limiteur, anti_robot
        self.horloge, self.regles = horloge, regles

    # --- Visiteurs ---

    def lister(self, page: str, visiteur: Optional[str]) -> list[dict]:
        verifier_page(page)
        commentaires = self.depot.visibles(page, visiteur)
        aimes = self.depot.aimes_par(visiteur, [c.id for c in commentaires]) if visiteur else set()
        visibles = {c.id for c in commentaires}
        return [{
            "id": c.id, "parent_id": c.parent_id, "pseudo": c.pseudo, "texte": c.texte,
            "cree_le": c.cree_le, "equipe": c.equipe, "en_attente": c.statut == m.ATTENTE,
            "likes": c.likes, "aime": c.id in aimes,
            "de_moi": visiteur is not None and c.visiteur == visiteur,
        } for c in commentaires
            # une réponse dont le parent n'est pas visible n'est pas affichée
            if not c.parent_id or c.parent_id in visibles]

    def commenter(self, demande: NouveauCommentaire, visiteur: str, ip: str) -> int:
        if demande.piege:
            return 0     # robot : on fait comme si tout allait bien, sans rien enregistrer
        verifier_page(demande.page)
        pseudo, texte = nettoyer(demande.pseudo, 40), nettoyer(demande.texte, 2000)
        if not pseudo or not texte:
            raise Invalide("Le pseudo et le commentaire sont obligatoires.")
        self.limiteur.consommer(f"commentaire:{ip}", *self.regles.max_commentaires)
        self.anti_robot.verifier(demande.preuve)
        parent_id = demande.parent_id
        if parent_id is not None:
            parent = self.depot.trouver(parent_id)
            if not parent or parent.page != demande.page or parent.statut != m.PUBLIE:
                raise Invalide("Le commentaire auquel vous répondez n'existe plus.")
            parent_id = parent.parent_id or parent.id      # un seul niveau de réponses
        return self.depot.ajouter(m.Commentaire(
            id=0, page=demande.page, parent_id=parent_id, pseudo=pseudo, texte=texte,
            statut=m.ATTENTE, cree_le=self.horloge.maintenant(), visiteur=visiteur), ip)

    def liker(self, cid: int, visiteur: str, ip: str) -> dict:
        self.limiteur.consommer(f"action:{ip}", *self.regles.max_actions)
        self._publie(cid)
        aime, likes = self.depot.basculer_like(cid, visiteur)
        return {"aime": aime, "likes": likes}

    def signaler(self, cid: int, motif: str, precision: str, preuve: str, visiteur: str, ip: str) -> dict:
        if motif not in m.MOTIFS:
            raise Invalide("Motif inconnu.")
        self.limiteur.consommer(f"action:{ip}", *self.regles.max_actions)
        self.anti_robot.verifier(preuve)
        self._publie(cid)
        if not self.depot.ajouter_signalement(cid, visiteur, ip, motif, nettoyer(precision, 300),
                                              self.horloge.maintenant()):
            return {"deja_signale": True}
        if self.depot.nombre_signaleurs(cid) >= self.regles.seuil_signalements:
            self.depot.changer_statut(cid, m.MASQUE, self.horloge.maintenant())
        return {"deja_signale": False}

    # --- Modération ---

    def moderer(self, cid: int, action: str) -> None:
        if not self.depot.trouver(cid):
            raise Introuvable("Commentaire introuvable.")
        quand = self.horloge.maintenant()
        if action == "publier":        # valide, ou rétablit un commentaire signalé
            self.depot.changer_statut(cid, m.PUBLIE, quand, signalements_traites=True)
        elif action == "refuser":
            self.depot.changer_statut(cid, m.REFUSE, quand, signalements_traites=True)
        elif action == "supprimer":    # définitif, réponses comprises
            self.depot.supprimer(cid)
        else:
            raise Invalide("Action inconnue.")

    def repondre_au_nom_de_l_equipe(self, cid: int, texte: str) -> None:
        parent = self.depot.trouver(cid)
        if not parent:
            raise Introuvable("Commentaire introuvable.")
        texte = nettoyer(texte, 2000)
        if not texte:
            raise Invalide("La réponse est vide.")
        quand = self.horloge.maintenant()
        self.depot.publier_si_attente(cid, quand)       # répondre valide aussi le commentaire
        self.depot.ajouter(m.Commentaire(
            id=0, page=parent.page, parent_id=parent.parent_id or parent.id, pseudo=m.NOM_EQUIPE,
            texte=texte, statut=m.PUBLIE, cree_le=quand, equipe=True), None)

    def pour_admin(self, filtre: str) -> dict:
        if filtre not in ("attente", "signales", "publies", "refuses"):
            raise Invalide("Filtre inconnu.")
        return {
            "compteurs": self.depot.compteurs(),
            "commentaires": [{
                "id": c.id, "page": c.page, "pseudo": c.pseudo, "texte": c.texte, "statut": c.statut,
                "equipe": c.equipe, "cree_le": c.cree_le, "likes": c.likes,
                "parent": {"pseudo": p.pseudo, "texte": p.texte} if p else None,
                "signalements": [{"motif": m.MOTIFS.get(s.motif, s.motif), "precision": s.precision,
                                  "cree_le": s.cree_le} for s in signalements],
            } for c, p, signalements in self.depot.pour_admin(filtre)],
        }

    def _publie(self, cid: int) -> None:
        c = self.depot.trouver(cid)
        if not c or c.statut != m.PUBLIE:
            raise Introuvable("Commentaire introuvable.")
