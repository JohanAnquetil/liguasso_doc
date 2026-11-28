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

Avec les commentaires (modération sur http://localhost:8003/api/commentaires/admin) :

    docker compose up asso dep commentaires

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
| `accueil/` | Page d'accueil à la racine du site (choix du guide), HTML simple |


### Réutiliser un bloc commun

Dans une page, insérez un fichier de `commun/partiels/` :

    --8<-- "parcours-adhesion-ligue.md"

Le bloc est écrit une seule fois et apparaît dans les deux guides.

### Onglets par fédération

    === "Ligue (socioculturel)"

        Contenu Ligue.

    === "UFOLEP"

        Contenu UFOLEP.

### Indiquer le chemin d'accès

Chaque page commence, juste sous le titre, par un encadré « Accès » qui donne le chemin
dans le menu de Ligu'asso. Recopiez les intitulés **exactement** comme dans l'application :

    !!! chemin "Accès"
        Dans le menu, cliquez sur **Adhésion**, puis sur **Lots**, puis sur le bouton **Nouveau lot**.

Plusieurs écrans sur la même page :

    !!! chemin "Accès"
        - Sections : dans le menu, cliquez sur **Affiliation**, puis sur **Gérer les sections**.
        - Écoles : dans le menu, cliquez sur **Affiliation**, puis sur **Gérer les écoles**.

Le test lit les intitulés en gras après « dans le menu », jusqu'au mot « bouton » : gardez cette formule.
Sans passer par le menu : `Depuis le **tableau de bord** (logo central), cliquez sur le bouton **Modifier votre affiliation**.`
Seules les pages d'accueil et d'aide (`index`, `probleme`, `limitations`, `connexion`, `glossaire`, `videos`) n'en ont pas.

### Éditeur visuel des propositions

Le bouton **Modifier** ouvre la fiche dans un éditeur visuel (`commun/javascripts/editeur-fiche.js`),
sans Markdown à l'écran : les textes (titres, paragraphes, listes, encadrés, onglets) se modifient
directement, avec gras, italique et lien ; « + Ajouter » insère un paragraphe, un sous-titre, une
liste ou un encadré. Les éléments techniques (encadré « Accès », vidéos, captures, blocs communs,
mises en page HTML, tableaux) sont verrouillés ; une capture peut être retirée. Un **mode avancé**
donne accès au Markdown brut.

Les blocs non modifiés sont réécrits à l'identique : la proposition ne contient que les vrais
changements. Le test `npm run test:editeur` (dans `verification/`) le vérifie sur toutes les fiches.

### Tests de bout en bout (Playwright)

`verification/e2e` rejoue les parcours dans un vrai navigateur, sur les guides lancés en
local : encadrés « Accès », bouton PDF, version imprimée, commentaires (envoi, validation,
like, réponse, signalement, champ piège), modération, propositions de modification jusqu'à
la pull request (sur un faux GitHub). Playwright démarre lui-même les guides, le service de
commentaires et le faux GitHub.

    cd verification
    npm install && npx playwright install chromium            # la première fois
    PYTHON=python3 npm run test:e2e                           # python avec mkdocs et commentaires/requirements.txt
    npm run rapport:e2e

Organisation : `e2e/pages/` (une classe par écran : page du guide, bloc commentaires,
fenêtre de proposition, modération), `e2e/support/` (fixtures, faux GitHub), `e2e/specs/`
(les scénarios). Ces tests et ceux du service tournent sur chaque pull request
(`.github/workflows/tests.yml`).

### Vérifier les chemins sur la recette (Playwright)

Le dossier `verification/` relit tous les encadrés « Accès » et vérifie sur
http://recette.liguasso.org que chaque entrée existe dans le menu et que l'écran s'ouvre.
Il signale aussi une page qui n'a pas d'encadré.

    cd verification
    npm install && npx playwright install chromium   # la première fois
    login_tests_liguasso npm run test:recette         # identifiants via LOGIN et MDP
    npm run rapport:recette                           # rapport HTML, captures en cas d'échec

Profils utilisés par défaut : `Président.e|AL La Guerche` (guide associations) et
`Gestionnaire départemental.e|Puy de Dôme` (guide départemental). Pour en changer :
`PROFIL_ASSO="Gestionnaire de l'association|Chevaux fringants"`, `PROFIL_DEP="…"`.

### Bouton « PDF »

Chaque page a un bouton **PDF** à droite du titre. Sur le site publié, il télécharge le PDF
de la page, préparé à chaque mise en ligne par `generer-pdf.py` (Chromium, dans une étape
Docker à part, `pdf`, qui n'alourdit pas l'image de rédaction) : entête reprise
de la couverture du guide PDF complet, onglets Ligue / UFOLEP / USEP tous affichés, chapitre
et numéros de page en bas, logos des fédérations. Le PDF est identique quel que soit le
navigateur de la personne.

- En rédaction locale (`docker compose up asso dep`), les PDF n'existent pas : le bouton
  ouvre l'impression du navigateur, avec la même mise en page (« Enregistrer en PDF »).
- Mise en page : `commun/stylesheets/extra.css` (`@media print`) et `commun/javascripts/impression.js`.
- Logos : `commun/img/logos/` (fichiers officiels de l'application).
- Si la création des PDF échoue, le site est publié quand même et le bouton revient à l'impression.

Tester la création des PDF sans Docker :

    pip install playwright && playwright install chromium
    mkdocs build -f mkdocs.departemental.yml
    python generer-pdf.py site/departemental     # crée site/departemental/<page>/page.pdf

### Commentaires

Chaque page se termine par des commentaires (pseudo seul, anti-robot, publication après
validation). Service, modération et réglages : voir [`commentaires/README.md`](commentaires/README.md).
Sur le serveur, définir `ADMIN_MOT_DE_PASSE` dans le `.env` pour activer la modération.

### Signaler une limitation

    !!! warning "Limitation connue — septembre 2026"
        Description du problème et contournement.

Reportez-la aussi dans `docs-departemental/limitations.md`, qui les recense toutes.

### Ajouter un tuto vidéo

Dans la fiche concernée, à l'endroit voulu :

    !!! video "Importer un fichier de demandes de licence"
        https://www.youtube-nocookie.com/embed/lMVnP_gSw5U · 7 min
        Choisir la saison et le type de licence, déposer le fichier CSV, puis vérifier l'import.

1re ligne : l'adresse YouTube (`youtube-nocookie.com/embed/…`, `watch?v=…` ou `youtu.be/…`) et
la durée ; lignes suivantes (facultatif) : ce qu'on apprend dans la vidéo.

La vidéo apparaît alors automatiquement (`hooks/videos.py`, `commun/javascripts/videos.js`) :
en carte dans la fiche, avec un ▶ dans le menu, dans le bloc « En vidéo » de l'accueil
(`<!-- videos:accueil -->`) et dans la page « Tutos vidéo » (`<!-- videos:toutes -->`).
YouTube (`youtube-nocookie`) ne se charge qu'au clic. Pour une image d'aperçu servie par le
guide (aucune requête vers Google avant le clic), ajoutez `commun/img/videos/<identifiant>.jpg` ;
sinon celle de YouTube est utilisée.

## Notes techniques

- MkDocs 1.6 + Material 9, versions bloquées sous MkDocs 2.0 (incompatible avec Material).
- `sync-commun.sh` recopie `commun/img` et `commun/stylesheets` dans chaque site avant
  construction. Ces copies sont ignorées par Git : la source reste `commun/`.

## Bac à sable `/test`

Aperçu en local, avec rechargement automatique :

    docker compose up test

→ http://localhost:8002


`docs-test/` est une copie du guide départemental, publiée sur
https://guide-liguasso.laligue.org/test/ pour essayer des modifications
(mise en page, nouvelles pages…) sans toucher aux vrais guides.

- Configuration : `mkdocs.test.yml` (même navigation que le départemental au départ).
- Construit sans `--strict` : un avertissement n'empêche pas la publication,
  et un échec du bac à sable ne bloque jamais les deux vrais guides.
- Non indexé par les moteurs de recherche, mais accessible à qui connaît l'adresse.
- Styles à essayer uniquement sur `/test` : `docs-test/test.css`.
  Mise en page (en-tête, pied de page…) : `overrides-test/`.
- Une fois une modification validée, la reporter à la main dans `docs-departemental/`
  (et les styles dans `commun/stylesheets/extra.css`). Pour voir les écarts :

      diff -r -x img -x stylesheets -x test.css docs-departemental docs-test

- Repartir de zéro (pages, menu et `test.css` remis comme le départemental,
  le bandeau est conservé) :

      ./reset-test.sh

**Attention** : `mkdocs.base.yml`, `commun/stylesheets/`, `commun/img/` et
`commun/partiels/` sont partagés. Les modifier change aussi les vrais guides.
