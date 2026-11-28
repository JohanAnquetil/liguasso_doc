// Éditeur visuel : les gestes de saisie (Entrée, Retour arrière, encadrés, liens) et l'affichage mobile.
// Chaque test lit le Markdown produit et vérifie qu'il ne contient que le changement attendu.
const { test, expect } = require('../support/fixtures');

const lignesChangees = (avant, apres) => {
  const a = avant.split('\n'), b = apres.split('\n');
  return { retirees: a.filter((l) => !b.includes(l)), ajoutees: b.filter((l) => !a.includes(l)) };
};

test.describe('Éditeur visuel : gestes de saisie', () => {
  test('Entrée au milieu d\'un paragraphe le coupe en deux paragraphes', async ({ visiteur }) => {
    await visiteur.ouvrir('/adhesions-lots/');
    const fenetre = await visiteur.proposerUneModification();
    const avant = await fenetre.markdown();
    const para = fenetre.paragraphe('Par défaut, seuls les lots en cours');
    await fenetre.curseurApres(para, 'sont affichés.');
    await visiteur.page.keyboard.press('Enter');
    const apres = await fenetre.markdown();
    expect(apres).toContain('Par défaut, seuls les lots en cours sont affichés.\n\nCochez **Afficher l\'historique des lots validés**');
    expect(lignesChangees(avant, apres).retirees).toHaveLength(1);
  });

  test('Entrée dans une liste ajoute un élément, Retour arrière sur un élément vide le retire', async ({ visiteur }) => {
    await visiteur.ouvrir('/adhesions-gerer/');
    const fenetre = await visiteur.proposerUneModification();
    const avant = await fenetre.markdown();
    const element = fenetre.editeur.locator('.editeur-element', { hasText: 'Affinez si besoin' }).first();
    await fenetre.curseurALaFin(element);
    await visiteur.page.keyboard.press('Enter');
    await visiteur.page.keyboard.type('Étape ajoutée');
    let apres = await fenetre.markdown();
    expect(apres).toMatch(/2\. Affinez si besoin[^\n]*\n3\. Étape ajoutée\n4\. Cliquez sur \*\*Rechercher\*\*/);

    const ajoute = fenetre.editeur.locator('.editeur-element', { hasText: 'Étape ajoutée' });
    await fenetre.curseurALaFin(ajoute);
    for (let i = 0; i < 'Étape ajoutée'.length; i++) await visiteur.page.keyboard.press('Backspace');
    await visiteur.page.keyboard.press('Backspace');                 // élément vide : il disparaît
    apres = await fenetre.markdown();
    expect(apres).toBe(avant);                                       // retour exact à l'original
  });

  test('ajouter un encadré, changer son type et son titre', async ({ visiteur }) => {
    await visiteur.ouvrir('/adhesions-lots/');
    const fenetre = await visiteur.proposerUneModification();
    const para = fenetre.paragraphe('Par défaut, seuls les lots en cours');
    await fenetre.ajouterApres(para, 'Encadré « Astuce »');
    await visiteur.page.keyboard.type('Actualisez la page après un import.');
    const encadre = fenetre.editeur.locator('.editeur-encadre').filter({ has: visiteur.page.locator('.editeur-paragraphe', { hasText: 'Actualisez la page' }) });
    await encadre.locator('select.editeur-encadre-genre').selectOption('warning');
    await encadre.locator('input.editeur-encadre-titre').fill('Lot introuvable ?');
    const md = await fenetre.markdown();
    expect(md).toContain('!!! warning "Lot introuvable ?"\n    Actualisez la page après un import.');
  });

  test('mettre un mot en lien avec le bouton Lien, puis le retirer', async ({ visiteur }) => {
    await visiteur.ouvrir('/adhesions-lots/');
    const fenetre = await visiteur.proposerUneModification();
    const para = fenetre.paragraphe('Par défaut, seuls les lots en cours');
    await fenetre.selectionner(para, 'lots en cours');
    visiteur.page.once('dialog', (d) => d.accept('adhesions-valider.md'));
    await fenetre.fenetre.locator('.editeur-outil[title=Lien]').click();
    expect(await fenetre.markdown()).toContain('seuls les [lots en cours](adhesions-valider.md) sont affichés');

    const para2 = fenetre.paragraphe('Par défaut, seuls les');
    await fenetre.selectionner(para2, 'lots en cours');
    await fenetre.fenetre.getByRole('button', { name: 'Retirer le lien' }).click();
    expect(await fenetre.markdown()).toContain('seuls les lots en cours sont affichés');
  });

  test('un texte collé depuis ailleurs arrive sans sa mise en forme', async ({ visiteur }) => {
    await visiteur.ouvrir('/adhesions-lots/');
    const fenetre = await visiteur.proposerUneModification();
    const para = fenetre.paragraphe('Par défaut, seuls les lots en cours');
    await fenetre.curseurALaFin(para);
    await para.evaluate((n) => {
      const donnees = new DataTransfer();
      donnees.setData('text/html', '<h1 style="color:red">Titre <b>collé</b></h1>');
      donnees.setData('text/plain', ' Texte\ncollé');
      n.dispatchEvent(new ClipboardEvent('paste', { clipboardData: donnees, bubbles: true, cancelable: true }));
    });
    const md = await fenetre.markdown();
    expect(md).toContain('déjà validés. Texte collé');
    expect(md).not.toContain('color:red');
  });
});

test.describe('Éditeur visuel sur téléphone', () => {
  test.use({ viewport: { width: 390, height: 844 } });

  test('l\'éditeur tient dans l\'écran et reste utilisable', async ({ visiteur, page }) => {
    await visiteur.ouvrir('/adhesions-lots/');
    const fenetre = await visiteur.proposerUneModification();
    const largeur = await fenetre.fenetre.evaluate((d) => ({ visible: d.clientWidth, contenu: d.scrollWidth }));
    expect(largeur.contenu).toBeLessThanOrEqual(largeur.visible + 1);          // pas de défilement horizontal
    await expect(fenetre.fenetre.locator('.editeur-outil[title=Gras]')).toBeVisible();
    const para = fenetre.paragraphe('Par défaut, seuls les lots en cours');
    await fenetre.curseurALaFin(para);
    await page.keyboard.type(' Ajout sur mobile.');
    expect(await fenetre.markdown()).toContain('déjà validés. Ajout sur mobile.');
  });
});
