# Charte de rédaction des fiches

Les fiches sont lues par deux publics : les **utilisateurs** de Ligu'asso (bénévoles d'association,
gestionnaires de fédération) et le **chatbot**, qui découpe chaque fiche en passages autonomes
(un par titre `##` ou `###`) et répond à partir de ces seuls passages. Une fiche claire pour l'un
l'est pour l'autre.

## Ton et langue

- On s'adresse au lecteur : « vous ». Les étapes sont à l'impératif : « Cliquez sur… ».
- Phrases courtes, une idée par phrase. Pas de jargon sans explication : sinon, renvoyer au
  [glossaire](commun/partiels/glossaire.md).
- **Pas d'écriture inclusive** : masculin générique (« les adhérents », « le président »,
  « le correspondant », « les gestionnaires départementaux »).
- Orthographe : « réaffiliation », « réadhésion » (sans trait d'union) dans le texte courant.
  Les noms d'écran et de bouton s'écrivent **exactement comme dans Ligu'asso**, même s'ils
  diffèrent : **Campagne de ré-affiliation**, **Campagne de ré-adhésion**.
- Fédérations : « Ligue (socioculturel) », « UFOLEP », « USEP ». Dans le texte courant :
  « le secteur socioculturel de la Ligue ».

## Libellés de l'application

- Tout ce qui est écrit à l'écran (menu, bouton, champ, onglet, valeur de liste) est en **gras**
  et recopié à l'identique, majuscules comprises. Vérifier sur la recette en cas de doute.
- Un bouton sans texte est décrit par son icône et sa place : « l'icône en forme d'œil, dans la
  colonne **Actions** ».

## Structure d'une fiche

```
# Verbe + objet (« Importer un fichier d'adhésions »)

!!! chemin "Accès"
    Dans le menu, cliquez sur **…**, puis sur **…**.

Une ou deux phrases : à quoi sert l'écran, pour qui.

## Avant de commencer        (si des conditions s'appliquent)
## <Tâche 1, avec un verbe>  (étapes numérotées)
## <Tâche 2>
## À savoir                  (règles, limites, cas particuliers)
## Voir aussi                (liens vers les fiches liées)
```

- **Un titre `##` = une tâche ou une question**, formulé pour être compris seul :
  « Valider les adhésions d'un lot », pas « Valider ». Le chatbot affiche ces titres comme sources.
- Le chemin d'accès est dans l'encadré « Accès » et **n'est pas répété** dans le texte.
- Étapes numérotées, une action par étape, avec le résultat attendu quand il n'est pas évident.
- Les règles importantes (champs obligatoires, conditions, limites) sont écrites **en toutes
  lettres**, pas seulement montrées sur une capture.

## Captures d'écran

- Une capture illustre le texte ; elle ne le remplace jamais. Le chatbot ne voit pas les images.
- Interdit : « comme ci-dessous », « voir la capture ». Écrire ce que la capture montre :
  « Si le sexe n'a pas été reconnu, la ligne apparaît en rouge : choisissez-le dans la liste ».
- Texte alternatif court et descriptif : `![Formulaire Nouvelle campagne](img/…)`.

## Encadrés

| Encadré | Usage |
|---|---|
| `!!! chemin "Accès"` | Chemin dans le menu, en tête de fiche (obligatoire) |
| `!!! warning` | Erreur fréquente ou action irréversible |
| `!!! tip` | Astuce qui fait gagner du temps |
| `!!! note` | Précision utile, sans risque |
| `!!! video "Titre"` | Tuto vidéo : adresse YouTube et durée, puis ce qu'on y apprend (voir README) |
| `!!! warning "Limitation connue — <mois année>"` | Défaut de la plateforme et contournement, aussi reporté dans `limitations.md` |

## Pages « Ça ne marche pas comme prévu »

Chaque entrée est titrée par la phrase qu'un utilisateur dirait : `## « Je ne retrouve pas… »`.
Réponse courte, puis un lien vers la fiche détaillée. C'est le format qui aide le plus le chatbot.
