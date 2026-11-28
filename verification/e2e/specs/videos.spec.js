// Tutos vidéo : carte dans la fiche, lecture au clic sans cookie, repères et vidéothèque.
const { test, expect } = require('../support/fixtures');

test.describe('Tutos vidéo', () => {
  test('la carte affiche l\'aperçu, et YouTube ne se charge qu\'au clic', async ({ visiteur, page }) => {
    const youtube = [];
    page.on('request', (r) => /youtube|ytimg/.test(r.url()) && youtube.push(r.url()));
    await visiteur.ouvrir('/adhesions-import/');
    const carte = page.locator('.tuto-video').first();
    await expect(carte).toContainText('Importer un fichier de demandes de licence');
    await expect(carte.locator('.tuto-video__duree')).toHaveText('7 min');
    expect(youtube).toEqual([]);                                   // rien avant le clic

    await carte.getByRole('button', { name: /Lire la vidéo/ }).click();
    await expect(carte.locator('iframe')).toHaveAttribute('src', /^https:\/\/www\.youtube-nocookie\.com\/embed\/lMVnP_gSw5U/);
  });

  test('le menu signale les fiches qui ont une vidéo', async ({ visiteur, page }) => {
    await visiteur.ouvrir('/adhesions-import/');
    const reperes = page.locator('.md-nav--primary .repere-video');
    await expect(reperes.first()).toBeAttached();
    await expect(page.locator('.md-nav--secondary .repere-video')).toHaveCount(0);   // pas dans la table des matières
  });

  test('l\'accueil et la page Tutos vidéo listent les vidéos', async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('.videos-grille .vignette-video')).toHaveCount(2);
    await page.goto('/videos/');
    const vignette = page.locator('.vignette-video', { hasText: 'Importer un fichier de demandes de licence' });
    await vignette.click();
    await expect(page).toHaveURL(/adhesions-import\/#video-lMVnP_gSw5U$/);
  });

  test('dans le PDF, la vidéo devient un aperçu avec son lien sans cookie', async ({ visiteur, page }) => {
    await visiteur.ouvrir('/adhesions-import/');
    await page.emulateMedia({ media: 'print' });
    await expect(page.locator('.tuto-video__lien')).toBeVisible();
    await expect(page.locator('.tuto-video__lien a')).toHaveAttribute('href', 'https://www.youtube-nocookie.com/embed/lMVnP_gSw5U');
  });
});
