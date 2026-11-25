# Guide Ligu'asso — documentation

Deux guides construits depuis une base commune :

- **Associations** — pour les responsables d'association affiliées
- **Fédérations départementales** — pour les gestionnaires et administrateur.rice.s

## Lancer avec Docker

Rédaction du guide associations (rechargement automatique) :

    docker compose up asso

→ http://localhost:8000

Rédaction du guide départemental :

    docker compose up dep

→ http://localhost:8001

Les deux en même temps :

    docker compose up asso dep

Version publiée (sites statiques servis par nginx) :

    docker compose --profile prod up --build prod

→ http://localhost:8080/association/ et http://localhost:8080/departemental/

## Sans Docker

    pip install -r requirements.txt
    ./sync-commun.sh
    mkdocs serve -f mkdocs.association.yml

## Où écrire quoi

| Dossier | Contenu |
|---|---|
| `docs-association/` | Pages du guide associations |
| `docs-departemental/` | Pages du guide départemental |
| `commun/partiels/` | Blocs de texte partagés par les deux guides |
| `commun/img/` | Toutes les captures d'écran |
| `commun/stylesheets/` | Feuille de style |
| `brouillons/` | Pages pas encore publiées |


### Réutiliser un bloc commun

Dans une page, insérez un fichier de `commun/partiels/` :

    --8<-- "parcours-adhesion-ligue.md"

Le bloc est écrit une seule fois et apparaît dans les deux guides.

### Onglets par fédération

    === "Ligue (socioculturel)"

        Contenu Ligue.

    === "UFOLEP"

        Contenu UFOLEP.

### Signaler une limitation

    !!! warning "Limitation connue — septembre 2026"
        Description du problème et contournement.

Reportez-la aussi dans `docs-departemental/limitations.md`, qui les recense toutes.

### Ajouter une vidéo

    <div class="video">
      <iframe src="https://www.youtube-nocookie.com/embed/IDENTIFIANT"
              title="Titre de la vidéo" allowfullscreen></iframe>
    </div>

`youtube-nocookie.com` évite le dépôt de cookies tant que la vidéo n'est pas lancée.

## Notes techniques

- MkDocs 1.6 + Material 9, versions bloquées sous MkDocs 2.0 (incompatible avec Material).
- `sync-commun.sh` recopie `commun/img` et `commun/stylesheets` dans chaque site avant
  construction. Ces copies sont ignorées par Git : la source reste `commun/`.

## Bac à sable `/test`

`docs-test/` est une copie du guide départemental, publiée sur
https://guide-liguasso.laligue.org/test/ pour essayer des modifications
(mise en page, nouvelles pages…) sans toucher aux vrais guides.

- Configuration : `mkdocs.test.yml` (même navigation que le départemental au départ).
- Construit sans `--strict` : un avertissement n'empêche pas la publication,
  et un échec du bac à sable ne bloque jamais les deux vrais guides.
- Non indexé par les moteurs de recherche, mais accessible à qui connaît l'adresse.
- Une fois une modification validée, la reporter à la main dans `docs-departemental/`.
