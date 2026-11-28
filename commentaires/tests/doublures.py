"""Doublures en mémoire des ports, pour tester les cas d'usage sans base ni réseau.

Leur comportement est vérifié par les mêmes tests de contrat que les adaptateurs SQLite
(tests/integration/test_contrats_depots.py) : elles ne peuvent pas diverger en silence.
"""
from __future__ import annotations

import itertools
from dataclasses import replace

from liguasso_contrib.domaine import modeles as m
from liguasso_contrib.domaine.erreurs import Introuvable, Invalide, TropDeDemandes


class DepotCommentairesMemoire:
    def __init__(self):
        self.commentaires: dict[int, m.Commentaire] = {}
        self.likes: set[tuple[int, str]] = set()
        self.signalements: list[dict] = []
        self._ids = itertools.count(1)

    def _likes(self, cid):
        return sum(1 for c, _ in self.likes if c == cid)

    def visibles(self, page, visiteur):
        return [replace(c, likes=self._likes(c.id)) for c in sorted(self.commentaires.values(), key=lambda c: (c.cree_le, c.id))
                if c.page == page and (c.statut == m.PUBLIE or (c.statut == m.ATTENTE and visiteur and c.visiteur == visiteur))]

    def aimes_par(self, visiteur, ids):
        return {c for c, v in self.likes if v == visiteur and c in ids}

    def trouver(self, cid):
        c = self.commentaires.get(cid)
        return replace(c) if c else None

    def ajouter(self, c, ip):
        cid = next(self._ids)
        self.commentaires[cid] = replace(c, id=cid)
        return cid

    def basculer_like(self, cid, visiteur):
        if (cid, visiteur) in self.likes:
            self.likes.discard((cid, visiteur))
            return False, self._likes(cid)
        self.likes.add((cid, visiteur))
        return True, self._likes(cid)

    def ajouter_signalement(self, cid, visiteur, ip, motif, precision, quand):
        if any(s["cid"] == cid and s["visiteur"] == visiteur for s in self.signalements):
            return False
        self.signalements.append({"cid": cid, "visiteur": visiteur, "ip": ip, "motif": motif,
                                  "precision": precision, "quand": quand, "traite": False})
        return True

    def nombre_signaleurs(self, cid):
        return len({s["ip"] for s in self.signalements if s["cid"] == cid and not s["traite"]})

    def changer_statut(self, cid, statut, quand, signalements_traites=False):
        self.commentaires[cid].statut = statut
        if signalements_traites:
            for s in self.signalements:
                if s["cid"] == cid:
                    s["traite"] = True

    def publier_si_attente(self, cid, quand):
        if self.commentaires[cid].statut == m.ATTENTE:
            self.commentaires[cid].statut = m.PUBLIE

    def supprimer(self, cid):
        for c in [c for c in self.commentaires.values() if c.parent_id == cid]:
            self.supprimer(c.id)
        self.commentaires.pop(cid, None)
        self.likes = {l for l in self.likes if l[0] != cid}
        self.signalements = [s for s in self.signalements if s["cid"] != cid]

    def _non_traites(self, cid):
        return [m.Signalement(s["motif"], s["precision"], s["quand"]) for s in self.signalements
                if s["cid"] == cid and not s["traite"]]

    def _filtre(self, filtre, c):
        return {"attente": c.statut == m.ATTENTE, "publies": c.statut == m.PUBLIE, "refuses": c.statut == m.REFUSE,
                "signales": c.statut == m.MASQUE or bool(self._non_traites(c.id))}[filtre]

    def pour_admin(self, filtre):
        return [(replace(c, likes=self._likes(c.id)), self.trouver(c.parent_id) if c.parent_id else None,
                 self._non_traites(c.id))
                for c in sorted(self.commentaires.values(), key=lambda c: (c.cree_le, c.id), reverse=True)
                if self._filtre(filtre, c)]

    def compteurs(self):
        return {f: sum(self._filtre(f, c) for c in self.commentaires.values())
                for f in ("attente", "signales", "publies", "refuses")}


class DepotPropositionsMemoire:
    def __init__(self):
        self.propositions: dict[int, m.Proposition] = {}
        self._ids = itertools.count(1)

    def ajouter(self, p, visiteur, ip):
        pid = next(self._ids)
        self.propositions[pid] = replace(p, id=pid)
        return pid

    def trouver(self, pid):
        p = self.propositions.get(pid)
        return replace(p) if p else None

    def lister(self, statut):
        return sorted((replace(p) for p in self.propositions.values() if p.statut == statut),
                      key=lambda p: (p.cree_le, p.id), reverse=True)

    def accepter(self, pid, pr_url, quand):
        self.propositions[pid].statut, self.propositions[pid].pr_url = m.P_ACCEPTEE, pr_url

    def refuser(self, pid, quand):
        p = self.propositions.get(pid)
        if not p or p.statut != m.P_ATTENTE:
            return False
        p.statut = m.P_REFUSEE
        return True


class LimiteurMemoire:
    """Compte les appels ; les fenêtres de temps sont ignorées."""
    def __init__(self):
        self.appels: dict[str, int] = {}

    def consommer(self, cle, maximum, fenetre):
        if self.appels.get(cle, 0) >= maximum:
            raise TropDeDemandes()
        self.appels[cle] = self.appels.get(cle, 0) + 1


class AntiRobotFactice:
    """Accepte la preuve « ok », une seule fois chacune si elle est numérotée (« ok-1 »)."""
    def __init__(self):
        self.utilisees: set[str] = set()

    def creer_defi(self):
        return {"factice": True}

    def verifier(self, preuve):
        if not preuve or not preuve.startswith("ok"):
            raise Invalide("Vérification anti-robot manquante.")
        if preuve != "ok" and preuve in self.utilisees:
            raise Invalide("Vérification anti-robot déjà utilisée. Réessayez.")
        self.utilisees.add(preuve)


V1, V2 = "1" * 40, "2" * 40     # identifiants de versions (commits) du dépôt


class FichesEnMemoire:
    """Un dépôt de fiches minimal : versions successives et pull requests créées."""
    def __init__(self, fiches: dict[str, str] | None = None, ecriture_possible: bool = True):
        self.versions = {V1: dict(fiches or {})}
        self.actuelle = V1
        self.ecriture_possible = ecriture_possible
        self.pull_requests: list[dict] = []

    @staticmethod
    def sha(texte: str) -> str:
        import hashlib
        return hashlib.sha1(texte.encode()).hexdigest()

    def modifier(self, chemin: str, texte: str, version: str = V2):
        """Simule une modification de la fiche dans le dépôt (nouvelle version)."""
        self.versions[version] = {**self.versions[self.actuelle], chemin: texte}
        self.actuelle = version

    def version_actuelle(self):
        return self.actuelle

    def lire(self, chemin, version):
        fiches = self.versions.get(version, {})
        if chemin not in fiches:
            raise Introuvable("Cette fiche n'existe pas dans le dépôt.")
        return fiches[chemin], self.sha(fiches[chemin])

    def existe(self, chemin, version):
        return chemin in self.versions.get(version, {})

    def proposer(self, branche, depart, fichiers, message, titre_pr, corps_pr):
        principal = fichiers[0]
        self.pull_requests.append(dict(branche=branche, depart=depart, chemin=principal.chemin, texte=principal.texte,
                                       blob_sha=principal.blob_sha, fichiers=list(fichiers), message=message,
                                       titre=titre_pr, corps=corps_pr))
        return f"https://github.com/exemple/pull/{len(self.pull_requests)}"


class HorlogeFixe:
    """Avance d'une seconde à chaque lecture : l'ordre de création reste déterministe."""
    def __init__(self, debut: str = "2026-11-28T10:00:00+00:00"):
        import datetime as dt
        self._t = dt.datetime.fromisoformat(debut)

    def maintenant(self):
        import datetime as dt
        self._t += dt.timedelta(seconds=1)
        return self._t.isoformat(timespec="seconds")


class SessionsFactices:
    def creer(self):
        return "jeton-valide"

    def valide(self, jeton):
        return jeton == "jeton-valide"
