// La page de modération.
const { test, expect, unique } = require('../support/fixtures');
const { PageModeration } = require('../pages/PageModeration');

const FICHE = '/adhesions-tipo/';

test.describe('Modération', () => {
  test('un mauvais mot de passe est refusé', async ({ page }) => {
    const moderation = new PageModeration(page);
    await moderation.connecter('pas-le-bon');
    await expect(moderation.erreurConnexion).toHaveText('Mot de passe incorrect.');
  });

  test('répondre au nom de l\'équipe publie la question et la réponse, avec un badge', async ({ visiteur, autreVisiteur, moderation }) => {
    const question = unique('Où trouver les participants TIPO ?');
    const reponse = unique('Dans le menu Adhésion');
    await visiteur.ouvrir(FICHE);
    await visiteur.commentaires.ecrire('Camille', question);

    await moderation.afficher('À valider');
    await moderation.repondreAuNomDeLEquipe(question, reponse);

    await autreVisiteur.ouvrir(FICHE);
    const fil = autreVisiteur.commentaires.commentaire(question);
    await expect(fil).toBeVisible();
    await expect(fil.locator('.commentaires-reponses .commentaire-equipe')).toHaveText('Équipe');
    await expect(fil.locator('.commentaires-reponses')).toContainText(reponse);
  });

  test('un commentaire refusé disparaît, même pour son auteur', async ({ visiteur, moderation }) => {
    const texte = unique('Hors sujet');
    await visiteur.ouvrir(FICHE);
    await visiteur.commentaires.ecrire('Camille', texte);
    await moderation.afficher('À valider');
    await moderation.agir(texte, 'Refuser');
    await moderation.afficher('Refusés');
    await expect(moderation.carte(texte)).toBeVisible();

    await visiteur.ouvrir(FICHE);
    await expect(visiteur.commentaires.commentaire(texte)).toHaveCount(0);
  });

  test('supprimer efface définitivement', async ({ visiteur, moderation }) => {
    const texte = unique('À effacer');
    await visiteur.ouvrir(FICHE);
    await visiteur.commentaires.ecrire('Camille', texte);
    await moderation.afficher('À valider');
    await moderation.agir(texte, 'Supprimer');
    for (const onglet of ['À valider', 'Publiés', 'Refusés']) {
      await moderation.afficher(onglet);
      await expect(moderation.carte(texte)).toHaveCount(0);
    }
  });
});
