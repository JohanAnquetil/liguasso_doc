"""Réglages du service, lus dans les variables d'environnement."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Reglages:
    donnees: Path = Path("/donnees")
    admin_mot_de_passe: str = ""
    secret: str = ""
    cors_origines: list = field(default_factory=list)
    altcha_cout: int = 5000
    github_jeton: str = ""
    github_depot: str = "JohanAnquetil/liguasso_doc"
    github_branche: str = "main"
    github_api: str = "https://api.github.com"
    site_public: str = "https://guide-liguasso.laligue.org"
    limites_relachees: bool = False   # tests e2e uniquement : toutes les requêtes viennent de la même IP

    @classmethod
    def depuis_environnement(cls) -> "Reglages":
        e = os.environ.get
        return cls(
            donnees=Path(e("DONNEES", "/donnees")),
            admin_mot_de_passe=e("ADMIN_MOT_DE_PASSE", ""),
            secret=e("SECRET", ""),
            cors_origines=e("CORS_ORIGINES", "").replace(",", " ").split(),
            altcha_cout=int(e("ALTCHA_COUT", "5000")),
            github_jeton=e("GITHUB_TOKEN", ""),
            github_depot=e("GITHUB_DEPOT", "JohanAnquetil/liguasso_doc"),
            github_branche=e("GITHUB_BRANCHE", "main"),
            github_api=e("GITHUB_API", "https://api.github.com"),
            site_public=e("SITE_PUBLIC", "https://guide-liguasso.laligue.org"),
            limites_relachees=e("LIMITES_RELACHEES", "") == "1",
        )
