# Comptabilité

!!! chemin "Accès"
    - Dans le menu, cliquez sur **Comptabilité**, puis sur **Transfert vers logiciel comptable**.
    - Dans le menu, cliquez sur **Comptabilité**, puis sur **Consultation d'un compte tiers**.
    - Dans le menu, cliquez sur **Comptabilité**, puis sur **Livres comptables**.

Le menu **Comptabilité** regroupe les outils qui permettent de suivre les écritures générées par Ligu'asso — ventes et règlements — et de les transférer vers votre logiciel comptable.

![Menu Comptabilité](img/dep-comptabilite-menu.png)

Il propose trois entrées :

| Entrée | À quoi elle sert |
|---|---|
| **Transfert vers logiciel comptable** | Génère le fichier d'écritures à importer dans votre comptabilité. |
| **Consultation d'un compte tiers** | Affiche le détail des écritures d'un tiers : association, adhérent.e… |
| **Livres comptables** | Donne accès au Grand livre des tiers, au Journal des ventes, au Journal des règlements et à la Balance. |

!!! note
    Toutes ces pages sont en **consultation seule**, à l'exception du transfert vers le logiciel comptable.

## Transférer ses écritures

L'écran **Transfert vers logiciel comptable** prépare puis génère le fichier d'écritures sur une période donnée.

### 1. Rechercher les écritures

- **Comptabilité** : celle concernée par le transfert — USEP, UFOLEP ou Ligue.
- **Début de période** et **Fin de période** : obligatoires. Seules les écritures comprises entre ces deux dates sont prises en compte.
- **Type d'écritures** : *Ventes et règlements*, *Ventes uniquement* ou *Règlements uniquement*.

![Recherche des écritures](img/dep-comptabilite-recherche.png)

### 2. Vérifier le récapitulatif

Le tableau présente, pour chaque journal — ventes ou règlements — et chaque mois : le nombre de pièces, le nombre d'écritures dont le compte général n'est pas renseigné, le total au débit et le total au crédit.

![Récapitulatif](img/dep-comptabilite-resultats.png)

!!! tip
    Vérifiez que le débit et le crédit sont équilibrés avant de lancer l'export.

### 3. Générer le fichier

1. Cliquez sur **Génération du fichier d'écritures**.
2. Choisissez le format de votre logiciel : Sage i7, Sage 100c, Quadra / Quadratus ou Générique (Ciel, EBP…).
3. Vérifiez le nom du fichier, proposé automatiquement.
4. Cliquez sur **Générer le fichier d'écritures**.

![Bouton Génération du fichier d'écritures](img/dep-comptabilite-bouton-generation.png)

![Choix du format](img/dep-comptabilite-generation.png)

Le fichier `.txt` est téléchargé : il ne reste plus qu'à l'importer dans votre logiciel comptable.

## Corriger les écritures sans compte général

Un **triangle rouge** signale des écritures dont le compte général n'est pas renseigné : elles empêchent l'extraction.

![Triangle d'alerte](img/dep-comptabilite-alerte.png)

Le mieux est de compléter le [paramétrage comptable](parametrage-plans-comptables.md) avant de générer le fichier. Sinon, ces écritures devront être corrigées dans votre logiciel.

**Identifiez d'abord les lignes concernées.** Cliquez sur le bouton **Éditer**, en bas de page : le fichier s'ouvre et laisse voir, par exemple, un compte clients non renseigné sur la pièce comptable *RL 3083*.

![Fichier édité](img/dep-comptabilite-editer.png)

**Remontez ensuite à la pièce.** Rendez-vous dans [Facturation et règlement](facturation.md), indiquez le numéro de la pièce et l'association, puis visualisez-la en cliquant sur l'**œil**.

![Retrouver la pièce](img/dep-comptabilite-piece.png)

Dans l'exemple ci-dessous, la ligne en cause est un paiement par **Carte Bleue** : ce mode de règlement n'a pas de rattachement dans le plan comptable.

![Ligne en cause](img/dep-comptabilite-ligne.png)

!!! tip "La corriger durablement"
    Rattachez le mode de règlement à un compte dans [Plans comptables](parametrage-plans-comptables.md). L'écriture cessera alors de bloquer les transferts suivants.
