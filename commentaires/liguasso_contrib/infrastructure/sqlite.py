"""Stockage SQLite : commentaires, propositions, limites de débit, défis anti-robot utilisés.

Le schéma est celui de la première version du service : les bases existantes restent valables.
"""
from __future__ import annotations

import sqlite3
import threading
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Optional

from ..domaine import modeles as m
from ..domaine.erreurs import TropDeDemandes

SCHEMA = """
CREATE TABLE IF NOT EXISTS commentaires (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  page TEXT NOT NULL,
  parent_id INTEGER REFERENCES commentaires(id) ON DELETE CASCADE,
  pseudo TEXT NOT NULL,
  texte TEXT NOT NULL,
  statut TEXT NOT NULL CHECK (statut IN ('attente', 'publie', 'masque', 'refuse')),
  equipe INTEGER NOT NULL DEFAULT 0,
  visiteur TEXT,
  ip TEXT,
  cree_le TEXT NOT NULL,
  modere_le TEXT
);
CREATE INDEX IF NOT EXISTS commentaires_page ON commentaires(page, statut);
CREATE TABLE IF NOT EXISTS likes (
  commentaire_id INTEGER NOT NULL REFERENCES commentaires(id) ON DELETE CASCADE,
  visiteur TEXT NOT NULL,
  PRIMARY KEY (commentaire_id, visiteur)
);
CREATE TABLE IF NOT EXISTS signalements (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  commentaire_id INTEGER NOT NULL REFERENCES commentaires(id) ON DELETE CASCADE,
  visiteur TEXT NOT NULL,
  ip TEXT NOT NULL,
  motif TEXT NOT NULL,
  precision TEXT,
  cree_le TEXT NOT NULL,
  traite INTEGER NOT NULL DEFAULT 0,
  UNIQUE (commentaire_id, visiteur)
);
CREATE TABLE IF NOT EXISTS defis_utilises (nonce TEXT PRIMARY KEY, expire INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS debits (cle TEXT NOT NULL, quand INTEGER NOT NULL);
CREATE INDEX IF NOT EXISTS debits_cle ON debits(cle, quand);
CREATE TABLE IF NOT EXISTS propositions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  type TEXT NOT NULL CHECK (type IN ('modification', 'nouvelle')),
  page TEXT NOT NULL,
  chemin TEXT NOT NULL,
  titre TEXT,
  pseudo TEXT NOT NULL,
  resume TEXT NOT NULL,
  texte_avant TEXT NOT NULL,
  texte TEXT NOT NULL,
  blob_sha TEXT,
  commit_sha TEXT,
  statut TEXT NOT NULL CHECK (statut IN ('attente', 'acceptee', 'refusee')),
  pr_url TEXT,
  visiteur TEXT,
  ip TEXT,
  cree_le TEXT NOT NULL,
  modere_le TEXT
);
"""

FILTRES_ADMIN = {
    "attente": "c.statut = 'attente'",
    "signales": "(c.statut = 'masque' OR EXISTS (SELECT 1 FROM signalements s WHERE s.commentaire_id = c.id AND s.traite = 0))",
    "publies": "c.statut = 'publie'",
    "refuses": "c.statut = 'refuse'",
}


class Base:
    """Connexion unique protégée par un verrou (un seul processus uvicorn)."""

    def __init__(self, fichier: Path | str):
        if str(fichier) != ":memory:":
            Path(fichier).parent.mkdir(parents=True, exist_ok=True)
        self._cnx = sqlite3.connect(str(fichier), check_same_thread=False)
        self._cnx.row_factory = sqlite3.Row
        self._cnx.execute("PRAGMA foreign_keys = ON")
        self._cnx.execute("PRAGMA journal_mode = WAL")
        self._cnx.executescript(SCHEMA)
        self._verrou = threading.Lock()

    @contextmanager
    def transaction(self):
        with self._verrou:
            try:
                yield self._cnx
                self._cnx.commit()
            except Exception:
                self._cnx.rollback()
                raise


def _commentaire(l: sqlite3.Row, likes: int = 0) -> m.Commentaire:
    return m.Commentaire(id=l["id"], page=l["page"], parent_id=l["parent_id"], pseudo=l["pseudo"],
                         texte=l["texte"], statut=l["statut"], cree_le=l["cree_le"],
                         equipe=bool(l["equipe"]), visiteur=l["visiteur"], likes=likes)


class DepotCommentairesSQLite:
    def __init__(self, base: Base):
        self.base = base

    def visibles(self, page, visiteur):
        with self.base.transaction() as db:
            lignes = db.execute(
                """SELECT c.*, (SELECT COUNT(*) FROM likes l WHERE l.commentaire_id = c.id) AS nb_likes
                   FROM commentaires c WHERE c.page = ?
                   AND (c.statut = 'publie' OR (c.statut = 'attente' AND c.visiteur = ?))
                   ORDER BY c.cree_le, c.id""", (page, visiteur or "-")).fetchall()
        return [_commentaire(l, l["nb_likes"]) for l in lignes]

    def aimes_par(self, visiteur, ids):
        if not ids:
            return set()
        with self.base.transaction() as db:
            marques = ",".join("?" * len(ids))
            return {r[0] for r in db.execute(
                f"SELECT commentaire_id FROM likes WHERE visiteur = ? AND commentaire_id IN ({marques})",
                [visiteur, *ids])}

    def trouver(self, cid):
        with self.base.transaction() as db:
            l = db.execute("SELECT * FROM commentaires WHERE id = ?", (cid,)).fetchone()
        return _commentaire(l) if l else None

    def ajouter(self, c, ip):
        with self.base.transaction() as db:
            return db.execute(
                """INSERT INTO commentaires (page, parent_id, pseudo, texte, statut, equipe, visiteur, ip,
                     cree_le, modere_le) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (c.page, c.parent_id, c.pseudo, c.texte, c.statut, int(c.equipe), c.visiteur, ip,
                 c.cree_le, c.cree_le if c.equipe else None)).lastrowid

    def basculer_like(self, cid, visiteur):
        with self.base.transaction() as db:
            if db.execute("DELETE FROM likes WHERE commentaire_id = ? AND visiteur = ?", (cid, visiteur)).rowcount:
                aime = False
            else:
                db.execute("INSERT INTO likes (commentaire_id, visiteur) VALUES (?, ?)", (cid, visiteur))
                aime = True
            n = db.execute("SELECT COUNT(*) FROM likes WHERE commentaire_id = ?", (cid,)).fetchone()[0]
        return aime, n

    def ajouter_signalement(self, cid, visiteur, ip, motif, precision, quand):
        with self.base.transaction() as db:
            try:
                db.execute("""INSERT INTO signalements (commentaire_id, visiteur, ip, motif, precision, cree_le)
                              VALUES (?, ?, ?, ?, ?, ?)""", (cid, visiteur, ip, motif, precision, quand))
                return True
            except sqlite3.IntegrityError:
                return False

    def nombre_signaleurs(self, cid):
        with self.base.transaction() as db:
            return db.execute("SELECT COUNT(DISTINCT ip) FROM signalements WHERE commentaire_id = ? AND traite = 0",
                              (cid,)).fetchone()[0]

    def changer_statut(self, cid, statut, quand, signalements_traites=False):
        with self.base.transaction() as db:
            db.execute("UPDATE commentaires SET statut = ?, modere_le = ? WHERE id = ?", (statut, quand, cid))
            if signalements_traites:
                db.execute("UPDATE signalements SET traite = 1 WHERE commentaire_id = ?", (cid,))

    def publier_si_attente(self, cid, quand):
        with self.base.transaction() as db:
            db.execute("UPDATE commentaires SET statut = 'publie', modere_le = ? WHERE id = ? AND statut = 'attente'",
                       (quand, cid))

    def supprimer(self, cid):
        with self.base.transaction() as db:
            db.execute("DELETE FROM commentaires WHERE id = ?", (cid,))

    def pour_admin(self, filtre):
        with self.base.transaction() as db:
            lignes = db.execute(f"""
                SELECT c.*, (SELECT COUNT(*) FROM likes l WHERE l.commentaire_id = c.id) AS nb_likes
                FROM commentaires c WHERE {FILTRES_ADMIN[filtre]}
                ORDER BY c.cree_le DESC, c.id DESC LIMIT 200""").fetchall()
            parents = {l["id"]: _commentaire(l) for l in db.execute(
                "SELECT * FROM commentaires WHERE id IN (SELECT parent_id FROM commentaires WHERE parent_id IS NOT NULL)")}
            signalements = {}
            for s in db.execute("SELECT * FROM signalements WHERE traite = 0 ORDER BY cree_le"):
                signalements.setdefault(s["commentaire_id"], []).append(
                    m.Signalement(motif=s["motif"], precision=s["precision"] or "", cree_le=s["cree_le"]))
        return [(_commentaire(l, l["nb_likes"]), parents.get(l["parent_id"]), signalements.get(l["id"], []))
                for l in lignes]

    def compteurs(self):
        with self.base.transaction() as db:
            return {f: db.execute(f"SELECT COUNT(*) FROM commentaires c WHERE {c}").fetchone()[0]
                    for f, c in FILTRES_ADMIN.items()}


def _proposition(l: sqlite3.Row) -> m.Proposition:
    return m.Proposition(**{k: l[k] for k in (
        "id", "type", "page", "chemin", "titre", "pseudo", "resume", "texte_avant", "texte",
        "blob_sha", "commit_sha", "statut", "pr_url", "cree_le")})


class DepotPropositionsSQLite:
    def __init__(self, base: Base):
        self.base = base

    def ajouter(self, p, visiteur, ip):
        with self.base.transaction() as db:
            return db.execute(
                """INSERT INTO propositions (type, page, chemin, titre, pseudo, resume, texte_avant, texte,
                     blob_sha, commit_sha, statut, visiteur, ip, cree_le)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (p.type, p.page, p.chemin, p.titre, p.pseudo, p.resume, p.texte_avant, p.texte,
                 p.blob_sha, p.commit_sha, p.statut, visiteur, ip, p.cree_le)).lastrowid

    def trouver(self, pid):
        with self.base.transaction() as db:
            l = db.execute("SELECT * FROM propositions WHERE id = ?", (pid,)).fetchone()
        return _proposition(l) if l else None

    def lister(self, statut):
        with self.base.transaction() as db:
            return [_proposition(l) for l in db.execute(
                "SELECT * FROM propositions WHERE statut = ? ORDER BY cree_le DESC, id DESC LIMIT 100", (statut,))]

    def accepter(self, pid, pr_url, quand):
        with self.base.transaction() as db:
            db.execute("UPDATE propositions SET statut = 'acceptee', pr_url = ?, modere_le = ? WHERE id = ?",
                       (pr_url, quand, pid))

    def refuser(self, pid, quand):
        with self.base.transaction() as db:
            return db.execute("UPDATE propositions SET statut = 'refusee', modere_le = ? WHERE id = ? AND statut = 'attente'",
                              (quand, pid)).rowcount > 0


class LimiteurSQLite:
    def __init__(self, base: Base, horloge=time.time):
        self.base, self.horloge = base, horloge

    def consommer(self, cle, maximum, fenetre):
        t = int(self.horloge())
        with self.base.transaction() as db:
            db.execute("DELETE FROM debits WHERE quand < ?", (t - 86400,))
            n = db.execute("SELECT COUNT(*) FROM debits WHERE cle = ? AND quand > ?", (cle, t - fenetre)).fetchone()[0]
            if n >= maximum:
                raise TropDeDemandes()
            db.execute("INSERT INTO debits (cle, quand) VALUES (?, ?)", (cle, t))


class DefisUtilisesSQLite:
    """Mémorise les preuves anti-robot déjà utilisées, le temps de leur validité."""

    def __init__(self, base: Base, horloge=time.time):
        self.base, self.horloge = base, horloge

    def premiere_utilisation(self, nonce: str, duree: int) -> bool:
        t = int(self.horloge())
        with self.base.transaction() as db:
            db.execute("DELETE FROM defis_utilises WHERE expire < ?", (t,))
            try:
                db.execute("INSERT INTO defis_utilises (nonce, expire) VALUES (?, ?)", (nonce, t + duree))
                return True
            except sqlite3.IntegrityError:
                return False
