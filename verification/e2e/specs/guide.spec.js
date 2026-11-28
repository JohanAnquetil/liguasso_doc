// Ce que tout le monde voit sur une fiche, avant toute contribution.
const { test, expect } = require('../support/fixtures');

test.describe('Une fiche du guide', () => {
  test('commence par son encadré « Accès » et propose Modifier et PDF', async ({ visiteur }) => {
    await visiteur.ouvrir('/adhesions-valider/');
    await expect(visiteur.encadreAcces).toContainText('Dans le menu, cliquez sur Adhésion, puis sur Lots');
    await expect(visiteur.boutonModifier).toBeVisible();
    await expect(visiteur.boutonPdf).toBeVisible();
  });

  test('sans PDF préparé (rédaction locale), le bouton PDF ouvre l\'impression', async ({ visiteur, page }) => {
    await page.addInitScript(() => { window.__impressions = 0; window.print = () => { window.__impressions++; }; });
    await visiteur.ouvrir('/adhesions-valider/');
    await expect(visiteur.boutonPdf).not.toHaveAttribute('download');
    await visiteur.boutonPdf.click();
    expect(await page.evaluate(() => window.__impressions)).toBe(1);
  });

  test('à l\'impression, seuls le contenu et l\'entête du guide apparaissent', async ({ visiteur, page }) => {
    await visiteur.ouvrir('/adhesions-valider/');
    await page.emulateMedia({ media: 'print' });
    await expect(page.locator('.impression-entete')).toContainText('Guide d’utilisation');
    await expect(page.locator('.impression-entete')).toContainText('Gestion Départementale');
    for (const masque of ['#commentaires', '.contribuer', '.bouton-pdf', '.md-header']) {
      await expect(page.locator(masque).first()).toBeHidden();
    }
  });

  test('le guide associations a ses propres commentaires', async ({ visiteur, page }) => {
    const appel = page.waitForRequest((r) => r.url().includes('/api/commentaires?page='));
    await visiteur.ouvrir('http://localhost:8000/adherents-lots/');
    expect(new URL((await appel).url()).searchParams.get('page')).toBe('association/adherents-lots');
    await expect(page.locator('.impression-entete')).toContainText('Gestion Associative');
  });
});
