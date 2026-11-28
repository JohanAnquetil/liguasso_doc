# Suivre et transférer la comptabilité

!!! chemin "Accès"
    - Dans le menu, cliquez sur **Comptabilité**, puis sur **Transfert vers logiciel comptable**.
    - Dans le menu, cliquez sur **Comptabilité**, puis sur **Consultation d'un compte tiers**.
    - Dans le menu, cliquez sur **Comptabilité**, puis sur **Livres comptables**.

Ligu'asso transforme les factures et les règlements en **écritures comptables**. Le menu **Comptabilité** permet de les consulter et de les transférer vers votre logiciel de comptabilité.

![Menu Comptabilité](img/dep-comptabilite-menu.png)

| Entrée du menu | À quoi elle sert |
|---|---|
| **Transfert vers logiciel comptable** | Génère le fichier d'écritures à importer dans votre logiciel de comptabilité. |
| **Consultation d'un compte tiers** | Affiche les écritures d'un tiers (une association), à partir d'une date. |
| **Livres comptables** | Donne accès au **Grand livre des tiers**, au **Journal des ventes**, au **Journal des réglements** et à la **Balance**. |

!!! note
    Toutes ces pages sont en **consultation seule**, sauf le transfert vers le logiciel de comptabilité.

## Consulter le compte d'une association

1. Ouvrez **Consultation d'un compte tiers**.
2. Choisissez la **Comptabilité** (LIGUE, UFOLEP ou USEP) et l'**Association**.
3. Indiquez si besoin une date de départ dans **A partir du**.
4. Cliquez sur **Rechercher**.

## Transférer les écritures vers votre logiciel

### 1. Rechercher les écritures de la période

1. Ouvrez **Transfert vers logiciel comptable**.
2. Choisissez la **Comptabilité** concernée : Ligue, Ufolep ou Usep.
3. Renseignez le **Début de période** et la **Fin de période** (obligatoires). Seules les écritures comprises entre ces deux dates sont prises en compte.
4. Choisissez le type d'écritures : **Ventes et règlement**, **Ventes uniquement** ou **Règlements uniquement**.
5. Cliquez sur **Rechercher**.

![Recherche des écritures](img/dep-comptabilite-recherche.png)

### 2. Vérifier le récapitulatif

Le tableau présente, pour chaque journal (ventes ou règlements) et chaque mois : le nombre de pièces, le nombre d'écritures **sans compte général**, le total au débit et le total au crédit.

![Récapitulatif](img/dep-comptabilite-resultats.png)

!!! tip
    Avant l'export, vérifiez que le débit et le crédit sont équilibrés et qu'aucune écriture n'est sans compte général.

### 3. Générer le fichier

1. Cliquez sur **Génération du fichier d'écritures**.
2. Choisissez le format de votre logiciel : **Sage i7**, **Sage 100c**, **Quadra / Quadratus** ou **Générique** (Ciel, EBP…).
3. Vérifiez le nom du fichier, proposé automatiquement.
4. Cliquez sur **Générer le fichier d'écritures**.

![Bouton Génération du fichier d'écritures](img/dep-comptabilite-bouton-generation.png)

![Choix du format](img/dep-comptabilite-generation.png)

Un fichier `.txt` est téléchargé : importez-le dans votre logiciel de comptabilité. Le bouton **Afficher historique** liste les transferts déjà effectués.

## Corriger les écritures sans compte général

Un **triangle rouge** signale des écritures dont le compte général n'est pas renseigné. Elles **bloquent le transfert**.

![Triangle d'alerte](img/dep-comptabilite-alerte.png)

Le mieux est de compléter le [paramétrage comptable](parametrage-plans-comptables.md) avant de générer le fichier ; sinon, il faudra corriger ces écritures dans votre logiciel.

1. **Identifiez les lignes en cause.** Cliquez sur **Éditer**, en bas de page : le fichier s'ouvre et indique, pour chaque écriture incomplète, le numéro de sa pièce comptable (par exemple *RL 3083*) et le compte manquant (par exemple un compte clients).

    ![Fichier édité](img/dep-comptabilite-editer.png)

2. **Retrouvez la pièce.** Ouvrez [Facturation et règlement](facturation.md), indiquez le numéro de la pièce dans **N° de pièce** et l'association, puis cliquez sur l'icône en forme d'œil.

    ![Retrouver la pièce](img/dep-comptabilite-piece.png)

3. **Repérez la cause.** Dans l'exemple *RL 3083*, la pièce est un règlement par **carte bancaire** : ce mode de règlement n'est rattaché à aucun compte dans le plan comptable.

    ![Ligne en cause](img/dep-comptabilite-ligne.png)

!!! tip "Corriger durablement"
    Rattachez le mode de règlement à un compte dans [Plans comptables](parametrage-plans-comptables.md), section **Plan comptable des modes de règlement**. Les transferts suivants ne seront plus bloqués.
