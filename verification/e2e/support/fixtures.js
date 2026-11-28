// Fixtures : chaque test reçoit des visiteurs indépendants (navigateurs séparés),
// une modération déjà connectée et un accès au faux GitHub.
const base = require('@playwright/test');
const { PageGuide } = require('../pages/PageGuide');
const { PageModeration } = require('../pages/PageModeration');

const FAUX_GITHUB = 'http://127.0.0.1:8099/__ecritures';

/** Texte unique par test : les tests partagent la même base sans se gêner. */
const unique = (prefixe) => `${prefixe} ${Date.now().toString(36)}${Math.random().toString(36).slice(2, 6)}`;

const test = base.test.extend({
  // Un premier visiteur (Camille)
  visiteur: async ({ page }, use) => use(new PageGuide(page)),

  // Un second visiteur, avec son propre navigateur (autre identité anonyme)
  autreVisiteur: async ({ browser }, use) => {
    const contexte = await browser.newContext();
    await use(new PageGuide(await contexte.newPage()));
    await contexte.close();
  },

  moderation: async ({ browser }, use) => {
    const contexte = await browser.newContext();
    const moderation = new PageModeration(await contexte.newPage());
    await moderation.connecter();
    await use(moderation);
    await contexte.close();
  },

  github: async ({ request }, use) => {
    await request.delete(FAUX_GITHUB);
    await use({ ecritures: async () => (await request.get(FAUX_GITHUB)).json() });
  },
});

module.exports = { test, expect: base.expect, unique };
