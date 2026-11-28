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
Seules les pages d'accueil et d'aide (`index`, `probleme`, `limitations`, `connexion`) n'en ont pas.

### Vérifier les chemins sur la recette (Playwright)

Le dossier `verification/` relit tous les encadrés « Accès » et vérifie sur
http://recette.liguasso.org que chaque entrée existe dans le menu et que l'écran s'ouvre.
Il signale aussi une page qui n'a pas d'encadré.

    cd verification
    npm install && npx playwright install chromium   # la première fois
    login_tests_liguasso npm test                     # identifiants via LOGIN et MDP
    npm run rapport                                   # rapport HTML, captures en cas d'échec

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
