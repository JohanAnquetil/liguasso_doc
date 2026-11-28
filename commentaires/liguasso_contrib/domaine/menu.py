"""Le menu d'un guide (section `nav:` d'un fichier mkdocs.*.yml), lu et modifié comme du texte.

On n'utilise pas de bibliothèque YAML pour écrire : le fichier est modifié par insertion de
lignes, le reste (commentaires, ordre, mise en forme) reste intact au caractère près.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional

from .erreurs import Invalide

ENTREE = re.compile(r'^(?P<indent> *)- (?P<libelle>"(?:[^"\\]|\\.)*"|\'[^\']*\'|[^:]+?)\s*:\s*(?P<cible>.*?)\s*$')
PAS = 4   # décalage d'un niveau dans les fichiers du projet (« - Rubrique: » puis « ↦ ↦ - Fiche: »)


@dataclass
class Rubrique:
    titre: str
    sous_rubriques: list = field(default_factory=list)


def _libelle(brut: str) -> str:
    brut = brut.strip()
    if len(brut) >= 2 and brut[0] == brut[-1] and brut[0] in "\"'":
        return brut[1:-1].replace('\\"', '"')
    return brut


def _citer(libelle: str) -> str:
    """Met le libellé entre guillemets si YAML pourrait mal le lire."""
    if re.search(r'[:#\[\]{}&*!|>\'"%@`,?]', libelle) or libelle != libelle.strip() or libelle[:1] in "-":
        return '"' + libelle.replace('\\', '\\\\').replace('"', '\\"') + '"'
    return libelle


def _bornes_nav(lignes: list[str]) -> tuple[int, int]:
    """Indices [debut, fin) des lignes d'éléments du menu (après « nav: »)."""
    try:
        debut = next(i for i, l in enumerate(lignes) if re.match(r"^nav:\s*$", l)) + 1
    except StopIteration:
        raise Invalide("Ce guide n'a pas de menu (nav).")
    fin = debut
    while fin < len(lignes) and (lignes[fin].strip() == "" or lignes[fin].startswith((" ", "-"))):
        fin += 1
    while fin > debut and lignes[fin - 1].strip() == "":
        fin -= 1
    return debut, fin


def _entrees(lignes, debut, fin):
    """(indice, indentation, libellé, cible) de chaque entrée du menu."""
    for i in range(debut, fin):
        m = ENTREE.match(lignes[i])
        if m:
            yield i, len(m["indent"]), _libelle(m["libelle"]), m["cible"]


def _bloc(lignes, i, fin):
    """Fin (exclue) du bloc de l'entrée i : jusqu'à une entrée de même indentation ou moins."""
    indent = len(ENTREE.match(lignes[i])["indent"])
    j = i + 1
    while j < fin:
        m = ENTREE.match(lignes[j])
        if m and len(m["indent"]) <= indent:
            break
        j += 1
    while j > i + 1 and lignes[j - 1].strip() == "":
        j -= 1
    return j


def lire_menu(yml: str) -> list[Rubrique]:
    """Les rubriques (entrées qui contiennent d'autres entrées) et leurs sous-rubriques."""
    lignes = yml.split("\n")
    debut, fin = _bornes_nav(lignes)
    entrees = list(_entrees(lignes, debut, fin))
    if not entrees:
        return []
    racine = min(e[1] for e in entrees)
    rubriques = []
    for i, indent, libelle, cible in entrees:
        if indent == racine and cible == "":
            sous = [l for j, ind, l, c in entrees if c == "" and ind == indent + PAS and i < j < _bloc(lignes, i, fin)]
            rubriques.append(Rubrique(libelle, sous))
    return rubriques


def ajouter_au_menu(yml: str, rubrique: str, sous_rubrique: Optional[str], libelle: str, fichier: str) -> str:
    """Ajoute « libellé: fichier » à la fin de la rubrique (et de la sous-rubrique), en les créant
    au besoin à la fin du menu ou de la rubrique."""
    rubrique, libelle = rubrique.strip(), libelle.strip()
    sous_rubrique = (sous_rubrique or "").strip() or None
    if not rubrique or not libelle:
        raise Invalide("La rubrique et le nom dans le menu sont obligatoires.")
    lignes = yml.split("\n")
    debut, fin = _bornes_nav(lignes)
    entrees = list(_entrees(lignes, debut, fin))
    racine = min((e[1] for e in entrees), default=2)

    def ligne(indent, texte, cible=""):
        return " " * indent + "- " + _citer(texte) + ":" + (" " + cible if cible else "")

    page = lambda indent: ligne(indent, libelle, fichier)

    trouvee = next(((i, c) for i, ind, l, c in entrees if ind == racine and l.lower() == rubrique.lower()), None)
    if trouvee and trouvee[1]:
        raise Invalide(f"« {rubrique} » est déjà une fiche du menu, pas une rubrique.")
    if not trouvee:
        nouvelles = [ligne(racine, rubrique)]
        if sous_rubrique:
            nouvelles += [ligne(racine + PAS, sous_rubrique), page(racine + 2 * PAS)]
        else:
            nouvelles.append(page(racine + PAS))
        return "\n".join(lignes[:fin] + nouvelles + lignes[fin:])

    i_rub = trouvee[0]
    fin_rub = _bloc(lignes, i_rub, fin)
    if not sous_rubrique:
        return "\n".join(lignes[:fin_rub] + [page(racine + PAS)] + lignes[fin_rub:])

    sous = next(((j, c) for j, ind, l, c in entrees
                 if i_rub < j < fin_rub and ind == racine + PAS and l.lower() == sous_rubrique.lower()), None)
    if sous and sous[1]:
        raise Invalide(f"« {sous_rubrique} » est déjà une fiche du menu, pas une sous-rubrique.")
    if not sous:
        return "\n".join(lignes[:fin_rub] + [ligne(racine + PAS, sous_rubrique), page(racine + 2 * PAS)] + lignes[fin_rub:])
    fin_sous = _bloc(lignes, sous[0], fin)
    return "\n".join(lignes[:fin_sous] + [page(racine + 2 * PAS)] + lignes[fin_sous:])
