// La page de modération (/api/commentaires/admin).
const ADRESSE = 'http://localhost:8003/api/commentaires/admin';

class PageModeration {
  /** @param {import('@playwright/test').Page} page */
  constructor(page) {
    this.page = page;
    this.motDePasse = page.locator('#mdp');
    this.erreurConnexion = page.locator('#erreur-connexion');
    this.liste = page.locator('#liste');
    this.alerteGithub = page.locator('#sans-github');
  }

  async ouvrir() {
    await this.page.goto(ADRESSE);
  }

  async connecter(motDePasse = 'mot-de-passe-e2e') {
    await this.ouvrir();
    await this.motDePasse.fill(motDePasse);
    await this.page.getByRole('button', { name: 'Se connecter' }).click();
    await this.page.locator('#moderation:not([hidden]), #erreur-connexion:not(:empty)').first().waitFor();
  }

  onglet(nom) {
    return this.page.locator('.onglets button', { hasText: nom }).first();
  }

  compteur(filtre) {
    return this.page.locator(`[data-compte="${filtre}"]`);
  }

  async afficher(nom) {
    await this.onglet(nom).click();
    await this.page.waitForFunction((n) =>
      [...document.querySelectorAll('.onglets button')].some((b) => b.textContent.startsWith(n) && b.getAttribute('aria-pressed') === 'true'), nom);
    await this.liste.locator('.carte, .vide').first().waitFor();
  }

  carte(texte) {
    return this.liste.locator('.carte', { hasText: texte }).first();
  }

  /** Clique sur un bouton d'une carte, en acceptant une éventuelle confirmation. */
  async agir(texte, bouton) {
    this.page.once('dialog', (d) => d.accept());
    const carte = this.carte(texte);
    await carte.getByRole('button', { name: bouton }).click();
    await carte.waitFor({ state: 'detached' });
  }

  async repondreAuNomDeLEquipe(texte, reponse) {
    const carte = this.carte(texte);
    await carte.getByRole('button', { name: "Répondre au nom de l'équipe" }).click();
    await carte.locator('textarea').fill(reponse);
    await carte.getByRole('button', { name: 'Publier la réponse' }).click();
    await carte.waitFor({ state: 'detached' });
  }

  async accepterProposition(resume) {
    this.page.once('dialog', (d) => d.dismiss());        // « Ouvrir la pull request ? » : non
    const carte = this.carte(resume);
    await carte.getByRole('button', { name: /Accepter/ }).click();
    await carte.waitFor({ state: 'detached' });
  }
}

module.exports = { PageModeration };
