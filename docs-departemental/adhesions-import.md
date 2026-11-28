# Importer un fichier d'adhésions

!!! chemin "Accès"
    **Adhésion** › **Importer des adhésions**

![type:video](https://www.youtube-nocookie.com/embed/lMVnP_gSw5U)

Pour créer ou renouveler un grand nombre d'adhésions en une seule fois, utilisez **Adhésion > Importer des adhésions**.

![Menu Importer des adhésions](img/dep-import-menu.png)

=== "Adhérents et licenciés"

    **Étape 1.** Définissez la saison, le type d'adhésion ou de licence, la date de validation et **l'association concernée**.

    ![Étape 1](img/dep-import-etape1.png)

    **Étape 2.** Sélectionnez l'activité attribuée à tous les adhérent.e.s du fichier.

    **Étape 3.** Sélectionnez le fichier, au format Excel ou CSV.

    --8<-- "colonnes-import-adherents.md"

    ![Étape 3](img/dep-import-etape3.png)

    **Étape 4.** Faites correspondre les colonnes de votre fichier avec les champs de Ligu'asso, si la correspondance n'est pas automatique.

    ![Étape 4](img/dep-import-etape4.png)

    **Étape 5.** Cette étape n'apparaît que si des erreurs ont été détectées. Vous pouvez décocher les lignes erronées pour les exclure de l'import, ou corriger l'erreur manuellement.

    ![Erreurs détectées](img/dep-import-erreurs.png)

    Dans l'exemple ci-dessous, le sexe n'a pas été détecté : on le corrige avec le menu déroulant.

    ![Correction manuelle](img/dep-import-correction.png)

    **Étape 6.** Confirmez en cliquant sur **Importer les données**.

    ![Étape 6](img/dep-import-etape6.png)

    ![Import terminé](img/dep-import-termine.png)

=== "Élèves (USEP)"

    !!! tip "À faire avant"
        Vérifiez et paramétrez les classes, niveaux et enseignant.e.s rattachés dans [Sections et écoles](affiliations-annexes.md). L'import se fait **par classe** : préparez autant de fichiers que de classes.

    **Étape 1.** Définissez la saison, le type d'adhésion ou de licence et la date de validation.

    **Étape 2.** Sélectionnez l'école et la classe des enfants concernés.

    **Étape 3.** Sélectionnez le fichier, au format Excel ou CSV.

    --8<-- "colonnes-import-eleves.md"

    **Étape 4.** Faites correspondre les colonnes, si la correspondance n'est pas automatique.

    **Étape 5.** Corrigez les anomalies détectées avant le transfert.

    **Étape 6.** Confirmez l'import.

L'historique des fichiers importés est disponible dans [Lots](adhesions-lots.md).
