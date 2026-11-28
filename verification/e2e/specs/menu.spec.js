// Nouvelle fiche avec sa place dans le menu : rubrique ou sous-rubrique, existante ou nouvelle.
const { test, expect, unique } = require('../support/fixtures');

const decoder = (b64) => Buffer.from(b64, 'base64').toString();

test.describe('Place d\'une nouvelle fiche dans le menu', () => {
  test('le formulaire propose les rubriques du guide', async ({ visiteur }) => {
    await visiteur.ouvrir('/adhesions-lots/');
    const fenetre = await visiteur.proposerUneNouvelleFiche();
    const rubrique = fenetre.fenetre.locator('select[name=menu_rubrique]');
    await expect(rubrique.locator('option', { hasText: 'Adhésions et licences' })).toHaveCount(1);
    await expect(rubrique.locator('option', { hasText: '+ Nouvelle rubrique…' })).toHaveCount(1);
    await expect(rubrique).toHaveValue('');                               // « l'équipe choisira » par défaut
  });

  test('nouvelle rubrique et nouvelle sous-rubrique : la PR crée la fiche et l\'entrée de menu', async ({ visiteur, moderation, github }) => {
    const titre = unique('Rembourser une adhésion');
    const rubrique = unique('Remboursements');
    await visiteur.ouvrir('/adhesions-lots/');
    const fenetre = await visiteur.proposerUneNouvelleFiche();
    await fenetre.titreFiche.fill(titre);
    const f = fenetre.fenetre;
    await f.locator('select[name=menu_rubrique]').selectOption({ label: '+ Nouvelle rubrique…' });
    await f.locator('input[name=menu_nouvelle_rubrique]').fill(rubrique);
    await f.locator('select[name=menu_sous_rubrique]').selectOption({ label: '+ Nouvelle sous-rubrique…' });
    await f.locator('input[name=menu_nouvelle_sous_rubrique]').fill('Cas particuliers');
    await f.locator('input[name=menu_libelle]').fill('Rembourser');
    await fenetre.editeur.locator('.editeur-paragraphe').first().click();
    await visiteur.page.keyboard.type('Les étapes du remboursement.');
    await fenetre.envoyer({ resume: titre, pseudo: 'Sam' });
    await expect(fenetre.merci).toBeVisible();

    await moderation.afficher('Propositions');
    await expect(moderation.carte(titre).locator('.menu-prevu')).toHaveText(`Menu : ${rubrique} › Cas particuliers › Rembourser`);
    await moderation.accepterProposition(titre);

    const ecritures = await github.ecritures();
    expect(ecritures.map((e) => `${e.methode} ${e.chemin.replace(/rembourser-une-adhesion-[a-z0-9]+/, 'FICHE')}`)).toEqual([
      'POST git/refs', 'PUT contents/docs-departemental/FICHE.md', 'PUT contents/mkdocs.departemental.yml', 'POST pulls']);
    const fiche = ecritures[1].chemin.split('/').pop();
    const menu = decoder(ecritures[2].corps.content);
    expect(menu).toContain(`  - ${rubrique}:\n      - Cas particuliers:\n          - Rembourser: ${fiche}\n`);
    expect(ecritures[2].corps.sha).toBeTruthy();                           // modification du fichier existant
    expect(ecritures[3].corps.body).toContain(`**Menu** : ${rubrique} › Cas particuliers › Rembourser`);
  });

  test('rubrique existante : une seule ligne ajoutée au menu, à la fin de la rubrique', async ({ visiteur, moderation, github }) => {
    const titre = unique('Relancer un impayé');
    await visiteur.ouvrir('/facturation/');
    const fenetre = await visiteur.proposerUneNouvelleFiche();
    await fenetre.titreFiche.fill(titre);
    await fenetre.fenetre.locator('select[name=menu_rubrique]').selectOption('Facturation et comptabilité');
    await fenetre.editeur.locator('.editeur-paragraphe').first().click();
    await visiteur.page.keyboard.type('Envoyer une relance.');
    await fenetre.envoyer({ resume: titre, pseudo: 'Sam' });
    await moderation.afficher('Propositions');
    await expect(moderation.carte(titre).locator('.menu-prevu')).toHaveText(`Menu : Facturation et comptabilité › ${titre}`);
    await moderation.accepterProposition(titre);

    const [, fiche, menu] = await github.ecritures();
    const avant = require('node:fs').readFileSync(require('node:path').resolve(__dirname, '../../../mkdocs.departemental.yml'), 'utf8');
    const apres = decoder(menu.corps.content);
    const ajoutees = apres.split('\n').filter((l) => !avant.split('\n').includes(l));
    expect(ajoutees).toEqual([`      - ${titre.includes(':') ? `"${titre}"` : titre}: ${fiche.chemin.split('/').pop()}`]);
    expect(apres.indexOf(titre)).toBeLessThan(apres.indexOf('  - Statistiques et extractions'));
  });

  test('nom de rubrique manquant : message clair', async ({ visiteur }) => {
    await visiteur.ouvrir('/adhesions-lots/');
    const fenetre = await visiteur.proposerUneNouvelleFiche();
    await fenetre.titreFiche.fill('Une fiche');
    await fenetre.fenetre.locator('select[name=menu_rubrique]').selectOption({ label: '+ Nouvelle rubrique…' });
    await fenetre.editeur.locator('.editeur-paragraphe').first().click();
    await visiteur.page.keyboard.type('Texte.');
    await fenetre.envoyer({ resume: 'Essai', pseudo: 'Sam' });
    await expect(fenetre.message).toHaveText('Donnez un nom à la nouvelle rubrique ou sous-rubrique.');
  });
});
