// Vérifie, sur la recette, que chaque chemin indiqué dans un encadré « Accès »
// existe bien dans le menu et mène à une page qui s'affiche.
//
//   login_tests_liguasso npm test
//
// Profils utilisés (modifiables) :
//   PROFIL_ASSO="Président.e|AL La Guerche"
//   PROFIL_DEP="Gestionnaire départemental.e|Puy de Dôme"
const { test, expect } = require('@playwright/test');
const { cheminsDuGuide, pagesSansChemin } = require('./chemins');
const { seConnecter, trouverDansLeMenu } = require('./recette');

const profil = (v, defaut) => {
  const [role, structure] = (v || defaut).split('|');
  return { role, structure };
};

const GUIDES = [
  { dossier: 'docs-association', profil: profil(process.env.PROFIL_ASSO, 'Président.e|AL La Guerche') },
  { dossier: 'docs-departemental', profil: profil(process.env.PROFIL_DEP, 'Gestionnaire départemental.e|Puy de Dôme') },
];

// Pages volontairement sans encadré « Accès » (accueil, aide…)
const SANS_CHEMIN = ['index.md', 'probleme.md', 'limitations.md', 'connexion.md'];

for (const guide of GUIDES) {
  test.describe(guide.dossier, () => {
    test('chaque page a un encadré « Accès »', () => {
      expect(pagesSansChemin(guide.dossier).filter(f => !SANS_CHEMIN.includes(f))).toEqual([]);
    });

    test.describe(`${guide.profil.role} — ${guide.profil.structure}`, () => {
      test.describe.configure({ mode: 'serial' });
      /** @type {import('@playwright/test').Page} */
      let page;

      test.beforeAll(async ({ browser }) => {
        page = await browser.newPage();
        await seConnecter(page, guide.profil);
      });
      test.afterAll(async () => { await page?.close(); });

      for (const { fichier, chemin } of cheminsDuGuide(guide.dossier)) {
        test(`${fichier} : ${chemin.join(' › ')}`, async () => {
          await page.goto('/Pages/Private/Accueil.aspx');
          const r = await trouverDansLeMenu(page, chemin);
          expect(r.erreur, `${r.erreur}\nEntrées disponibles : ${(r.possibles || []).join(' | ')}`).toBeUndefined();

          if (!r.href) return; // sous-menu (ex. « Comptabilité » dans Paramétrage) : sa présence suffit
          const reponse = await page.goto(r.href);
          expect(reponse?.status(), `HTTP pour ${r.href}`).toBeLessThan(400);
          expect(page.url(), 'redirigé vers la connexion').not.toMatch(/Login|Public/i);
          await expect(page.locator('body')).not.toContainText(/Erreur serveur|Server Error/i);
        });
      }
    });
  });
}
