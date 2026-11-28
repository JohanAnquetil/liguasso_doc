// Connexion à la recette et choix du profil.
// Identifiants lus dans les variables d'environnement LOGIN et MDP.
const { expect } = require('@playwright/test');

async function seConnecter(page, { role, structure }) {
  if (!process.env.LOGIN || !process.env.MDP) {
    throw new Error('Variables LOGIN et MDP manquantes (ex. : login_tests_liguasso npm test)');
  }
  await page.goto('/');
  await page.fill('#MainContent_MainContent_ucLogin1_txtIdentifiant', process.env.LOGIN);
  await page.fill('#MainContent_MainContent_ucLogin1_txtMdp', process.env.MDP);
  await page.click('#MainContent_MainContent_ucLogin1_btnConnect');
  await page.waitForLoadState('networkidle');

  const carte = page.locator('a[id*=lbRoleChx]').filter({ hasText: role }).filter({ hasText: structure }).first();
  if (await carte.count()) {
    await Promise.all([page.waitForNavigation(), carte.click()]);
  }
  await expect(page.locator('.dropdown-menu').first()).toBeAttached();
}

// Retrouve dans le menu l'entrée correspondant au chemin ["Adhésion", "Lots"].
// Renvoie { href } ou { erreur, possibles }.
async function trouverDansLeMenu(page, chemin) {
  return page.evaluate((chemin) => {
    const norm = s => s.replace(/»/g, '').replace(/\s+/g, ' ').trim().toLowerCase();
    const libelle = el => norm(el.childNodes.length ? [...el.childNodes].filter(n => n.nodeType === 3 || n.tagName !== 'UL').map(n => n.textContent).join(' ') : el.textContent);
    // Niveau 0 : les déclencheurs des menus principaux
    let candidats = [...document.querySelectorAll('.dropdown-menu')]
      .map(m => m.parentElement.querySelector(':scope > a, :scope > button, :scope > .dropdown-toggle'))
      .filter(Boolean)
      .filter(t => !t.closest('.dropdown-menu'));
    let courant = null;
    for (const [niveau, nom] of chemin.entries()) {
      courant = candidats.find(c => libelle(c) === norm(nom));
      if (!courant) {
        return { erreur: `« ${nom} » introuvable (niveau ${niveau + 1})`, possibles: [...new Set(candidats.map(c => c.textContent.replace(/\s+/g, ' ').trim()))] };
      }
      const sousMenu = courant.parentElement.querySelector(':scope > .dropdown-menu');
      candidats = sousMenu
        ? [...sousMenu.querySelectorAll(':scope > li > a, :scope > a, :scope > li > .dropdown-toggle')]
        : [];
    }
    const href = courant.getAttribute('href');
    return { href: href && href !== '#' ? courant.href : null };
  }, chemin);
}

module.exports = { seConnecter, trouverDansLeMenu };
