// Une page du guide : en-tête de fiche (encadré Accès, boutons Modifier et PDF).
const { BlocCommentaires } = require('./BlocCommentaires');
const { FenetreProposition } = require('./FenetreProposition');

class PageGuide {
  /** @param {import('@playwright/test').Page} page */
  constructor(page) {
    this.page = page;
    this.titre = page.locator('article h1');
    this.encadreAcces = page.locator('.admonition.chemin');
    this.boutonPdf = page.locator('a.bouton-pdf:not(.bouton-modifier)');
    this.boutonModifier = page.locator('.bouton-modifier');
    this.boutonNouvelleFiche = page.getByRole('button', { name: 'Proposer une nouvelle fiche' });
    this.commentaires = new BlocCommentaires(page);
  }

  async ouvrir(chemin) {
    await this.page.goto(chemin);
    await this.commentaires.section.waitFor();       // le service a répondu
  }

  async proposerUneModification() {
    await this.boutonModifier.click();
    const fenetre = new FenetreProposition(this.page);
    await fenetre.attendreLeTexte();
    return fenetre;
  }

  async proposerUneNouvelleFiche() {
    await this.boutonNouvelleFiche.click();
    return new FenetreProposition(this.page);
  }
}

module.exports = { PageGuide };
