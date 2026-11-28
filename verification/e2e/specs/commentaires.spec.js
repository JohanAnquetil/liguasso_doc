// Commenter, répondre, liker, signaler : le point de vue des visiteurs.
const { test, expect, unique } = require('../support/fixtures');

const FICHE = '/adhesions-lots/';

test.describe('Commentaires', () => {
  test('un commentaire attend la validation, puis devient visible par tous', async ({ visiteur, autreVisiteur, moderation }) => {
    const texte = unique('Astuce : augmentez le nombre de lignes');
    await visiteur.ouvrir(FICHE);
    await visiteur.commentaires.ecrire('Camille', texte);

    await expect(visiteur.commentaires.message).toHaveText(/sera visible après validation/);
    await expect(visiteur.commentaires.commentaire(texte)).toContainText('En attente de validation');
    await autreVisiteur.ouvrir(FICHE);
    await expect(autreVisiteur.commentaires.commentaire(texte)).toHaveCount(0);

    await moderation.afficher('À valider');
    await moderation.agir(texte, 'Publier');

    await autreVisiteur.ouvrir(FICHE);
    await expect(autreVisiteur.commentaires.commentaire(texte)).toContainText('Camille');
    await expect(autreVisiteur.commentaires.commentaire(texte)).not.toContainText('En attente');
  });

  test('on peut liker puis retirer son like', async ({ visiteur, autreVisiteur, moderation }) => {
    const texte = unique('Merci pour la fiche');
    await visiteur.ouvrir(FICHE);
    await visiteur.commentaires.ecrire('Camille', texte);
    await moderation.afficher('À valider');
    await moderation.agir(texte, 'Publier');

    await autreVisiteur.ouvrir(FICHE);
    const like = autreVisiteur.commentaires.commentaire(texte).locator('.commentaire-like').first();
    await autreVisiteur.commentaires.liker(texte);
    await expect(like).toHaveText(/1/);
    await expect(like).toHaveAttribute('aria-pressed', 'true');
    await autreVisiteur.commentaires.liker(texte);
    await expect(like).toHaveText(/0/);
  });

  test('une réponse s\'affiche sous le commentaire, après validation', async ({ visiteur, autreVisiteur, moderation }) => {
    const question = unique('Comment valider plus de 100 adhésions ?');
    const reponse = unique('Créez plusieurs lots');
    await visiteur.ouvrir(FICHE);
    await visiteur.commentaires.ecrire('Camille', question);
    await moderation.afficher('À valider');
    await moderation.agir(question, 'Publier');

    await autreVisiteur.ouvrir(FICHE);
    await autreVisiteur.commentaires.repondre(question, 'Dominique', reponse);
    await moderation.afficher('À valider');
    await expect(moderation.carte(reponse)).toContainText(`En réponse à Camille`);
    await moderation.agir(reponse, 'Publier');

    await visiteur.ouvrir(FICHE);
    const fil = visiteur.commentaires.commentaire(question);
    await expect(fil.locator('.commentaires-reponses')).toContainText(reponse);
  });

  test('un commentaire signalé arrive dans l\'onglet « Signalés »', async ({ visiteur, autreVisiteur, moderation }) => {
    const texte = unique('Information douteuse');
    await visiteur.ouvrir(FICHE);
    await visiteur.commentaires.ecrire('Camille', texte);
    await expect(visiteur.commentaires.commentaire(texte).getByRole('button', { name: 'Signaler' })).toHaveCount(0);
    await moderation.afficher('À valider');
    await moderation.agir(texte, 'Publier');

    await autreVisiteur.ouvrir(FICHE);
    await autreVisiteur.commentaires.signaler(texte, 'faux');

    await moderation.afficher('Signalés');
    await expect(moderation.carte(texte)).toContainText('Information fausse');
  });

  test('un robot qui remplit le champ piège croit avoir réussi, sans rien publier', async ({ visiteur, page, moderation }) => {
    const texte = unique('Achetez maintenant');
    await visiteur.ouvrir(FICHE);
    await page.locator('input[name=site_web]').evaluate((champ) => { champ.value = 'http://spam.example'; });
    await visiteur.commentaires.ecrire('Robot', texte);
    await expect(visiteur.commentaires.message).toHaveText(/Merci/);
    await moderation.afficher('À valider');
    await expect(moderation.carte(texte)).toHaveCount(0);
  });

  test('pseudo et commentaire sont obligatoires', async ({ visiteur }) => {
    await visiteur.ouvrir(FICHE);
    await visiteur.commentaires.ecrire('', 'Sans pseudo');
    await expect(visiteur.commentaires.message).toHaveText('Indiquez un pseudo et votre commentaire.');
  });
});
