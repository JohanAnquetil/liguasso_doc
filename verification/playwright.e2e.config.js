// @ts-check
// Tests de bout en bout des guides en local : guides (mkdocs), service de commentaires et
// faux GitHub sont démarrés par Playwright. Aucun appel au vrai GitHub ni à la recette.
//
//   npm run test:e2e                 (PYTHON=chemin/vers/python si mkdocs n'est pas dans python3)
const { defineConfig } = require('@playwright/test');
const { mkdtempSync } = require('node:fs');
const { tmpdir } = require('node:os');
const path = require('node:path');

const RACINE = path.resolve(__dirname, '..');
const PYTHON = process.env.PYTHON || 'python3';
const DONNEES = mkdtempSync(path.join(tmpdir(), 'liguasso-e2e-'));   // base neuve à chaque lancement
const reutiliser = !process.env.CI;
const mkdocs = (config, port) =>
  `./sync-commun.sh >/dev/null && NO_MKDOCS_2_WARNING=1 ${PYTHON} -m mkdocs serve -f ${config} --dev-addr=127.0.0.1:${port} --no-livereload`;

module.exports = defineConfig({
  testDir: './e2e/specs',
  outputDir: './test-results/e2e',
  workers: 1,                  // une seule base partagée : les tests s'enchaînent
  timeout: 60_000,
  expect: { timeout: 10_000 },
  reporter: [['list'], ['html', { open: 'never', outputFolder: 'playwright-report/e2e' }]],
  use: {
    baseURL: 'http://localhost:8001',
    viewport: { width: 1300, height: 900 },
    screenshot: 'only-on-failure',
    trace: 'retain-on-failure',
  },
  webServer: [
    {
      command: 'node e2e/support/faux-github.mjs',
      url: 'http://127.0.0.1:8099/__ecritures',
      reuseExistingServer: reutiliser,
    },
    {
      command: `${PYTHON} -m uvicorn app:app --host 127.0.0.1 --port 8003`,
      cwd: path.join(RACINE, 'commentaires'),
      url: 'http://127.0.0.1:8003/sante',
      reuseExistingServer: reutiliser,
      env: {
        DONNEES, ADMIN_MOT_DE_PASSE: 'mot-de-passe-e2e', ALTCHA_COUT: '1000', LIMITES_RELACHEES: '1',
        GITHUB_TOKEN: 'jeton-factice', GITHUB_API: 'http://127.0.0.1:8099',
        CORS_ORIGINES: 'http://localhost:8000 http://localhost:8001',
      },
    },
    {
      command: mkdocs('mkdocs.departemental.local.yml', 8001),
      cwd: RACINE, url: 'http://127.0.0.1:8001/', reuseExistingServer: reutiliser, timeout: 120_000,
    },
    {
      command: mkdocs('mkdocs.association.local.yml', 8000),
      cwd: RACINE, url: 'http://127.0.0.1:8000/', reuseExistingServer: reutiliser, timeout: 120_000,
    },
  ],
});
