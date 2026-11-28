"""Service de commentaires du guide Ligu'asso.

- Commentaires anonymes (pseudo seul), visibles seulement après validation d'un admin.
- Anti-bot ALTCHA (preuve de travail calculée par le navigateur, sans service tiers),
  champ piège et limite de débit par adresse IP.
- Likes, réponses (un niveau), signalements. Un commentaire signalé par plusieurs
  personnes est masqué en attendant qu'un admin tranche.
- Page d'administration : /api/commentaires/admin (mot de passe ADMIN_MOT_DE_PASSE).

Aucune adresse IP n'est stockée en clair : seulement une empreinte salée, pour limiter
les abus. Variables d'environnement : voir README.md à côté de ce fichier.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import hmac
import os
import re
import secrets
import sqlite3
import threading
import time
import unicodedata
from contextlib import contextmanager
from pathlib import Path
from typing import Optional

import altcha
from fastapi import APIRouter, Depends, FastAPI, Header, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from itsdangerous import BadSignature, SignatureExpired, TimestampSigner
from pydantic import BaseModel, Field

# --- Réglages -----------------------------------------------------------------------------

DONNEES = Path(os.environ.get("DONNEES", "/donnees"))
ADMIN_MOT_DE_PASSE = os.environ.get("ADMIN_MOT_DE_PASSE", "")
CORS_ORIGINES = [o for o in os.environ.get("CORS_ORIGINES", "").replace(",", " ").split() if o]
NOM_EQUIPE = "Équipe Ligu'asso"

SEUIL_SIGNALEMENTS = 3          # signalements distincts avant masquage automatique
MAX_COMMENTAIRES_PAR_IP = 5     # par fenêtre de 10 minutes
MAX_ACTIONS_PAR_IP = 60         # likes et signalements, par heure
MAX_CONNEXIONS_ADMIN = 5        # tentatives par fenêtre de 15 minutes
DUREE_SESSION_ADMIN = 8 * 3600
DUREE_DEFI = 10 * 60
COUT_DEFI = int(os.environ.get("ALTCHA_COUT", "5000"))

PAGE_VALIDE = re.compile(r"^[a-z0-9][a-z0-9/_-]{0,199}$")
MOTIFS = {"spam": "Spam ou publicité", "propos": "Propos inappropriés",
          "faux": "Information fausse", "autre": "Autre"}


def _secret() -> str:
    """Secret de signature : variable SECRET, sinon créé une fois et gardé avec les données."""
    if os.environ.get("SECRET"):
        return os.environ["SECRET"]
    DONNEES.mkdir(parents=True, exist_ok=True)
    fichier = DONNEES / "secret"
    if not fichier.exists():
        fichier.write_text(secrets.token_hex(32))
        fichier.chmod(0o600)
    return fichier.read_text().strip()


SECRET = _secret()
signeur = TimestampSigner(SECRET, salt="admin")

# --- Base de données -----------------------------------------------------------------------

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
"""

_verrou = threading.Lock()


def base() -> sqlite3.Connection:
    DONNEES.mkdir(parents=True, exist_ok=True)
    cnx = sqlite3.connect(DONNEES / "commentaires.sqlite3", check_same_thread=False)
    cnx.row_factory = sqlite3.Row
    cnx.execute("PRAGMA foreign_keys = ON")
    cnx.execute("PRAGMA journal_mode = WAL")
    cnx.executescript(SCHEMA)
    return cnx


_cnx = base()


@contextmanager
def transaction():
    with _verrou:
        try:
            yield _cnx
            _cnx.commit()
        except Exception:
            _cnx.rollback()
            raise


def maintenant() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def empreinte(valeur: str, sel: str) -> str:
    return hmac.new(SECRET.encode(), f"{sel}:{valeur}".encode(), hashlib.sha256).hexdigest()[:32]


def ip_client(request: Request) -> str:
    return empreinte(request.client.host if request.client else "inconnue", "ip")


def limiter(cle: str, maximum: int, fenetre: int) -> None:
    """Limite de débit simple, stockée en base. Lève 429 au-delà de *maximum* par *fenetre* s."""
    t = int(time.time())
    with transaction() as db:
        db.execute("DELETE FROM debits WHERE quand < ?", (t - 86400,))
        n = db.execute("SELECT COUNT(*) FROM debits WHERE cle = ? AND quand > ?", (cle, t - fenetre)).fetchone()[0]
        if n >= maximum:
            raise HTTPException(429, "Trop de demandes. Réessayez dans quelques minutes.")
        db.execute("INSERT INTO debits (cle, quand) VALUES (?, ?)", (cle, t))


def nettoyer(texte: str, maximum: int) -> str:
    texte = unicodedata.normalize("NFC", texte)
    texte = "".join(c for c in texte if c in "\n\t" or unicodedata.category(c)[0] != "C")
    texte = re.sub(r"\n{3,}", "\n\n", texte.replace("\r", "")).strip()
    return texte[:maximum]


# --- Anti-bot ALTCHA -----------------------------------------------------------------------

def creer_defi() -> dict:
    return altcha.create_challenge(
        algorithm="PBKDF2/SHA-256",
        cost=COUT_DEFI,
        counter=secrets.randbelow(40) + 10,
        expires_at=int(time.time()) + DUREE_DEFI,
        hmac_secret=SECRET,
        hmac_key_secret=SECRET + ":cle",
    ).to_dict()


def verifier_altcha(charge: str) -> None:
    if not charge:
        raise HTTPException(400, "Vérification anti-robot manquante.")
    try:
        resultat = altcha.verify_solution(charge, SECRET, hmac_key_secret=SECRET + ":cle")
        nonce = altcha.Payload.from_base64(charge).challenge.parameters.nonce
    except Exception:
        raise HTTPException(400, "Vérification anti-robot invalide.")
    if not resultat.verified:
        raise HTTPException(400, "Vérification anti-robot expirée ou invalide. Réessayez.")
    t = int(time.time())
    with transaction() as db:
        db.execute("DELETE FROM defis_utilises WHERE expire < ?", (t,))
        try:
            db.execute("INSERT INTO defis_utilises (nonce, expire) VALUES (?, ?)", (nonce, t + DUREE_DEFI))
        except sqlite3.IntegrityError:
            raise HTTPException(400, "Vérification anti-robot déjà utilisée. Réessayez.")


# --- Modèles -------------------------------------------------------------------------------

class NouveauCommentaire(BaseModel):
    page: str
    pseudo: str = Field(min_length=1, max_length=40)
    texte: str = Field(min_length=1, max_length=2000)
    parent_id: Optional[int] = None
    altcha: str = ""
    site_web: str = ""          # champ piège : invisible pour les humains


class Signalement(BaseModel):
    motif: str
    precision: str = Field("", max_length=300)
    altcha: str = ""


class Reponse(BaseModel):
    texte: str = Field(min_length=1, max_length=2000)


class Connexion(BaseModel):
    mot_de_passe: str


def visiteur_requis(x_visiteur: str = Header("")) -> str:
    if not re.fullmatch(r"[A-Za-z0-9_-]{16,64}", x_visiteur or ""):
        raise HTTPException(400, "Identifiant de visiteur manquant.")
    return empreinte(x_visiteur, "visiteur")


def visiteur_facultatif(x_visiteur: str = Header("")) -> Optional[str]:
    return empreinte(x_visiteur, "visiteur") if re.fullmatch(r"[A-Za-z0-9_-]{16,64}", x_visiteur or "") else None


def en_json(ligne: sqlite3.Row, visiteur: Optional[str], likes: dict, aime: set) -> dict:
    return {
        "id": ligne["id"],
        "parent_id": ligne["parent_id"],
        "pseudo": ligne["pseudo"],
        "texte": ligne["texte"],
        "cree_le": ligne["cree_le"],
        "equipe": bool(ligne["equipe"]),
        "en_attente": ligne["statut"] == "attente",
        "likes": likes.get(ligne["id"], 0),
        "aime": ligne["id"] in aime,
        "de_moi": visiteur is not None and ligne["visiteur"] == visiteur,
    }


# --- API publique --------------------------------------------------------------------------

api = APIRouter(prefix="/api/commentaires")


@api.get("/defi")
def defi(response: Response):
    response.headers["Cache-Control"] = "no-store"
    return creer_defi()


@api.get("")
def lister(page: str, visiteur: Optional[str] = Depends(visiteur_facultatif)):
    if not PAGE_VALIDE.match(page):
        raise HTTPException(400, "Page invalide.")
    with transaction() as db:
        lignes = db.execute(
            """SELECT * FROM commentaires WHERE page = ?
               AND (statut = 'publie' OR (statut = 'attente' AND visiteur = ?))
               ORDER BY cree_le, id""", (page, visiteur or "-")).fetchall()
        ids = [l["id"] for l in lignes] or [0]
        marques = ",".join("?" * len(ids))
        likes = dict(db.execute(f"SELECT commentaire_id, COUNT(*) FROM likes WHERE commentaire_id IN ({marques}) GROUP BY commentaire_id", ids).fetchall())
        aime = {r[0] for r in db.execute(f"SELECT commentaire_id FROM likes WHERE visiteur = ? AND commentaire_id IN ({marques})", [visiteur or "-", *ids])}
    visibles = {l["id"] for l in lignes}
    # Une réponse dont le parent n'est pas visible n'est pas affichée
    return [en_json(l, visiteur, likes, aime) for l in lignes if not l["parent_id"] or l["parent_id"] in visibles]


@api.post("", status_code=201)
def commenter(donnees: NouveauCommentaire, request: Request, visiteur: str = Depends(visiteur_requis)):
    if donnees.site_web:
        # Robot : on fait comme si tout allait bien, sans rien enregistrer
        return {"id": 0, "en_attente": True}
    if not PAGE_VALIDE.match(donnees.page):
        raise HTTPException(400, "Page invalide.")
    pseudo, texte = nettoyer(donnees.pseudo, 40), nettoyer(donnees.texte, 2000)
    if not pseudo or not texte:
        raise HTTPException(400, "Le pseudo et le commentaire sont obligatoires.")
    ip = ip_client(request)
    limiter(f"commentaire:{ip}", MAX_COMMENTAIRES_PAR_IP, 600)
    verifier_altcha(donnees.altcha)
    with transaction() as db:
        parent_id = donnees.parent_id
        if parent_id is not None:
            parent = db.execute("SELECT id, parent_id, page, statut FROM commentaires WHERE id = ?", (parent_id,)).fetchone()
            if not parent or parent["page"] != donnees.page or parent["statut"] != "publie":
                raise HTTPException(400, "Le commentaire auquel vous répondez n'existe plus.")
            parent_id = parent["parent_id"] or parent["id"]   # un seul niveau de réponses
        cur = db.execute(
            """INSERT INTO commentaires (page, parent_id, pseudo, texte, statut, visiteur, ip, cree_le)
               VALUES (?, ?, ?, ?, 'attente', ?, ?, ?)""",
            (donnees.page, parent_id, pseudo, texte, visiteur, ip, maintenant()))
    return {"id": cur.lastrowid, "en_attente": True}


@api.post("/{cid}/like")
def liker(cid: int, request: Request, visiteur: str = Depends(visiteur_requis)):
    limiter(f"action:{ip_client(request)}", MAX_ACTIONS_PAR_IP, 3600)
    with transaction() as db:
        if not db.execute("SELECT 1 FROM commentaires WHERE id = ? AND statut = 'publie'", (cid,)).fetchone():
            raise HTTPException(404, "Commentaire introuvable.")
        if db.execute("DELETE FROM likes WHERE commentaire_id = ? AND visiteur = ?", (cid, visiteur)).rowcount == 0:
            db.execute("INSERT INTO likes (commentaire_id, visiteur) VALUES (?, ?)", (cid, visiteur))
            aime = True
        else:
            aime = False
        n = db.execute("SELECT COUNT(*) FROM likes WHERE commentaire_id = ?", (cid,)).fetchone()[0]
    return {"aime": aime, "likes": n}


@api.post("/{cid}/signaler")
def signaler(cid: int, donnees: Signalement, request: Request, visiteur: str = Depends(visiteur_requis)):
    if donnees.motif not in MOTIFS:
        raise HTTPException(400, "Motif inconnu.")
    ip = ip_client(request)
    limiter(f"action:{ip}", MAX_ACTIONS_PAR_IP, 3600)
    verifier_altcha(donnees.altcha)
    with transaction() as db:
        if not db.execute("SELECT 1 FROM commentaires WHERE id = ? AND statut = 'publie'", (cid,)).fetchone():
            raise HTTPException(404, "Commentaire introuvable.")
        try:
            db.execute(
                "INSERT INTO signalements (commentaire_id, visiteur, ip, motif, precision, cree_le) VALUES (?, ?, ?, ?, ?, ?)",
                (cid, visiteur, ip, donnees.motif, nettoyer(donnees.precision, 300), maintenant()))
        except sqlite3.IntegrityError:
            return {"deja_signale": True}
        # Masquage automatique : plusieurs personnes différentes (visiteurs ET adresses IP)
        n = db.execute(
            "SELECT COUNT(DISTINCT ip) FROM signalements WHERE commentaire_id = ? AND traite = 0", (cid,)).fetchone()[0]
        if n >= SEUIL_SIGNALEMENTS:
            db.execute("UPDATE commentaires SET statut = 'masque' WHERE id = ? AND statut = 'publie'", (cid,))
    return {"deja_signale": False}


# --- Administration ------------------------------------------------------------------------

def admin_requis(request: Request) -> None:
    jeton = request.cookies.get("admin_commentaires", "")
    try:
        signeur.unsign(jeton, max_age=DUREE_SESSION_ADMIN)
    except (BadSignature, SignatureExpired):
        raise HTTPException(401, "Connexion requise.")


@api.get("/admin", response_class=HTMLResponse)
def page_admin():
    return HTMLResponse((Path(__file__).parent / "admin.html").read_text(),
                        headers={"Cache-Control": "no-store", "X-Robots-Tag": "noindex"})


@api.post("/admin/connexion")
def connexion(donnees: Connexion, request: Request):
    if not ADMIN_MOT_DE_PASSE:
        raise HTTPException(503, "Administration désactivée : ADMIN_MOT_DE_PASSE n'est pas défini.")
    limiter(f"connexion:{ip_client(request)}", MAX_CONNEXIONS_ADMIN, 900)
    if not hmac.compare_digest(donnees.mot_de_passe.encode(), ADMIN_MOT_DE_PASSE.encode()):
        raise HTTPException(401, "Mot de passe incorrect.")
    reponse = JSONResponse({"ok": True})
    reponse.set_cookie("admin_commentaires", signeur.sign(b"admin").decode(), max_age=DUREE_SESSION_ADMIN,
                       httponly=True, samesite="strict", secure=request.url.scheme == "https",
                       path="/api/commentaires")
    return reponse


@api.post("/admin/deconnexion")
def deconnexion():
    reponse = JSONResponse({"ok": True})
    reponse.delete_cookie("admin_commentaires", path="/api/commentaires")
    return reponse


@api.get("/admin/liste", dependencies=[Depends(admin_requis)])
def liste_admin(filtre: str = "attente"):
    conditions = {
        "attente": "c.statut = 'attente'",
        "signales": "(c.statut = 'masque' OR EXISTS (SELECT 1 FROM signalements s WHERE s.commentaire_id = c.id AND s.traite = 0))",
        "publies": "c.statut = 'publie'",
        "refuses": "c.statut = 'refuse'",
    }
    if filtre not in conditions:
        raise HTTPException(400, "Filtre inconnu.")
    with transaction() as db:
        lignes = db.execute(f"""
            SELECT c.*, p.pseudo AS parent_pseudo, p.texte AS parent_texte,
                   (SELECT COUNT(*) FROM likes l WHERE l.commentaire_id = c.id) AS likes
            FROM commentaires c LEFT JOIN commentaires p ON p.id = c.parent_id
            WHERE {conditions[filtre]} ORDER BY c.cree_le DESC LIMIT 200""").fetchall()
        signalements = {}
        for s in db.execute("SELECT commentaire_id, motif, precision, cree_le FROM signalements WHERE traite = 0"):
            signalements.setdefault(s["commentaire_id"], []).append(
                {"motif": MOTIFS.get(s["motif"], s["motif"]), "precision": s["precision"], "cree_le": s["cree_le"]})
        compteurs = {f: db.execute(f"SELECT COUNT(*) FROM commentaires c WHERE {c}").fetchone()[0]
                     for f, c in conditions.items()}
    return {
        "compteurs": compteurs,
        "commentaires": [{
            "id": l["id"], "page": l["page"], "pseudo": l["pseudo"], "texte": l["texte"],
            "statut": l["statut"], "equipe": bool(l["equipe"]), "cree_le": l["cree_le"], "likes": l["likes"],
            "parent": {"pseudo": l["parent_pseudo"], "texte": l["parent_texte"]} if l["parent_id"] else None,
            "signalements": signalements.get(l["id"], []),
        } for l in lignes],
    }


# Déclarée avant /admin/{cid}/{action}, qui l'intercepterait sinon
@api.post("/admin/{cid}/repondre", dependencies=[Depends(admin_requis)])
def repondre_equipe(cid: int, donnees: Reponse):
    texte = nettoyer(donnees.texte, 2000)
    with transaction() as db:
        parent = db.execute("SELECT id, parent_id, page FROM commentaires WHERE id = ?", (cid,)).fetchone()
        if not parent:
            raise HTTPException(404, "Commentaire introuvable.")
        # Répondre valide aussi le commentaire d'origine
        db.execute("UPDATE commentaires SET statut = 'publie', modere_le = ? WHERE id = ? AND statut = 'attente'",
                   (maintenant(), cid))
        db.execute(
            """INSERT INTO commentaires (page, parent_id, pseudo, texte, statut, equipe, cree_le, modere_le)
               VALUES (?, ?, ?, ?, 'publie', 1, ?, ?)""",
            (parent["page"], parent["parent_id"] or parent["id"], NOM_EQUIPE, texte, maintenant(), maintenant()))
    return {"ok": True}


@api.post("/admin/{cid}/{action}", dependencies=[Depends(admin_requis)])
def moderer(cid: int, action: str):
    with transaction() as db:
        if not db.execute("SELECT 1 FROM commentaires WHERE id = ?", (cid,)).fetchone():
            raise HTTPException(404, "Commentaire introuvable.")
        if action == "publier":      # valide, ou rétablit un commentaire signalé
            db.execute("UPDATE commentaires SET statut = 'publie', modere_le = ? WHERE id = ?", (maintenant(), cid))
            db.execute("UPDATE signalements SET traite = 1 WHERE commentaire_id = ?", (cid,))
        elif action == "refuser":
            db.execute("UPDATE commentaires SET statut = 'refuse', modere_le = ? WHERE id = ?", (maintenant(), cid))
            db.execute("UPDATE signalements SET traite = 1 WHERE commentaire_id = ?", (cid,))
        elif action == "supprimer":  # définitif, réponses comprises
            db.execute("DELETE FROM commentaires WHERE id = ?", (cid,))
        else:
            raise HTTPException(400, "Action inconnue.")
    return {"ok": True}


# --- Application ---------------------------------------------------------------------------

app = FastAPI(title="Commentaires du guide Ligu'asso", docs_url=None, redoc_url=None, openapi_url=None)
if CORS_ORIGINES:  # rédaction locale uniquement (guides servis sur un autre port)
    app.add_middleware(CORSMiddleware, allow_origins=CORS_ORIGINES, allow_methods=["GET", "POST"],
                       allow_headers=["Content-Type", "X-Visiteur"])
app.include_router(api)


@app.get("/sante")
def sante():
    return {"ok": True}
