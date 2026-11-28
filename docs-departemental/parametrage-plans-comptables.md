# Paramétrer les plans comptables

!!! chemin "Accès"
    - Dans le menu, cliquez sur **Paramétrage**, puis sur **Comptabilité**, puis sur **Paramétres comptables**.
    - Dans le menu, cliquez sur **Paramétrage**, puis sur **Comptabilité**, puis sur **Plan comptable général**.
    - Dans le menu, cliquez sur **Paramétrage**, puis sur **Comptabilité**, puis sur **Plan comptable analytique**.
    - Dans le menu, cliquez sur **Paramétrage**, puis sur **Comptabilité**, puis sur **Plan comptable tiers**.
    - Dans le menu, cliquez sur **Paramétrage**, puis sur **Comptabilité**, puis sur **Plan comptable des produits**.
    - Dans le menu, cliquez sur **Paramétrage**, puis sur **Comptabilité**, puis sur **Plan comptable des modes de règlement**.

Le paramétrage comptable indique à Ligu'asso **dans quels comptes enregistrer** chaque facture et chaque règlement, pour produire les écritures comptables. Il se remplit une fois, au démarrage, puis ne change qu'en cas d'évolution de votre comptabilité.

!!! warning "Pourquoi c'est important"
    Un produit ou un mode de règlement sans compte produit des **écritures sans compte général**, qui **bloquent le transfert** vers votre logiciel de comptabilité. → [Suivre et transférer la comptabilité](comptabilite.md)

![Menu Paramétrage comptable](img/dep-plans-menu.png)

## Paramètres comptables : régler l'export

C'est ici que se règle l'**export comptable** : la façon dont les pièces sont converties en écritures importables dans votre logiciel. L'écran **Gestion des paramètrages comptables** liste un paramétrage par structure : **LIGUE**, **UFOLEP** et **USEP**.

1. Sur la ligne de la structure, cliquez sur l'icône crayon (**Modifier**), dans la colonne **Actions**. L'icône en forme d'œil (**Visualiser**) affiche le paramétrage sans le modifier.
2. Réglez les blocs décrits ci-dessous.
3. Cliquez sur **Valider**. **Retour** quitte l'écran sans enregistrer.

![Liste des paramétrages : une ligne par structure, icônes Visualiser et Modifier](img/dep-plans-parametres.png)

Le paramétrage d'une structure comprend :

- en haut, le **Journal des ventes** et le **Journal des réglements** : les codes des journaux de votre logiciel de comptabilité. L'option **Comptabilité analytique** active l'analytique, et **Plan analytique** indique le plan utilisé ;
- **Compte général** : **Client unique** (un seul compte pour toutes les associations, choisi dans **Compte général client unique**, par exemple **411000 - CLIENTS**), **Manuellement** ou **Par numéro d'affiliation** ;
- **Compte tiers** : **Client unique**, **Manuellement**, **Par numéro d'affiliation** ou **Aucun**. Avec **Par numéro d'affiliation**, renseignez aussi le **Radical** et le **Nombre de caractères à droite** ;
- **Format** du fichier d'écritures, selon votre logiciel : **Sage i7**, **Sage 100c**, **Quadra / Quadratus** ou **Générique (pour Ciel, Ebp, etc)** ;
- **Paramètres généraux** :
    - **Les données comptables ont été transférées jusqu'au** : la date jusqu'à laquelle les écritures ont déjà été transférées vers votre logiciel ;
    - **Compte d'attente pour facturation de juin à décembre** : à activer pour que les factures de juin à décembre utilisent le **compte d'attente** de chaque produit (voir le plan comptable des produits, plus bas) ;
    - **Inversé le sens au lieu d'avoir un montant négatif** : une écriture négative est passée dans le sens opposé, avec un montant positif.

![Modification du paramétrage comptable : journaux, compte général, compte tiers, format et paramètres généraux](img/dep-plans-export.png)

!!! warning "Activez l'option pour utiliser les comptes d'attente"
    Les comptes d'attente saisis dans le **Plan comptable des produits** ne sont utilisés que si l'option **Compte d'attente pour facturation de juin à décembre** est **activée** dans le paramétrage de la structure concernée (LIGUE, UFOLEP ou USEP). Si elle est désactivée, les factures de juin à décembre sont transférées sans compte d'attente, même quand chaque produit en a un.

## Plan comptable général et analytique : créer des comptes

Ces écrans servent à créer les comptes **généraux** et **analytiques**. Recherchez un compte existant, ou cliquez sur **Ajouter un compte**.

![Plan comptable général](img/dep-plans-general.png)

## Plan comptable tiers : le compte de chaque association

Le **compte tiers** est le compte comptable propre à chaque association affiliée. Recherchez les associations selon vos critères, puis modifiez un compte avec l'icône crayon.

![Plan comptable tiers](img/dep-plans-tiers.png)

![Modification d'un compte tiers](img/dep-plans-tiers-modif.png)

## Plan comptable des produits : les comptes de chaque produit facturé

Chaque produit (adhésion, cotisation, etc.) doit être associé aux comptes à utiliser quand il est facturé.

1. Choisissez la **saison** et la **comptabilité** (Ligue, UFOLEP ou USEP), et si besoin un code ou un libellé de produit. Cliquez sur **Rechercher**.
2. Sur la ligne du produit, l'icône crayon ouvre son paramétrage ; l'icône œil le consulte.
3. Choisissez le **compte général**, le **compte d'attente** et, si besoin, le **compte analytique**, avec pour chacun son **sens** (par exemple **Crédit**) et son **signe** (par exemple **+**).
4. Cliquez sur **Valider**.

!!! tip "Le compte d'attente n'est pas utilisé ?"
    Le compte d'attente d'un produit ne sert que si l'option **Compte d'attente pour facturation de juin à décembre** est activée dans les **Paramétres comptables** de la structure. → [Paramètres comptables : régler l'export](#parametres-comptables-regler-lexport)

![Plan comptable des produits](img/dep-plans-produits.png)

![Modification d'un produit](img/dep-plans-produits-modif.png)

## Plan comptable des modes de règlement : où enregistrer les encaissements

Chaque mode de règlement (chèque, virement, carte bancaire, OD de régularisation, etc.) doit être associé au compte où l'encaissement est enregistré.

1. Choisissez la **structure** (Ligue, UFOLEP ou USEP), puis cliquez sur **Rechercher**. Le filtre **Sans transfert comptable** n'affiche que les modes de règlement non transmis en comptabilité.
2. Ouvrez le mode de règlement avec l'icône crayon.
3. Choisissez le **compte général**, son **sens** et son **signe**, puis cliquez sur **Valider**.

![Plan comptable des règlements](img/dep-plans-reglements.png)

![Modification d'un mode de règlement](img/dep-plans-reglements-modif.png)
