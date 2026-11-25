# Statistiques et extractions

Le menu **Statistiques et extractions** permet d'extraire la liste des adhérent.e.s ou des associations de votre département, selon les critères de votre choix.

![Menu Statistiques et extractions](img/dep-statistiques-menu.png)

## Extraire les adhérent.e.s

Tous les paramètres sont facultatifs, **sauf la saison** : plus vous en renseignez, plus l'extraction est ciblée.

### Choisir la saison et le périmètre

Dans le bloc **Paramètres**, choisissez la **saison** concernée. Le champ **Département** est prérempli avec le vôtre. Pour limiter l'extraction à une association, sélectionnez-la dans le champ **Association** ; pour la limiter à un type de structure, sélectionnez-le dans la liste **Structures**.

![Paramètres de l'extraction](img/dep-extraction-parametres.png)

### Filtrer

Vous pouvez affiner à l'aide des filtres : **Activité / Dispositif fédéral**, **Catégorie d'adhérent**, **État adhésion**, **Sexe** et **Tranche d'âge**.

Les options **Loisirs**, **Compétitions**, **Officiels**, **Animateurs** et **Dirigeants** ne retiennent que les adhérent.e.s concernés — cliquez sur l'interrupteur pour l'activer.

![Filtres](img/dep-extraction-filtres.png)

Pour les adhérent.e.s **USEP**, des filtres propres au milieu scolaire s'ajoutent : **École**, **Cycle** et **Niveau**. Le champ **Secteur USEP pour rencontres sportives** cible les adhérent.e.s d'un secteur donné, et le champ **Diffusion** permet un filtrage supplémentaire.

### Choisir le type de sortie

Le champ **Type de sortie** détermine le contenu du fichier extrait. Cinq sorties sont proposées.

=== "Ligue"

    **Sortie simple Ligue** — une liste rapide des adhérent.e.s Ligue. Pour chaque personne : son département, son association, son activité, son numéro d'adhérent, sa civilité, son nom, son prénom, sa date de naissance et son âge.

=== "UFOLEP"

    **Sortie simple Ufolep** — une liste des adhérent.e.s UFOLEP par activité. Le fichier précise si l'activité est l'activité principale, et donne le type de licence, l'identité, l'âge et la tranche d'âge. On y trouve aussi la date d'homologation, les fonctions exercées — pratiquant, animateur, dirigeant, officiel — et la colonne **Risque**.

    **Sortie complète Ufolep** — l'ensemble des informations de l'adhésion : état civil détaillé (lieu de naissance, nom des parents), coordonnées, date d'adhésion, informations de licence (catégorie, désignation, homologation, certificat médical, impression), fonctions exercées, contrôle d'honorabilité, doubles adhésions, ainsi que les informations Ufopass, MARSH et CASM.

=== "USEP"

    **Sortie simple Usep** — une liste des adhérent.e.s USEP rattachés à leur école. Pour chaque personne : son association, son identité, sa date de naissance, son âge, son école, sa classe et son niveau.

    **Sortie complète Usep** — l'ensemble des informations de l'adhésion : numéro de licence, état civil, coordonnées, date d'adhésion, type de licence, école, classe et niveau. Une éventuelle double adhésion USEP y est signalée.

!!! note
    Toutes les sorties se terminent par la colonne **Motif rejet**.

Cliquez enfin sur **Extraire les données**.

![Type de sortie](img/dep-extraction-sortie.png)

## Extraire les associations

Pour extraire la liste des associations de votre département, seuls la **saison** et le **type de sortie** doivent être renseignés. Les autres paramètres sont facultatifs et permettent de cibler l'extraction.

![Extraction des associations](img/dep-extraction-associations.png)

Choisissez le type de sortie, puis cliquez sur **Extraire les données**.
