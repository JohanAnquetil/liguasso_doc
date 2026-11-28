"""Garde-fou de la clean architecture : les dépendances vont vers l'intérieur.

domaine      ← n'importe que la bibliothèque standard
application  ← domaine (+ ses propres ports)
infrastructure, interface, composition ← tout le reste
"""
import ast
from pathlib import Path

import pytest

PAQUET = Path(__file__).resolve().parents[2] / "liguasso_contrib"
TECHNIQUES = {"fastapi", "starlette", "pydantic", "sqlite3", "altcha", "itsdangerous", "urllib", "uvicorn", "httpx", "requests"}


def imports(fichier: Path) -> set[str]:
    """Modules importés : « fastapi », « liguasso_contrib.infrastructure », etc."""
    arbre = ast.parse(fichier.read_text())
    paquet = ".".join(fichier.relative_to(PAQUET.parent).with_suffix("").parts[:-1])
    noms = set()
    for noeud in ast.walk(arbre):
        if isinstance(noeud, ast.Import):
            noms |= {a.name for a in noeud.names}
        elif isinstance(noeud, ast.ImportFrom):
            if noeud.level:   # import relatif -> chemin absolu dans le paquet
                base = paquet.split(".")[: len(paquet.split(".")) - noeud.level + 1]
                noms.add(".".join(base + ([noeud.module] if noeud.module else [])))
            else:
                noms.add(noeud.module)
    return noms


def couche(module: str) -> str | None:
    parties = module.split(".")
    return parties[1] if parties[0] == "liguasso_contrib" and len(parties) > 1 else None


@pytest.mark.parametrize("fichier", sorted((PAQUET / "domaine").glob("*.py")), ids=lambda f: f.name)
def test_le_domaine_ne_depend_de_rien(fichier):
    for module in imports(fichier):
        assert module.split(".")[0] not in TECHNIQUES, f"{fichier.name} importe {module}"
        assert couche(module) in (None, "domaine"), f"{fichier.name} importe {module}"


@pytest.mark.parametrize("fichier", sorted((PAQUET / "application").glob("*.py")), ids=lambda f: f.name)
def test_l_application_ne_depend_que_du_domaine(fichier):
    for module in imports(fichier):
        assert module.split(".")[0] not in TECHNIQUES, f"{fichier.name} importe {module}"
        assert couche(module) in (None, "domaine", "application"), f"{fichier.name} importe {module}"


@pytest.mark.parametrize("fichier", sorted((PAQUET / "infrastructure").glob("*.py")), ids=lambda f: f.name)
def test_l_infrastructure_ne_depend_pas_de_l_interface(fichier):
    for module in imports(fichier):
        assert couche(module) not in ("interface", "application"), f"{fichier.name} importe {module}"


def test_seule_la_composition_assemble_les_couches():
    for fichier in PAQUET.rglob("*.py"):
        if fichier.name in ("composition.py",) or fichier.parent.name == "interface":
            continue
        assert "liguasso_contrib.composition" not in imports(fichier), fichier.name
