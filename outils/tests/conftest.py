"""Chargement des outils de construction du site (hooks/videos.py, generer-pdf.py)."""
import importlib.util
import sys
from pathlib import Path

import pytest

RACINE = Path(__file__).resolve().parents[2]


def charger(nom: str, fichier: str):
    spec = importlib.util.spec_from_file_location(nom, RACINE / fichier)
    module = importlib.util.module_from_spec(spec)
    sys.modules[nom] = module          # nécessaire aux dataclasses du module
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def videos():
    return charger("hook_videos", "hooks/videos.py")


@pytest.fixture
def pdf():
    return charger("generer_pdf", "generer-pdf.py")
