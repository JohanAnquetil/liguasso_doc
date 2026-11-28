// Faux GitHub pour les tests e2e : sert les fiches du dépôt local (lecture) et garde
// en mémoire les écritures (branche, fichier, pull request), consultables sur /__ecritures.
import { createServer } from 'node:http';
import { readFileSync, existsSync } from 'node:fs';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const RACINE = resolve(dirname(fileURLToPath(import.meta.url)), '../../..');
const PORT = Number(process.env.PORT || 8099);
const VERSION = 'c'.repeat(40);
let ecritures = [];

const json = (res, code, corps) => {
  res.writeHead(code, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify(corps));
};

createServer((req, res) => {
  const url = new URL(req.url, 'http://x');
  if (url.pathname === '/__ecritures') {
    if (req.method === 'DELETE') ecritures = [];
    return json(res, 200, ecritures);
  }
  const [, , , , ...reste] = url.pathname.split('/');        // /repos/<o>/<d>/...
  const chemin = reste.join('/');
  if (req.method === 'GET') {
    if (chemin.startsWith('git/ref/heads/')) return json(res, 200, { object: { sha: VERSION } });
    if (chemin.startsWith('contents/')) {
      const fichier = resolve(RACINE, decodeURIComponent(chemin.slice('contents/'.length)));
      if (!fichier.startsWith(RACINE) || !existsSync(fichier)) return json(res, 404, {});
      return json(res, 200, { sha: 'b'.repeat(40), content: readFileSync(fichier).toString('base64') });
    }
    return json(res, 404, {});
  }
  let corps = '';
  req.on('data', (d) => (corps += d));
  req.on('end', () => {
    ecritures.push({ methode: req.method, chemin, corps: JSON.parse(corps || '{}') });
    json(res, 201, chemin === 'pulls' ? { html_url: `https://github.com/exemple/pull/${ecritures.length}` } : {});
  });
}).listen(PORT, '127.0.0.1', () => console.log(`Faux GitHub sur http://127.0.0.1:${PORT}`));
