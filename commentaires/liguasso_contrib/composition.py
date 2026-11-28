"""Assemblage : relie les cas d'usage à leurs adaptateurs."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .application.administration import Administration
from .application.commentaires import GestionCommentaires
from .application.ports import Fiches
from .application.propositions import GestionPropositions
from .config import Reglages
from .domaine.modeles import Regles
from .infrastructure.anti_robot import AntiRobotAltcha
from .infrastructure.github import FichesGitHub
from .infrastructure.securite import Empreintes, HorlogeSysteme, SessionsSignees, charger_secret
from .infrastructure.sqlite import (Base, DefisUtilisesSQLite, DepotCommentairesSQLite,
                                    DepotPropositionsSQLite, LimiteurSQLite)


@dataclass
class Services:
    commentaires: GestionCommentaires
    propositions: GestionPropositions
    administration: Administration
    anti_robot: AntiRobotAltcha
    empreintes: Empreintes
    cors_origines: list


def assembler(reglages: Reglages, regles: Optional[Regles] = None, fiches: Optional[Fiches] = None) -> Services:
    """*fiches* permet de remplacer GitHub (essais)."""
    if regles is None:
        regles = Regles(max_commentaires=(1000, 60), max_actions=(1000, 60), max_propositions=(1000, 60),
                        max_connexions_admin=(1000, 60)) \
            if reglages.limites_relachees else Regles()
    secret = charger_secret(reglages.secret, reglages.donnees)
    base = Base(reglages.donnees / "commentaires.sqlite3")
    limiteur = LimiteurSQLite(base)
    anti_robot = AntiRobotAltcha(secret, reglages.altcha_cout, DefisUtilisesSQLite(base))
    horloge = HorlogeSysteme()
    fiches = fiches or FichesGitHub(reglages.github_depot, reglages.github_branche,
                                    reglages.github_jeton, reglages.github_api)
    return Services(
        commentaires=GestionCommentaires(DepotCommentairesSQLite(base), limiteur, anti_robot, horloge, regles),
        propositions=GestionPropositions(DepotPropositionsSQLite(base), fiches, limiteur, anti_robot,
                                         horloge, regles, reglages.site_public),
        administration=Administration(reglages.admin_mot_de_passe, SessionsSignees(secret), limiteur, regles),
        anti_robot=anti_robot,
        empreintes=Empreintes(secret),
        cors_origines=reglages.cors_origines,
    )


def creer_app(reglages: Optional[Reglages] = None, **remplacements):
    from .interface.http import creer_api
    return creer_api(assembler(reglages or Reglages.depuis_environnement(), **remplacements))
