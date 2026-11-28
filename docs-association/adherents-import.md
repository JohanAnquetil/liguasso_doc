# Importer un fichier d'adhésions

!!! chemin "Accès"
    Dans le menu, cliquez sur **Adhésion**, puis sur **Importer des adhésions**.

L'import permet de créer ou de renouveler de nombreuses adhésions en une seule fois, à partir d'un fichier Excel (`.xls`, `.xlsx`) ou CSV (`.csv`). Les adhésions importées sont transmises directement à votre fédération départementale, qui les valide.

## Avant de commencer

- Votre association doit être **affiliée et validée pour la saison**.
- Préparez un fichier avec les colonnes obligatoires (voir l'onglet qui vous concerne) et **300 lignes au maximum**.
- Pour des élèves USEP, paramétrez d'abord vos écoles et vos classes dans [Sections et écoles](association-sections.md).

## Importer le fichier

=== "Adhérents et licenciés"

    **Étape 1.** Choisissez la **Saison**, la **Catégorie d'adhérents** (**Adhérents Socioculturels** ou **Licenciés Ufolep**), vérifiez l'**Association** et indiquez la **Date de validation**. Cliquez sur **suivant**.

    ![Étape 1](img/import-etape1.png)

    **Étape 2.** Sélectionnez l'activité attribuée à **tous** les adhérents du fichier. Si vos adhérents pratiquent des activités différentes, faites un fichier par activité.

    ![Étape 2](img/import-etape2.png)

    **Étape 3.** Sélectionnez le fichier sur votre ordinateur.

    --8<-- "colonnes-import-adherents.md"

    ![Étape 3](img/import-etape3.png)

    **Étape 4.** Associez chaque colonne de votre fichier au champ correspondant de Ligu'asso, si la correspondance n'a pas été faite automatiquement.

    ![Étape 4](img/import-etape4.png)

    **Étape 5.** Si des anomalies sont détectées, par exemple un sexe non reconnu, corrigez-les avant de continuer. Cette étape n'apparaît que s'il y a des erreurs.

    **Étape 6.** Vérifiez le récapitulatif et cliquez sur **Importer les données**.

    ![Étape 6](img/import-etape6.png)

    Un message confirme la fin de l'import.

    ![Import terminé](img/import-termine.png)

=== "Élèves (USEP)"

    !!! tip "À faire avant"
        Vérifiez vos écoles, classes, niveaux et enseignants dans [Sections et écoles](association-sections.md). L'import se fait **par classe** : préparez un fichier par classe.

    **Étape 1.** Choisissez la **Saison**, la **Catégorie d'adhérents** **Licenciés Usep Enfant** et la **Date de validation**. Cliquez sur **suivant**.

    **Étape 2.** Sélectionnez l'école et la classe des élèves du fichier.

    ![Étape 2 — choix de la classe](img/eleves-etape2.png)

    **Étape 3.** Sélectionnez le fichier sur votre ordinateur.

    --8<-- "colonnes-import-eleves.md"

    ![Étape 3](img/eleves-etape3.png)

    **Étape 4.** Associez les colonnes du fichier aux champs de Ligu'asso, si la correspondance n'est pas automatique.

    **Étape 5.** Corrigez les anomalies détectées : chaque ligne en erreur est signalée, avec le champ à corriger.

    ![Étape 5 — correction des anomalies](img/eleves-etape5.png)

    **Étape 6.** Confirmez l'import.

    ![Étape 6](img/eleves-etape6.png)

## Après l'import

Chaque fichier importé crée un **lot**. Les adhésions importées ne s'affichent pas dans **Gérer les adhésions** : retrouvez-les dans [Lots](adherents-lots.md), avec le nombre d'adhésions transmises, validées et refusées.

## Voir aussi

- [Enregistrer une adhésion](adherents-nouveau.md) : pour une seule personne.
- [Ça ne marche pas comme prévu](probleme.md)
