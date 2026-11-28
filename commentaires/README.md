# Service de commentaires du guide

Petit service (Python, FastAPI, SQLite) qui ajoute des commentaires en bas de chaque page
des guides. Environ 40 Mo de mémoire.

## Fonctionnement

- **Pseudo seul**, aucune adresse mail demandée.
- **Publication après validation** d'un admin. En attendant, l'auteur·rice voit son
  commentaire marqué « en attente », les autres ne le voient pas.
- **Anti-robot** :
  - [ALTCHA](https://altcha.org) : le navigateur fait un petit calcul (moins d'une seconde),
    sans service tiers ni cookie ; chaque preuve ne sert qu'une fois ;
  - un champ piège invisible : un robot qui le remplit est ignoré sans le savoir ;
  - 5 commentaires au plus par adresse IP toutes les 10 minutes.
- **Likes** (un par visiteur), **réponses** (un niveau), **signalements** avec motif.
  Un commentaire signalé par 3 personnes différentes est masqué en attendant un admin.
- **Données personnelles** : aucune adresse IP stockée en clair, seulement une empreinte
  salée qui sert aux limites anti-abus. Le pseudo et le texte sont publics.

## Modération

https://guide-liguasso.laligue.org/api/commentaires/admin

Onglets **À valider**, **Signalés**, **Publiés**, **Refusés**. Pour chaque commentaire :
publier ou rétablir, refuser, supprimer définitivement, ou **répondre au nom de l'équipe**
(la réponse est publiée sous « Équipe Ligu'asso », avec un badge, et valide le commentaire).

## Réglages (fichier `.env` à la racine du dépôt, sur le serveur)

| Variable | Rôle |
|---|---|
| `ADMIN_MOT_DE_PASSE` | Mot de passe de la page de modération. **Sans lui, la modération est désactivée** et les commentaires restent en attente. |
| `SECRET` | Facultatif. Sinon créé automatiquement et gardé avec les données. |
| `ALTCHA_COUT` | Facultatif. Difficulté du calcul anti-robot (5000 par défaut). |

Les données sont dans le volume Docker `commentaires_donnees` (fichier `commentaires.sqlite3`) :
à inclure dans les sauvegardes du serveur.

## En local

    docker compose up asso dep commentaires

Guides sur http://localhost:8000 et http://localhost:8001, modération sur
http://localhost:8003/api/commentaires/admin (mot de passe `ADMIN_MOT_DE_PASSE` du `.env` local).

Tests :

    pip install -r requirements.txt pytest httpx
    pytest

## Fichiers

- `app.py` : l'API et les règles (anti-robot, limites, signalements).
- `admin.html` : la page de modération.
- `../commun/javascripts/commentaires.js` : le bloc affiché en bas des pages.
- `../commun/javascripts/altcha/` : le widget ALTCHA (licence MIT), repris tel quel.
