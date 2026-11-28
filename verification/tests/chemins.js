// Lit les encadrés « Accès » des guides et en extrait les chemins de menu.
//
//   !!! chemin "Accès"
//       **Adhésion** › **Lots**, puis bouton **Nouveau lot**
//
// Un chemin = une suite d'intitulés en gras reliés par « › ».
// Les lignes sans « › » (ex. « depuis le tableau de bord ») ne sont pas vérifiées.
const fs = require('fs');
const path = require('path');

const RACINE = path.resolve(__dirname, '..', '..');
const CHAINE = /\*\*[^*]+\*\*(?:\s*›\s*\*\*[^*]+\*\*)+/g;

function cheminsDuGuide(dossier) {
  const dir = path.join(RACINE, dossier);
  const resultat = [];
  for (const fichier of fs.readdirSync(dir).filter(f => f.endsWith('.md')).sort()) {
    const lignes = fs.readFileSync(path.join(dir, fichier), 'utf8').split('\n');
    const debut = lignes.findIndex(l => /^!!! chemin\b/.test(l));
    if (debut === -1) continue;
    for (let i = debut + 1; i < lignes.length && /^( {4}|\s*$)/.test(lignes[i]); i++) {
      for (const m of lignes[i].match(CHAINE) || []) {
        resultat.push({ fichier, chemin: m.split('›').map(s => s.replace(/\*\*/g, '').trim()) });
      }
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
