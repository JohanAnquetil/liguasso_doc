// Proposer une modification ou une nouvelle fiche, puis la transformer en pull request.
const { test, expect, unique } = require('../support/fixtures');

const FICHE = '/adhesions-lots/';
const PHRASE = "Pour voir l'ensemble des lots";

test.describe('Propositions de modification', () => {
  test('une modification acceptée devient une pull request', async ({ visiteur, moderation, github }) => {
    const resume = unique('Astuce sur les lots validés');
    await visiteur.ouvrir(FICHE);
    const fenetre = await visiteur.proposerUneModification();
    await expect(fenetre.texte).toHaveValue(/^# Lots/);
    await fenetre.remplacer(PHRASE, `Astuce : ${PHRASE.toLowerCase()}`);
    await fenetre.envoyer({ resume, pseudo: 'Sam' });
    await expect(fenetre.merci).toContainText('Merci');

    await moderation.afficher('Propositions');
    const carte = moderation.carte(resume);
    await expect(carte.locator('.diff .moins')).toContainText(PHRASE);
    await expect(carte.locator('.diff .plus')).toContainText('Astuce : pour voir');
    await moderation.accepterProposition(resume);

    const ecritures = await github.ecritures();
    expect(ecritures.map((e) => `${e.methode} ${e.chemin}`)).toEqual([
      'POST git/refs', 'PUT contents/docs-departemental/adhesions-lots.md', 'POST pulls']);
    const fichier = Buffer.from(ecritures[1].corps.content, 'base64').toString();
    expect(fichier).toContain('Astuce : pour voir');
    expect(ecritures[2].corps.title).toContain(resume);

    await moderation.afficher('Propositions acceptées');
    await expect(moderation.carte(resume).getByRole('link', { name: /pull request/ })).toBeVisible();
  });

  test('une nouvelle fiche part d\'un titre et d\'un texte libres', async ({ visiteur, moderation, github }) => {
    const titre = unique('Rembourser une adhésion');
    await visiteur.ouvrir(FICHE);
    const fenetre = await visiteur.proposerUneNouvelleFiche();
    await fenetre.titreFiche.fill(titre);
    await fenetre.texte.fill('1. Dans le menu, cliquez sur Facturation.\n2. Choisissez l\'association.');
    await fenetre.envoyer({ resume: titre, pseudo: 'Sam' });
    await expect(fenetre.merci).toBeVisible();

    await moderation.afficher('Propositions');
    await expect(moderation.carte(titre)).toContainText('Nouvelle fiche');
    await moderation.accepterProposition(titre);

    const [, fichier, pr] = await github.ecritures();
    expect(fichier.chemin).toMatch(/^contents\/docs-departemental\/rembourser-une-adhesion-[a-z0-9]+\.md$/);
    expect(Buffer.from(fichier.corps.content, 'base64').toString()).toMatch(new RegExp(`^# ${titre}\\n`));
    expect(pr.corps.body).toContain('ajouter au menu');
  });

  test('une proposition refusée ne touche pas à GitHub', async ({ visiteur, moderation, github }) => {
    const resume = unique('Proposition à refuser');
    await visiteur.ouvrir(FICHE);
    const fenetre = await visiteur.proposerUneModification();
    await fenetre.remplacer(PHRASE, 'Texte farfelu');
    await fenetre.envoyer({ resume, pseudo: 'Sam' });
    await expect(fenetre.merci).toBeVisible();

    await moderation.afficher('Propositions');
    await moderation.agir(resume, 'Refuser');
    expect(await github.ecritures()).toEqual([]);
    await moderation.afficher('Propositions refusées');
    await expect(moderation.carte(resume)).toBeVisible();
  });

  test('envoyer la fiche sans rien changer est refusé', async ({ visiteur }) => {
    await visiteur.ouvrir(FICHE);
    const fenetre = await visiteur.proposerUneModification();
    await fenetre.envoyer({ resume: 'Rien', pseudo: 'Sam' });
    await expect(fenetre.message).toHaveText("Vous n'avez rien modifié.");
  });
});
