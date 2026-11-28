# Extraire les adhérents et les associations

!!! chemin "Accès"
    - Adhérents : dans le menu, cliquez sur **Statistiques et Extractions**, puis sur **Extractions**, puis sur **Extraction adhérents**.
    - Associations : dans le menu, cliquez sur **Statistiques et Extractions**, puis sur **Extractions**, puis sur **Extraction associations**.

Les extractions produisent un fichier Excel des adhérents ou des associations de votre département, filtrés selon vos critères.

![Menu Statistiques et extractions](img/dep-statistiques-menu.png)

## Extraire les adhérents

Seule la **Saison** est obligatoire ; plus vous renseignez de critères, plus l'extraction est ciblée.

### Choisir la saison et le périmètre

Dans le bloc **Paramètres**, choisissez la **Saison**. Le **Département** est déjà rempli. Pour limiter l'extraction à une association, choisissez-la dans **Association** ; pour la limiter à une fédération, choisissez **Ligue**, **Ufolep** ou **Usep** dans **Structure**.

![Paramètres de l'extraction](img/dep-extraction-parametres.png)

### Filtrer les adhérents

Tous les filtres sont facultatifs :

- **Activité / Dispositif fédéral** ;
- **Catégorie d'adhérent** : **Adhérents Socioculturels**, **Licenciés Usep**, **Licenciés Ufolep**, **Adhérents Ufopass** ;
- **Etat adhésion** : **A réadhérer**, **En cours**, **Validée**, **Refusée**, **Rejetée** ;
- **Sexe** et **Tranche d'âge** (par exemple **Jeune - Ligue**, **Adulte - Ufolep**, **Enfant - Usep**) ;
- les interrupteurs **Loisirs**, **Compétitions**, **Officiels**, **Animateurs** et **Dirigeants**, pour ne garder que les adhérents concernés.

Pour l'**USEP**, trois filtres propres au milieu scolaire s'ajoutent : **Ecole** (maternelle ou élémentaire), **Cycle** (**Cycle 1** à **Cycle 3**, **Hors cycle**) et **Niveau** (de la petite section au CM2).

Les [champs supplémentaires](parametrage-champs.md) de votre fédération apparaissent aussi comme filtres, par exemple **Diffusion** ou **Secteur Usep pour rencontres sportives**.

![Filtres](img/dep-extraction-filtres.png)

### Choisir le type de sortie

Le **Type de sortie** détermine le contenu du fichier :

=== "Ligue"

    **Sortie simple Ligue** : une liste rapide des adhérents de la Ligue. Pour chaque personne : département, association, activité, numéro d'adhérent, civilité, nom, prénom, date de naissance et âge.

=== "UFOLEP"

    **Sortie simple Ufolep** : la liste des licenciés UFOLEP par activité. Le fichier indique si l'activité est l'activité principale, le type de licence, l'identité, l'âge et la tranche d'âge, la date d'homologation, les fonctions exercées (pratiquant, animateur, dirigeant, officiel) et la colonne **Risque**.

    **Sortie complète Ufolep** : toutes les informations de l'adhésion. État civil détaillé (lieu de naissance, nom des parents), coordonnées, date d'adhésion, informations de licence (catégorie, désignation, homologation, certificat médical, impression), fonctions exercées, contrôle d'honorabilité, doubles adhésions, informations UFOPASS, MARSH et CASM.

=== "USEP"

    **Sortie simple Usep** : la liste des licenciés USEP rattachés à leur école. Pour chaque personne : association, identité, date de naissance, âge, école, classe et niveau.

    **Sortie complète Usep** : toutes les informations de l'adhésion. Numéro de licence, état civil, coordonnées, date d'adhésion, type de licence, école, classe et niveau. Une éventuelle double adhésion USEP est signalée.

Toutes les sorties se terminent par la colonne **Motif rejet**.

![Type de sortie](img/dep-extraction-sortie.png)

Cliquez enfin sur **Extraire les données**. Le bouton **Télécharger** permet de récupérer le fichier.

## Extraire les associations

1. Choisissez la **Saison** et le **Type de sortie** (**Ligue**, **Ufolep** ou **Usep**) : ce sont les deux seuls champs obligatoires.
2. Affinez si besoin avec : **Structure**, **Statut juridique** (par exemple **1100 - Association loi 1901**), **Activité / Dispositif fédéral**, **Type d'affiliation UFOLEP**, et vos champs supplémentaires (**Diffusion**…).
3. Cliquez sur **Extraire les données**.

![Extraction des associations](img/dep-extraction-associations.png)
