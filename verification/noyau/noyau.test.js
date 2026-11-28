// Règles pures des scripts du guide (commun/javascripts/noyau.js) :  npm run test:noyau
const test = require('node:test');
const assert = require('node:assert/strict');
const N = require('../../commun/javascripts/noyau.js');

test('guide d\'après le nom du site', () => {
  assert.equal(N.guideDuSite("Guide Ligu'asso — Associations"), 'association');
  assert.equal(N.guideDuSite("Guide Ligu'asso — Fédérations départementales"), 'departemental');
  assert.equal(N.guideDuSite("[TEST] Guide Ligu'asso — bac à sable"), 'test');
});

test('clé de page', () => {
  assert.equal(N.clePage('/departemental/adhesions-lots/', '/departemental/', ''), 'departemental/adhesions-lots');
  assert.equal(N.clePage('/association/', '/association/', ''), 'association');
  assert.equal(N.clePage('/adhesions-lots/', '/', "Guide Ligu'asso — Associations"), 'association/adhesions-lots');
  assert.ok(N.estAccueil('association') && !N.estAccueil('association/x'));
});

test('dates relatives', () => {
  const t = Date.parse('2026-11-28T10:00:00Z');
  assert.equal(N.quand('2026-11-28T09:55:00Z', t), 'il y a 5 min');
  assert.equal(N.quand('2026-11-28T07:00:00Z', t), 'il y a 3 h');
  assert.match(N.quand('2026-11-12T10:00:00Z', t), /^le 12 novembre 2026$/);
});

test('impression et PDF', () => {
  assert.equal(N.publicDuGuide("Guide Ligu'asso — Associations"), 'Gestion Associative');
  assert.equal(N.publicDuGuide('[TEST] bac à sable'), 'Gestion Départementale');
  assert.match(N.dateEntete(true, new Date(2026, 10, 28)), /^Mis à jour le 28\/11\/2026$/);
  assert.match(N.dateEntete(false, new Date(2026, 10, 28)), /^Extrait le /);
  assert.equal(N.basDePage('Adhésions', 'Lots'), 'Adhésions › Lots');
  assert.equal(N.basDePage('Statistiques', 'Statistiques'), 'Statistiques');
  assert.equal(N.nomFichierPdf('Lots : valider / refuser?'), "Ligu'asso - Lots  valider  refuser.pdf");
});

test('place dans le menu', () => {
  const X = N.NOUVELLE;
  assert.deepEqual(N.placeDansLeMenu({ rubrique: '' }), { menu_rubrique: '', menu_sous_rubrique: '', menu_libelle: '' });
  assert.deepEqual(N.placeDansLeMenu({ rubrique: 'A', sousRubrique: '', libelle: ' L ' }), { menu_rubrique: 'A', menu_sous_rubrique: '', menu_libelle: 'L' });
  assert.deepEqual(N.placeDansLeMenu({ rubrique: X, nomRubrique: ' R ', sousRubrique: X, nomSousRubrique: 'S' }), { menu_rubrique: 'R', menu_sous_rubrique: 'S', menu_libelle: '' });
  assert.ok(N.placeDansLeMenu({ rubrique: X, nomRubrique: ' ' }).erreur);
  assert.ok(N.placeDansLeMenu({ rubrique: 'A', sousRubrique: X, nomSousRubrique: '' }).erreur);
});

test('repère vidéo dans le menu', () => {
  const fiches = N.fichesAvecVideo([{ fiche: 'adhesions-import/' }], 'https://g.fr/departemental/');
  assert.ok(N.lienAvecVideo('../adhesions-import/', false, 'https://g.fr/departemental/lots/', fiches));
  assert.ok(!N.lienAvecVideo('#etape', false, 'https://g.fr/departemental/adhesions-import/', fiches));
  assert.ok(!N.lienAvecVideo('../adhesions-import/', true, 'https://g.fr/departemental/lots/', fiches));
  assert.ok(!N.lienAvecVideo('../lots/', false, 'https://g.fr/departemental/x/', fiches));
});
