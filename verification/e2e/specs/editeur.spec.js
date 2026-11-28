// Éditeur visuel des propositions : modifier une fiche sans connaître le Markdown.
const { test, expect, unique } = require('../support/fixtures');

const FICHE = '/adhesions-lots/';

test.describe('Éditeur visuel', () => {
  test('la fiche s\'ouvre en blocs : textes modifiables, éléments techniques verrouillés', async ({ visiteur }) => {
    await visiteur.ouvrir(FICHE);
    const fenetre = await visiteur.proposerUneModification();
    await expect(fenetre.editeur.locator('.editeur-editable').first()).toBeVisible();
    await expect(fenetre.editeur.locator('.editeur-verrou', { hasText: 'Accès' })).toBeVisible();
    await expect(fenetre.editeur.locator('.editeur-verrou [contenteditable]')).toHaveCount(0);
    await expect(fenetre.editeur.locator('.editeur-image img').first()).toBeVisible();
    await expect(fenetre.texte).toHaveCount(0);                                  // pas de Markdown à l'écran
  });

  test('gras, nouvelle liste et capture retirée deviennent une proposition propre', async ({ visiteur, moderation }) => {
    const resume = unique('Proposition depuis l\'éditeur visuel');
    await visiteur.ouvrir(FICHE);
    const fenetre = await visiteur.proposerUneModification();

    const para = fenetre.paragraphe('Par défaut, seuls les lots en cours');
    await fenetre.curseurALaFin(para);
    await visiteur.page.keyboard.type(' Pensez à ');
    await fenetre.fenetre.locator('.editeur-outil[title=Gras]').click();
    await visiteur.page.keyboard.type('actualiser');
    await fenetre.fenetre.locator('.editeur-outil[title=Gras]').click();
    await visiteur.page.keyboard.type(' la page.');

    await fenetre.ajouterApres(para, 'Liste à puces');
    await visiteur.page.keyboard.type('Premier point');
    await visiteur.page.keyboard.press('Enter');
    await visiteur.page.keyboard.type('Second point');

    const capture = fenetre.editeur.locator('.editeur-bloc--image', { hasText: /Capture : Lots —/ });
    await capture.hover();
    await capture.getByRole('button', { name: 'Supprimer' }).click();

    await fenetre.envoyer({ resume, pseudo: 'Sam' });
    await expect(fenetre.merci).toBeVisible();

    await moderation.afficher('Propositions');
    const diff = moderation.carte(resume).locator('.diff');
    await expect(diff.locator('.plus', { hasText: 'Pensez à **actualiser** la page.' })).toBeVisible();
    await expect(diff.locator('.plus', { hasText: '- Premier point' })).toBeVisible();
    await expect(diff.locator('.plus', { hasText: '- Second point' })).toBeVisible();
    await expect(diff.locator('.moins', { hasText: 'img/dep-lots-liste.png' })).toBeVisible();
    // rien d'autre n'a bougé : seulement 1 ligne retirée pour le paragraphe et 1 pour la capture
    await expect(diff.locator('.moins')).toHaveCount(2);
  });

  test('aller-retour par le mode avancé sans rien changer : refusé car identique', async ({ visiteur }) => {
    await visiteur.ouvrir('/facturation/');
    const fenetre = await visiteur.proposerUneModification();
    await fenetre.modeAvance();
    await fenetre.boutonModeAvance.click();                     // retour à l'éditeur visuel
    await fenetre.attendreLeTexte();
    await fenetre.envoyer({ resume: 'Aucun changement', pseudo: 'Sam' });
    await expect(fenetre.message).toHaveText("Vous n'avez rien modifié.");
  });

  test('une nouvelle fiche s\'écrit directement dans l\'éditeur visuel', async ({ visiteur, moderation }) => {
    const titre = unique('Fiche écrite sans Markdown');
    await visiteur.ouvrir(FICHE);
    const fenetre = await visiteur.proposerUneNouvelleFiche();
    await fenetre.titreFiche.fill(titre);
    await fenetre.editeur.locator('.editeur-paragraphe').first().click();
    await visiteur.page.keyboard.type('Voici la démarche.');
    await fenetre.envoyer({ resume: titre, pseudo: 'Sam' });
    await expect(fenetre.merci).toBeVisible();
    await moderation.afficher('Propositions');
    await expect(moderation.carte(titre).locator('.diff .plus', { hasText: 'Voici la démarche.' })).toBeVisible();
  });
});
