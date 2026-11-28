# Suivre et valider les lots d'adhésions

!!! chemin "Accès"
    Dans le menu, cliquez sur **Adhésion**, puis sur **Lots**.

Un **lot** est un ensemble d'adhésions traitées ensemble. Il est créé automatiquement à chaque **import de fichier** (`.xls`, `.xlsx` ou `.csv`), et vous pouvez en créer un vous-même pour [valider des adhésions en masse](adhesions-valider.md).

Les adhésions importées ne s'affichent pas dans **Gérer les adhésions** : c'est ici qu'on les retrouve et qu'on les valide.

![Liste des lots](img/dep-lots.png)

## Lire la liste des lots

Pour chaque lot, le tableau indique son **ID**, son **Libellé**, l'**Association**, le nombre d'adhésions (**Nb adhes.**, **Nb adhes. validées**, **Nb adhes. refusées**), et les dates et auteurs de création (**Créé le**), de transfert (**Transfert le**) et de validation (**Validé le**).

Par défaut, seuls les lots en cours sont affichés. Cochez **Afficher l'historique des lots validés** pour voir aussi les lots déjà validés.

![Lots](img/dep-lots-liste.png)

La colonne **Actions** propose trois icônes : **Visualiser** (œil), **Supprimer** et **Valider**.

## Valider les adhésions d'un lot

Quel que soit leur état, les adhésions d'un lot se valident depuis cet écran.

1. Cliquez sur l'icône **Visualiser**, en forme d'œil : la liste des adhésions du lot s'affiche.
2. Choisissez ce que vous validez :

=== "Une partie du lot"

    Cochez les adhésions concernées, puis cliquez sur **Valider les éléments sélectionnés**.

    ![Valider une sélection](img/dep-lot-valider.png)

=== "Tout le lot"

    Cliquez sur **Tout sélectionner**, en haut à gauche, puis sur **Tout valider**.

![Adhésions d'un lot](img/dep-lot-adhesions.png)

Un message confirme la validation.

![Message de validation](img/dep-lot-message.png)

Les adhésions validées sont marquées comme telles dans le lot, qui garde l'historique complet.

![Lot validé](img/dep-lot-valide.png)

Une fois validées, elles sont aussi visibles dans **Gérer les adhésions**, en recherchant l'association concernée.

![Retrouver les adhésions](img/dep-lot-retrouver.png)

## Voir aussi

- [Valider des adhésions en masse](adhesions-valider.md)
- [Importer un fichier d'adhésions](adhesions-import.md)
