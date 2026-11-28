"""Cas d'usage des propositions de modification de fiches."""
from __future__ import annotations

from dataclasses import dataclass

from ..domaine import modeles as m
from ..domaine.erreurs import Conflit, Indisponible, Introuvable, Invalide
from ..domaine.textes import (SHA_VALIDE, differences, fichier_de_page, nettoyer, nom_de_fiche,
                              normaliser_fiche, verifier_page)
from .ports import AntiRobot, DepotPropositions, Fiches, Horloge, Limiteur


@dataclass
class NouvelleProposition:
    type: str
    page: str
    pseudo: str
    resume: str
    texte: str
    titre: str = ""
    blob_sha: str = ""      # version de la fiche au départ (modification)
    commit_sha: str = ""
    preuve: str = ""
    piege: str = ""


class GestionPropositions:
    def __init__(self, depot: DepotPropositions, fiches: Fiches, limiteur: Limiteur,
                 anti_robot: AntiRobot, horloge: Horloge, regles: m.Regles, site_public: str):
        self.depot, self.fiches, self.limiteur, self.anti_robot = depot, fiches, limiteur, anti_robot
        self.horloge, self.regles, self.site_public = horloge, regles, site_public.rstrip("/")

    def source(self, page: str) -> dict:
        """Texte actuel d'une fiche, avec ses versions, pour l'éditeur."""
        chemin = fichier_de_page(page, self.regles.dossiers)
        version = self.fiches.version_actuelle()
        texte, blob_sha = self.fiches.lire(chemin, version)
        return {"texte": texte, "blob_sha": blob_sha, "commit_sha": version}

    def proposer(self, d: NouvelleProposition, visiteur: str, ip: str) -> int:
        if d.piege:
            return 0
        if d.type not in (m.MODIFICATION, m.NOUVELLE):
            raise Invalide("Proposition invalide.")
        verifier_page(d.page)
        pseudo, resume = nettoyer(d.pseudo, 40), nettoyer(d.resume, 300)
        texte = normaliser_fiche(d.texte)
        if not pseudo or not resume or not texte.strip():
            raise Invalide("Le pseudo, le résumé et le texte sont obligatoires.")
        if len(texte) > self.regles.taille_max_fiche:
            raise Invalide("Le texte est trop long.")
        self.limiteur.consommer(f"proposition:{ip}", *self.regles.max_propositions)
        self.anti_robot.verifier(d.preuve)

        if d.type == m.MODIFICATION:
            chemin = fichier_de_page(d.page, self.regles.dossiers)
            if not SHA_VALIDE.match(d.blob_sha or "") or not SHA_VALIDE.match(d.commit_sha or ""):
                raise Invalide("Version de la fiche manquante. Rechargez la page.")
            # Texte de départ relu à la version que la personne a modifiée
            avant, blob_sha = self.fiches.lire(chemin, d.commit_sha)
            if blob_sha != d.blob_sha:
                raise Conflit("La fiche a changé entre-temps. Rechargez la page et recommencez.")
            if avant.strip() == texte.strip():
                raise Invalide("Vous n'avez rien modifié.")
            titre, commit_sha = None, d.commit_sha
        else:
            titre = nettoyer(d.titre, 120)
            if not titre:
                raise Invalide("Donnez un titre à la nouvelle fiche.")
            guide = d.page.partition("/")[0]
            if guide not in self.regles.dossiers:
                raise Invalide("Guide inconnu.")
            chemin = f"{self.regles.dossiers[guide]}/{nom_de_fiche(titre)}.md"
            avant, blob_sha, commit_sha = "", None, None   # partira de la version actuelle du dépôt
            if not texte.lstrip().startswith("# "):
                texte = f"# {titre}\n\n{texte}"
        return self.depot.ajouter(m.Proposition(
            id=0, type=d.type, page=d.page, chemin=chemin, titre=titre, pseudo=pseudo, resume=resume,
            texte_avant=avant, texte=texte, blob_sha=blob_sha, commit_sha=commit_sha,
            statut=m.P_ATTENTE, cree_le=self.horloge.maintenant()), visiteur, ip)

    # --- Modération ---

    def pour_admin(self, filtre: str) -> dict:
        statuts = {"attente": m.P_ATTENTE, "acceptees": m.P_ACCEPTEE, "refusees": m.P_REFUSEE}
        if filtre not in statuts:
            raise Invalide("Filtre inconnu.")
        return {"github": self.fiches.ecriture_possible, "propositions": [{
            "id": p.id, "type": p.type, "page": p.page, "chemin": p.chemin, "titre": p.titre,
            "pseudo": p.pseudo, "resume": p.resume, "cree_le": p.cree_le, "statut": p.statut,
            "pr_url": p.pr_url, "differences": differences(p.texte_avant, p.texte),
        } for p in self.depot.lister(statuts[filtre])]}

    def accepter(self, pid: int) -> str:
        """Ouvre une pull request avec la proposition ; renvoie son adresse."""
        if not self.fiches.ecriture_possible:
            raise Indisponible("GITHUB_TOKEN n'est pas défini sur le serveur : impossible de créer la pull request.")
        p = self.depot.trouver(pid)
        if not p or p.statut != m.P_ATTENTE:
            raise Introuvable("Proposition introuvable ou déjà traitée.")
        if p.type == m.MODIFICATION:
            depart = p.commit_sha       # à partir de la version modifiée : GitHub signale les conflits
        else:
            depart = self.fiches.version_actuelle()
            if self.fiches.existe(p.chemin, depart):
                raise Conflit(f"Une fiche {p.chemin} existe déjà.")
        nom = nom_de_fiche(p.titre or p.chemin.rsplit("/", 1)[-1].removesuffix(".md"))
        message = (f"Proposition n°{p.id} : {p.resume}" if p.type == m.MODIFICATION
                   else f"Nouvelle fiche proposée : {p.titre}")
        lien = f"{self.site_public}/{p.page}/"
        corps = (f"**Proposée par** « {p.pseudo} » le {p.cree_le[:10]}, depuis [{p.page}]({lien}).\n\n"
                 f"**Résumé** : {p.resume}\n\n"
                 + ("Nouvelle fiche : pensez à l'ajouter au menu (`nav`) dans `mkdocs.*.yml`.\n\n"
                    if p.type == m.NOUVELLE else "")
                 + "Validée dans la page de modération du guide. Relisez puis fusionnez pour mettre en ligne.")
        url = self.fiches.proposer(
            branche=f"proposition-{p.id}-{nom}", depart=depart, chemin=p.chemin, texte=p.texte,
            blob_sha=p.blob_sha, message=f"{message}\n\nProposée par « {p.pseudo} » depuis le guide en ligne.",
            titre_pr=message[:120], corps_pr=corps)
        self.depot.accepter(p.id, url, self.horloge.maintenant())
        return url

    def refuser(self, pid: int) -> None:
        if not self.depot.refuser(pid, self.horloge.maintenant()):
            raise Introuvable("Proposition introuvable ou déjà traitée.")
