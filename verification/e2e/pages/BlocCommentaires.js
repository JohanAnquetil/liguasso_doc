const { expect } = require('@playwright/test');

// Le bloc « Commentaires » en bas d'une page du guide.
class BlocCommentaires {
  /** @param {import('@playwright/test').Page} page */
  constructor(page) {
    this.page = page;
    this.section = page.locator('#commentaires');
    this.titre = this.section.locator('h2');
    this.formulaire = this.section.locator('form.commentaires-formulaire');
    this.message = this.section.locator('.commentaires-message');
  }

  /** Le commentaire (élément de liste) dont le texte contient *texte*. */
  commentaire(texte) {
    return this.section.locator('li.commentaire').filter({ has: this.page.locator('.commentaire-texte', { hasText: texte }) }).first();
  }

  async ecrire(pseudo, texte) {
    await this.formulaire.getByPlaceholder('Prénom ou pseudo').fill(pseudo);
    await this.formulaire.getByPlaceholder('Votre commentaire').fill(texte);
    await this.formulaire.getByRole('button', { name: 'Envoyer' }).click();
    await this.page.waitForFunction(() => /Merci|Indiquez|erreur|Trop/i.test(document.querySelector('.commentaires-message')?.textContent || ''));
  }

  async liker(texte) {
    // Le bloc est redessiné après chaque like : on relit le bouton par son locator
    const bouton = this.commentaire(texte).locator('.commentaire-like').first();
    const avant = await bouton.textContent();
    await bouton.click();
    await expect(bouton).not.toHaveText(avant);
  }

  async repondre(texte, pseudo, reponse) {
    await this.commentaire(texte).getByRole('button', { name: 'Répondre' }).first().click();
    await this.ecrire(pseudo, reponse);
  }

  async signaler(texte, motif = 'faux') {
    const item = this.commentaire(texte);
    await item.getByRole('button', { name: 'Signaler' }).click();
    const formulaire = item.locator('form.commentaire-signalement');
    await formulaire.locator('select').selectOption(motif);
    await formulaire.getByRole('button', { name: 'Signaler' }).click();
    await item.getByText(/Merci, l'équipe va examiner|déjà signalé/).waitFor({ timeout: 30_000 });
  }
}

module.exports = { BlocCommentaires };
