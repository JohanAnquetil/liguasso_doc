# Facturer les associations et enregistrer les règlements

!!! chemin "Accès"
    Dans le menu, cliquez sur **Facturation**, puis sur **Facturation et règlement**.

L'écran **Facturation et règlement** regroupe les factures des associations de votre département et le suivi de leur paiement. En haut de l'écran, deux boutons permettent de créer une **facture vierge** ou d'enregistrer un **règlement**.

![Menu Facturation](img/dep-facturation-menu.png)

## Rechercher des factures

1. Dans le bloc **Recherche**, choisissez la **Comptabilité** : LIGUE, UFOLEP ou USEP.
2. Affinez si besoin :
    - **Association**, pour n'afficher que ses factures ;
    - **Statut** : **Tous**, **À jour**, **À facturer** ou **À rembourser** ;
    - **Type d'association** : **Toutes**, **Socio-Culturelles**, **Ufolep** ou **Usep** ;
    - **N° de pièce**, pour retrouver une facture ou un règlement précis.
3. Cliquez sur **Rechercher**.

![Résultats de la recherche](img/dep-facturation-recherche.png)

## Préfacturer une association

Une **préfacture** est une facture préparée, déjà remplie avec les produits à facturer à l'association. Vous la vérifiez avant de la valider.

1. Dans la colonne **Actions** de l'association, cliquez sur l'icône en forme de **caddie**.

    ![Icône caddie](img/dep-facturation-caddie.png)

2. Le formulaire reprend les informations de l'association. Complétez l'**adresse de facturation** et vérifiez l'**adresse mail d'envoi**.
3. Vérifiez les produits : vous pouvez modifier les quantités, supprimer une ligne ou ajouter un produit avec le champ **Produit à ajouter**.
4. Cliquez sur **Prévisualiser la facture** pour la contrôler, puis sur **Valider la facture**.

![Formulaire de facture](img/dep-facturation-formulaire.png)

!!! note "Compte tiers manquant"
    Pour facturer une association dans une comptabilité, elle doit y avoir un **compte tiers**. S'il manque, un message le signale dans la fenêtre **Sélectionner l'association** : cliquez sur **Oui** pour le créer. Le formulaire de facture s'ouvre ensuite.

    ![Création d'un compte tiers](img/dep-facturation-comptetiers.png)

## Consulter les factures d'une association et créer un avoir

1. Cliquez sur l'icône en forme d'**œil** en face de l'association : la liste de ses factures s'affiche.

    ![Liste des factures](img/dep-facturation-liste.png)

2. Pour chaque facture, les icônes permettent de **Voir la facture**, l'**Envoyer par mail**, créer un **Avoir** (icône €) pour l'annuler en tout ou partie, et l'**Imprimer**.

    ![Actions sur une facture](img/dep-facturation-actions.png)

3. Une **préfacture** se transforme en facture en cliquant sur son icône **caddie**.

    ![Transformer une préfacture](img/dep-facturation-prefacture.png)

## Créer une facture vierge

1. Cliquez sur **facture vierge**, en haut de l'écran.
2. Dans la fenêtre **Sélectionner l'association**, choisissez la **Comptabilité**, la **Saison** et l'**Association**, puis cliquez sur **Rechercher**. Si vous êtes déjà sur les factures d'une association, cette étape est sautée.
3. Bloc **Références** : vérifiez la saison, la comptabilité et l'association. Le champ **Section** permet d'adresser la facture à une section précise de l'association ; **Vos références** accueille une référence libre.
4. Bloc **Adresse** : vérifiez le **Contact** et l'adresse. Cochez **Envoi par email** et vérifiez l'**Email** pour envoyer la facture par mail.
5. Ajoutez les produits : sélectionnez chaque produit, vérifiez la **Quantité** et le **Px Unit.**, puis cliquez sur **+**.
6. Bloc **Réglement** : si la facture est payée tout de suite, choisissez le mode de règlement dans **Réglement de cette facture** ; sinon, laissez **Pas de réglement**.
7. Cliquez sur **Valider la facture**.

![Nouvelle facture](img/dep-facturation-nouvelle.png)

![Ajout de produits](img/dep-facturation-produits.png)

!!! tip "Un produit manque dans la liste ?"
    Les produits se créent dans [Produits et tarifs](parametrage-produits.md).

## Enregistrer un règlement

1. Cliquez sur **règlement**, en haut de l'écran. La fenêtre **Ajouter un règlement** s'ouvre.
2. Choisissez la **Structure** : Ligue, Ufolep ou Usep.
3. Saisissez le **N° de l'association** ; son nom s'affiche dans **Nom association**. Le bouton **Rechercher** aide à la retrouver.
4. Renseignez la **Date** et le **Mode de réglement** (obligatoires), et si besoin une **Référence** (par exemple le numéro du chèque).
5. Pour solder une facture précise, indiquez son **Numéro de facture**.
6. Saisissez le **Montant** (obligatoire) et, si besoin, des **Informations réglement**.
7. Validez. **Annuler** ferme la fenêtre sans rien enregistrer.

Le règlement apparaît ensuite dans le compte de l'association, que l'association consulte dans **Comptabilité > Mon compte**.

## Voir aussi

- [Faire une remise en banque](facturation-remise.md)
- [Suivre et transférer la comptabilité](comptabilite.md)
