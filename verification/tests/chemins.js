// Lit les encadrés « Accès » des guides et en extrait les chemins de menu.
//
//   !!! chemin "Accès"
//       Dans le menu, cliquez sur **Adhésion**, puis sur **Lots**, puis sur le bouton **Nouveau lot**.
//
// Un chemin = les intitulés en gras qui suivent « dans le menu », jusqu'au mot « bouton ».
// Les lignes sans « dans le menu » (ex. « depuis le tableau de bord ») ne sont pas vérifiées.
const fs = require('fs');
const path = require('path');

const RACINE = path.resolve(__dirname, '..', '..');
const GRAS = /\*\*([^*]+)\*\*/g;

function cheminDeLaLigne(ligne) {
  const debut = ligne.search(/dans le menu/i);
  if (debut === -1) return null;
  const suite = ligne.slice(debut).split(/\bbouton\b/)[0];
  const chemin = [...suite.matchAll(GRAS)].map(m => m[1].trim());
  return chemin.length ? chemin : null;
}

function cheminsDuGuide(dossier) {
  const dir = path.join(RACINE, dossier);
  const resultat = [];
  for (const fichier of fs.readdirSync(dir).filter(f => f.endsWith('.md')).sort()) {
    const lignes = fs.readFileSync(path.join(dir, fichier), 'utf8').split('\n');
    const debut = lignes.findIndex(l => /^!!! chemin\b/.test(l));
    if (debut === -1) continue;
    for (let i = debut + 1; i < lignes.length && /^( {4}|\s*$)/.test(lignes[i]); i++) {
      const chemin = cheminDeLaLigne(lignes[i]);
      if (chemin) resultat.push({ fichier, chemin });
    }
  }
  return resultat;
}

function pagesSansChemin(dossier) {
  const dir = path.join(RACINE, dossier);
  return fs.readdirSync(dir).filter(f => f.endsWith('.md'))
    .filter(f => !/^!!! chemin\b/m.test(fs.readFileSync(path.join(dir, f), 'utf8')));
}

module.exports = { cheminsDuGuide, pagesSansChemin };
