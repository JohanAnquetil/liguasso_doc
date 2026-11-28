// Tests du modèle de l'éditeur visuel (commun/javascripts/editeur-fiche.js) :  npm run test:editeur
// 1. Lire puis réécrire chaque fiche du dépôt redonne exactement le même texte.
// 2. Modifier un bloc ne change que ce bloc.
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const E = require('../../commun/javascripts/editeur-fiche.js');

const RACINE = path.resolve(__dirname, '..', '..');
const DOSSIERS = ['docs-association', 'docs-departemental', 'docs-test', 'commun/partiels', 'brouillons'];
const fiches = DOSSIERS.flatMap((d) => fs.existsSync(path.join(RACINE, d))
  ? fs.readdirSync(path.join(RACINE, d)).filter((f) => f.endsWith('.md')).map((f) => path.join(d, f)) : []);

const lireFiche = (f) => fs.readFileSync(path.join(RACINE, f), 'utf8');
const lignesChangees = (a, b) => {
  const x = a.split('\n'), y = b.split('\n');
  const n = Math.max(x.length, y.length);
  return Array.from({ length: n }, (_, i) => i).filter((i) => x[i] !== y[i]);
};
const tousLesBlocs = (conteneur, acc = []) => {
  for (const b of conteneur.blocs) {
    acc.push(b);
    if (b.type === 'encadre') tousLesBlocs(b.enfants, acc);
    if (b.type === 'onglets') b.onglets.forEach((o) => tousLesBlocs(o.enfants, acc));
    if (b.type === 'liste') b.elements.forEach((e) => e.enfants && tousLesBlocs(e.enfants, acc));
  }
  return acc;
};

test('le dépôt contient bien des fiches à tester', () => {
  assert.ok(fiches.length > 60, `${fiches.length} fiches seulement`);
});

for (const f of fiches) {
  test(`relecture à l'identique : ${f}`, () => {
    const texte = lireFiche(f);
    assert.equal(E.ecrire(E.lire(texte)), texte);
  });
}

test('chaque fiche a des blocs modifiables, et l\'encadré « Accès » est verrouillé', () => {
  for (const f of fiches.filter((x) => x.startsWith('docs-departemental/'))) {
    const blocs = tousLesBlocs(E.lire(lireFiche(f)));
    assert.ok(blocs.some((b) => ['paragraphe', 'liste', 'titre'].includes(b.type)), f);
    for (const b of blocs.filter((b) => /^!!! chemin/.test(b.brut || ''))) assert.equal(b.type, 'verrou', f);
  }
});

test('modifier un paragraphe ne change que sa ligne', () => {
  const texte = lireFiche('docs-departemental/adhesions-lots.md');
  const m = E.lire(texte);
  const p = tousLesBlocs(m).find((b) => b.type === 'paragraphe' && b.texte.startsWith('Par défaut'));
  p.texte = 'Par défaut, seuls les lots **en cours** sont affichés.'; p.modifie = true;
  const apres = E.ecrire(m);
  assert.deepEqual(lignesChangees(texte, apres).length, 1);
  assert.match(apres, /seuls les lots \*\*en cours\*\* sont affichés\./);
});

test('modifier un élément de liste avec captures et encadré imbriqués ne change que sa ligne', () => {
  const texte = lireFiche('docs-departemental/adhesions-valider.md');
  const m = E.lire(texte);
  const liste = m.blocs.flatMap((b) => tousLesBlocs({ blocs: [b] })).find((b) => b.type === 'liste' && b.numerotee);
  liste.elements[0].texte += ' (modifié)'; liste.modifie = true;
  const apres = E.ecrire(m);
  const changees = lignesChangees(texte, apres);
  assert.equal(changees.length, 1, changees.map((i) => `${texte.split('\n')[i]} → ${apres.split('\n')[i]}`).join('\n'));
  assert.equal(E.ecrire(E.lire(apres)), apres);
});

test('modifier un texte dans un onglet ne change que lui', () => {
  const texte = lireFiche('docs-departemental/adhesions-import.md');
  const m = E.lire(texte);
  const onglets = m.blocs.find((b) => b.type === 'onglets');
  const p = onglets.onglets[0].enfants.blocs.find((b) => b.type === 'paragraphe');
  p.texte = p.texte.replace('Étape 1.', 'Étape 1 (modifiée).'); p.modifie = true; onglets.modifie = true;
  const apres = E.ecrire(m);
  assert.equal(lignesChangees(texte, apres).length, 1);
});

test('ajouter des blocs neufs', () => {
  const m = E.lire('# Titre\n\nTexte.\n');
  const encadre = E.nouveauBloc('tip');
  encadre.titre = 'Bon à savoir';
  encadre.enfants.blocs[0].texte = 'Pensez à enregistrer.';
  const liste = E.nouveauBloc('numeros');
  liste.elements[0].texte = 'Première étape';
  liste.elements.push({ ecart: [], marque: '1.', texte: 'Deuxième étape', enfants: null });
  m.blocs.push(encadre, liste);
  assert.equal(E.ecrire(m), '# Titre\n\nTexte.\n\n!!! tip "Bon à savoir"\n    Pensez à enregistrer.\n\n1. Première étape\n2. Deuxième étape\n');
});

test('supprimer un bloc', () => {
  const m = E.lire('Un.\n\nDeux.\n\nTrois.\n');
  m.blocs.splice(1, 1);
  assert.equal(E.ecrire(m), 'Un.\n\nTrois.\n');
});

test('nouvelle fiche vide', () => {
  assert.equal(E.ecrire(E.lire('')), '');
});

test('texte enrichi : Markdown vers HTML', () => {
  assert.equal(E.versHtml('Cliquez sur **Valider**, voir [Lots](adhesions-lots.md) et `page.pdf`.'),
    'Cliquez sur <strong>Valider</strong>, voir <a href="adhesions-lots.md">Lots</a> et <code>page.pdf</code>.');
  assert.equal(E.versHtml('astérisque **\\***'), 'astérisque <strong>&#42;</strong>');
  assert.equal(E.versHtml('<script>'), '&lt;script&gt;');
});
