// La fenêtre « Proposer une modification » ou « Proposer une nouvelle fiche ».
class FenetreProposition {
  /** @param {import('@playwright/test').Page} page */
  constructor(page) {
    this.page = page;
    this.fenetre = page.locator('dialog.proposition');
    this.titreFiche = this.fenetre.locator('input[name=titre]');
    this.texte = this.fenetre.locator('textarea[name=texte]');
    this.resume = this.fenetre.locator('input[name=resume]');
    this.pseudo = this.fenetre.locator('input[name=pseudo]');
    this.message = this.fenetre.locator('.commentaires-message');
    this.merci = this.fenetre.locator('.proposition-merci');
  }

  async attendreLeTexte() {
    await this.page.waitForFunction(() => {
      const t = document.querySelector('dialog.proposition textarea');
      return t && !t.disabled && t.value.length > 20;
    });
  }

  /** Remplace *avant* par *apres* dans le texte de la fiche. */
  async remplacer(avant, apres) {
    const texte = await this.texte.inputValue();
    if (!texte.includes(avant)) throw new Error(`« ${avant} » absent de la fiche`);
    await this.texte.fill(texte.replace(avant, apres));
  }

  async envoyer({ resume, pseudo }) {
    await this.resume.fill(resume);
    await this.pseudo.fill(pseudo);
    await this.fenetre.getByRole('button', { name: 'Envoyer la proposition' }).click();
    // « Envoi… » n'est pas une réponse : on attend le remerciement ou un message d'erreur
    await this.merci.or(this.message.filter({ hasText: /^(?!Envoi)\S/ })).first().waitFor({ timeout: 30_000 });
  }

  async fermer() {
    await this.fenetre.getByRole('button', { name: 'Fermer' }).last().click();
  }
}

module.exports = { FenetreProposition };
