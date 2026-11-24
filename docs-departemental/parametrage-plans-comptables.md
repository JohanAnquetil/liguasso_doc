# Plans comptables

Ce paramétrage indique à Ligu'asso comment transformer vos factures et vos règlements en écritures comptables. Il se remplit une fois, au démarrage, puis ne change qu'en cas d'évolution de votre comptabilité.

![Menu Paramétrage comptable](img/dep-plans-menu.png)

## Paramètres comptables

L'écran liste vos paramétrages comptables. Pour en modifier un, cliquez sur le bouton **Modifier**, symbolisé par un crayon, à droite de la ligne.

![Liste des paramétrages](img/dep-plans-parametres.png)

C'est ici que se règle l'**export comptable** : la façon dont les pièces sont converties en écritures, pour être importées directement dans votre logiciel de comptabilité.

![Export comptable](img/dep-plans-export.png)

## Plan comptable général et analytique

Cet écran sert à créer les comptes comptables **généraux** et **analytiques**. Vous pouvez rechercher un compte existant, ou en ajouter un avec **Ajouter un compte**.

![Plan comptable général](img/dep-plans-general.png)

## Plan comptable tiers

Il liste les **comptes tiers**, c'est-à-dire le compte comptable propre à chaque association affiliée, et permet de les modifier.

![Plan comptable tiers](img/dep-plans-tiers.png)

Retrouvez les associations selon vos critères de recherche, puis modifiez-les avec l'icône crayon.

![Modification d'un compte tiers](img/dep-plans-tiers-modif.png)

## Plan comptable des produits

Il associe chaque produit — adhésion, cotisation, etc. — aux comptes comptables à utiliser lors de sa facturation.

**Rechercher un produit.** Choisissez la saison et la comptabilité (Ligue, UFOLEP ou USEP), ajoutez si besoin un code ou un libellé, puis cliquez sur **Rechercher**. L'icône crayon ouvre le paramétrage d'un produit, l'icône œil le consulte.

![Plan comptable des produits](img/dep-plans-produits.png)

**Modifier le paramétrage.** Choisissez le compte général, le compte d'attente et, si besoin, le compte analytique, avec pour chacun son **sens** (Crédit) et son **signe** (+). Cliquez ensuite sur **Valider**.

![Modification d'un produit](img/dep-plans-produits-modif.png)

## Plan comptable des modes de règlement

Il associe chaque mode de règlement — chèque, virement, OD de régularisation, etc. — au compte comptable où l'encaissement est enregistré.

**Rechercher un mode de règlement.** Choisissez la structure (Ligue, UFOLEP ou USEP), puis cliquez sur **Rechercher**. Le filtre **Sans transfert comptable** n'affiche que ceux qui ne sont pas transmis en comptabilité.

![Plan comptable des règlements](img/dep-plans-reglements.png)

**Modifier le paramétrage.** Choisissez le compte général, son sens et son signe, puis cliquez sur **Valider**.

![Modification d'un mode de règlement](img/dep-plans-reglements-modif.png)

!!! tip "Écritures bloquantes"
    Un mode de règlement sans rattachement ici produit des écritures sans compte général, qui empêchent le transfert comptable. → [Comptabilité](comptabilite.md)
