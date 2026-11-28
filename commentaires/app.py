"""Point d'entrée du service (uvicorn app:app). Le code est dans liguasso_contrib/."""
from liguasso_contrib.composition import creer_app

app = creer_app()
