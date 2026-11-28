# Importer un fichier d'adhésions

!!! chemin "Accès"
    Dans le menu, cliquez sur **Adhésion**, puis sur **Importer des adhésions**.

L'import crée ou renouvelle de nombreuses adhésions d'une association en une seule fois, à partir d'un fichier Excel (`.xls`, `.xlsx`) ou CSV (`.csv`). Chaque fichier importé crée un **lot**.

![type:video](https://www.youtube-nocookie.com/embed/lMVnP_gSw5U)

![Menu Importer des adhésions](img/dep-import-menu.png)

## Avant de commencer

- L'association doit être **affiliée et validée pour la saison**.
- Préparez un fichier avec les colonnes obligatoires et **300 lignes au maximum**.
- Pour des élèves USEP, vérifiez d'abord les écoles et les classes de l'association dans [Sections et écoles](affiliations-annexes.md).

## Importer le fichier

=== "Adhérents et licenciés"

    **Étape 1.** Choisissez la **Saison**, la **Catégorie d'adhérents** (**Adhérents Socioculturels**, **Licenciés Ufolep**, **Adhérents Ufopass** ou **Participants Tipo**), **l'Association** concernée et la **Date de validation**. Cliquez sur **suivant**.

    ![Étape 1](img/dep-import-etape1.png)

    **Étape 2.** Sélectionnez l'activité attribuée à **tous** les adhérents du fichier. Si les adhérents pratiquent des activités différentes, faites un fichier par activité.

    **Étape 3.** Sélectionnez le fichier sur votre ordinateur.

    --8<-- "colonnes-import-adherents.md"

    ![Étape 3](img/dep-import-etape3.png)

    **Étape 4.** Associez chaque colonne du fichier au champ correspondant de Ligu'asso, si la correspondance n'a pas été faite automatiquement.

    ![Étape 4](img/dep-import-etape4.png)

    **Étape 5.** Cette étape n'apparaît que si des erreurs sont détectées. Pour chaque ligne en erreur, vous pouvez :

    - **décocher la ligne** pour l'exclure de l'import ;
    - ou **corriger la valeur** directement. Par exemple, si le sexe d'un adhérent n'a pas été reconnu, choisissez-le dans la liste déroulante de la ligne.

    ![Erreurs détectées](img/dep-import-erreurs.png)

    ![Correction manuelle](img/dep-import-correction.png)

    **Étape 6.** Vérifiez le récapitulatif et cliquez sur **Importer les données**.

    ![Étape 6](img/dep-import-etape6.png)

    ![Import terminé](img/dep-import-termine.png)

=== "Élèves (USEP)"

    !!! tip "À faire avant"
        Vérifiez les classes, niveaux et enseignants de l'association dans [Sections et écoles](affiliations-annexes.md). L'import se fait **par classe** : préparez un fichier par classe.

    **Étape 1.** Choisissez la **Saison**, la **Catégorie d'adhérents**, l'**Association** et la **Date de validation**. Cliquez sur **suivant**.

    **Étape 2.** Sélectionnez l'école et la classe des élèves du fichier.

    **Étape 3.** Sélectionnez le fichier sur votre ordinateur.

    --8<-- "colonnes-import-eleves.md"

    **Étape 4.** Associez les colonnes du fichier aux champs de Ligu'asso, si la correspondance n'est pas automatique.

    **Étape 5.** Corrigez ou excluez les lignes en erreur.

    **Étape 6.** Confirmez l'import.

## Après l'import

Les adhésions importées ne s'affichent pas dans **Gérer les adhésions** : retrouvez-les et validez-les dans [Lots](adhesions-lots.md).
