// La fenêtre « Proposer une modification » ou « Proposer une nouvelle fiche ».
class FenetreProposition {
  /** @param {import('@playwright/test').Page} page */
  constructor(page) {
    this.page = page;
    this.fenetre = page.locator('dialog.proposition');
    this.titreFiche = this.fenetre.locator('input[name=titre]');
    this.editeur = this.fenetre.locator('.editeur-fiche');
    this.texte = this.fenetre.locator('textarea.editeur-texte-brut');   // mode avancé (Markdown)
    this.boutonModeAvance = this.fenetre.getByRole('button', { name: /Mode avancé|Revenir à l'éditeur visuel/ });
    this.resume = this.fenetre.locator('input[name=resume]');
    this.pseudo = this.fenetre.locator('input[name=pseudo]');
    this.message = this.fenetre.locator('.commentaires-message');
    this.merci = this.fenetre.locator('.proposition-merci');
  }

  async attendreLeTexte() {
    await this.editeur.locator('.editeur-bloc').first().waitFor({ timeout: 20_000 });
  }

  /** Passe en mode avancé (texte Markdown brut). */
  async modeAvance() {
    if (!(await this.texte.count())) await this.boutonModeAvance.click();
    await this.texte.waitFor();
  }

  /** Paragraphe de l'éditeur visuel contenant *texte*. */
  paragraphe(texte) {
    return this.editeur.locator('.editeur-paragraphe', { hasText: texte }).first();
  }

  /** Place le curseur à la fin d'un champ de l'éditeur visuel. */
  async curseurALaFin(champ) {
    await champ.click();
    await champ.evaluate((n) => {
      const r = document.createRange(); r.selectNodeContents(n); r.collapse(false);
      const s = getSelection(); s.removeAllRanges(); s.addRange(r);
    });
  }

  /** Ajoute un bloc (« Paragraphe », « Liste à puces »…) juste après le bloc contenant *champ*. */
  async ajouterApres(champ, genre) {
    const ajouter = champ.locator('xpath=ancestor::div[contains(@class,"editeur-bloc")][1]/following-sibling::div[contains(@class,"editeur-ajouter")][1]');
    await ajouter.hover();
    await ajouter.locator('.editeur-plus').click();
    await this.fenetre.locator('.editeur-menu:not([hidden]) .editeur-choix', { hasText: genre }).click();
  }

  /** Remplace *avant* par *apres* dans le texte de la fiche (mode avancé). */
  async remplacer(avant, apres) {
    await this.modeAvance();
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
