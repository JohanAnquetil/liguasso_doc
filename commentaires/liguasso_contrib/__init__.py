"""Contributions au guide Ligu'asso : commentaires et propositions de modification.

Organisation (clean architecture, les dépendances vont vers l'intérieur) :

- domaine/         règles métier pures, sans dépendance technique
- application/     cas d'usage et ports (interfaces) dont ils ont besoin
- infrastructure/  adaptateurs : SQLite, ALTCHA, GitHub, sécurité
- interface/       API HTTP (FastAPI) et page de modération
- composition.py   assemble le tout à partir des réglages
"""
