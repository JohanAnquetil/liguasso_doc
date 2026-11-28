"""API HTTP (FastAPI) : traduit les requêtes en cas d'usage et les erreurs métier en réponses."""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, FastAPI, Header, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field

from ..application.commentaires import NouveauCommentaire
from ..application.propositions import NouvelleProposition
from ..domaine.erreurs import ErreurMetier, Invalide
from ..domaine.textes import VISITEUR_VALIDE

COOKIE = "admin_commentaires"
PREFIXE = "/api/commentaires"


# --- Corps des requêtes ---

class CorpsCommentaire(BaseModel):
    page: str
    pseudo: str = Field(min_length=1, max_length=40)
    texte: str = Field(min_length=1, max_length=2000)
    parent_id: Optional[int] = None
    altcha: str = ""
    site_web: str = ""          # champ piège


class CorpsSignalement(BaseModel):
    motif: str
    precision: str = Field("", max_length=300)
    altcha: str = ""


class CorpsReponse(BaseModel):
    texte: str = Field(min_length=1, max_length=2000)


class CorpsConnexion(BaseModel):
    mot_de_passe: str


class CorpsProposition(BaseModel):
    type: str
    page: str
    titre: str = Field("", max_length=120)
    pseudo: str = Field(min_length=1, max_length=40)
    resume: str = Field(min_length=1, max_length=300)
    texte: str = Field(min_length=1, max_length=100_000)
    blob_sha: str = ""
    commit_sha: str = ""
    altcha: str = ""
    site_web: str = ""


def creer_api(s) -> FastAPI:
    api = APIRouter(prefix=PREFIXE)

    # --- Identité anonyme : empreintes du visiteur et de l'adresse IP ---

    def ip(request: Request) -> str:
        return s.empreintes.de(request.client.host if request.client else "inconnue", "ip")

    def visiteur_facultatif(x_visiteur: str = Header("")) -> Optional[str]:
        return s.empreintes.de(x_visiteur, "visiteur") if VISITEUR_VALIDE.match(x_visiteur or "") else None

    def visiteur(v: Optional[str] = Depends(visiteur_facultatif)) -> str:
        if not v:
            raise Invalide("Identifiant de visiteur manquant.")
        return v

    def admin(request: Request) -> None:
        s.administration.verifier(request.cookies.get(COOKIE, ""))

    # --- Visiteurs ---

    @api.get("/defi")
    def defi(response: Response):
        response.headers["Cache-Control"] = "no-store"
        return s.anti_robot.creer_defi()

    @api.get("")
    def lister(page: str, v: Optional[str] = Depends(visiteur_facultatif)):
        return s.commentaires.lister(page, v)

    @api.post("", status_code=201)
    def commenter(c: CorpsCommentaire, request: Request, v: str = Depends(visiteur)):
        cid = s.commentaires.commenter(NouveauCommentaire(
            page=c.page, pseudo=c.pseudo, texte=c.texte, parent_id=c.parent_id,
            preuve=c.altcha, piege=c.site_web), v, ip(request))
        return {"id": cid, "en_attente": True}

    @api.post("/{cid}/like")
    def liker(cid: int, request: Request, v: str = Depends(visiteur)):
        return s.commentaires.liker(cid, v, ip(request))

    @api.post("/{cid}/signaler")
    def signaler(cid: int, c: CorpsSignalement, request: Request, v: str = Depends(visiteur)):
        return s.commentaires.signaler(cid, c.motif, c.precision, c.altcha, v, ip(request))

    @api.get("/propositions/source")
    def source(page: str, response: Response):
        response.headers["Cache-Control"] = "no-store"
        return s.propositions.source(page)

    @api.post("/propositions", status_code=201)
    def proposer(c: CorpsProposition, request: Request, v: str = Depends(visiteur)):
        pid = s.propositions.proposer(NouvelleProposition(
            type=c.type, page=c.page, pseudo=c.pseudo, resume=c.resume, texte=c.texte, titre=c.titre,
            blob_sha=c.blob_sha, commit_sha=c.commit_sha, preuve=c.altcha, piege=c.site_web), v, ip(request))
        return {"id": pid}

    # --- Modération ---

    @api.get("/admin", response_class=HTMLResponse)
    def page_admin():
        return HTMLResponse((Path(__file__).parent / "admin.html").read_text(),
                            headers={"Cache-Control": "no-store", "X-Robots-Tag": "noindex"})

    @api.post("/admin/connexion")
    def connexion(c: CorpsConnexion, request: Request):
        jeton = s.administration.connecter(c.mot_de_passe, ip(request))
        reponse = JSONResponse({"ok": True})
        reponse.set_cookie(COOKIE, jeton, max_age=8 * 3600, httponly=True, samesite="strict",
                           secure=request.url.scheme == "https", path=PREFIXE)
        return reponse

    @api.post("/admin/deconnexion")
    def deconnexion():
        reponse = JSONResponse({"ok": True})
        reponse.delete_cookie(COOKIE, path=PREFIXE)
        return reponse

    @api.get("/admin/liste", dependencies=[Depends(admin)])
    def liste_admin(filtre: str = "attente"):
        return s.commentaires.pour_admin(filtre)

    @api.get("/admin/propositions", dependencies=[Depends(admin)])
    def liste_propositions(filtre: str = "attente"):
        return s.propositions.pour_admin(filtre)

    @api.post("/admin/propositions/{pid}/accepter", dependencies=[Depends(admin)])
    def accepter(pid: int):
        return {"pr_url": s.propositions.accepter(pid)}

    @api.post("/admin/propositions/{pid}/refuser", dependencies=[Depends(admin)])
    def refuser(pid: int):
        s.propositions.refuser(pid)
        return {"ok": True}

    # Déclarée avant /admin/{cid}/{action}, qui l'intercepterait sinon
    @api.post("/admin/{cid}/repondre", dependencies=[Depends(admin)])
    def repondre(cid: int, c: CorpsReponse):
        s.commentaires.repondre_au_nom_de_l_equipe(cid, c.texte)
        return {"ok": True}

    @api.post("/admin/{cid}/{action}", dependencies=[Depends(admin)])
    def moderer(cid: int, action: str):
        s.commentaires.moderer(cid, action)
        return {"ok": True}

    # --- Application ---

    app = FastAPI(title="Contributions au guide Ligu'asso", docs_url=None, redoc_url=None, openapi_url=None)

    @app.exception_handler(ErreurMetier)
    def erreur_metier(_request: Request, e: ErreurMetier):
        return JSONResponse({"detail": e.message}, status_code=e.code)

    if s.cors_origines:   # rédaction locale uniquement (guides servis sur d'autres ports)
        app.add_middleware(CORSMiddleware, allow_origins=s.cors_origines, allow_methods=["GET", "POST"],
                           allow_headers=["Content-Type", "X-Visiteur"])
    app.include_router(api)

    @app.get("/sante")
    def sante():
        return {"ok": True}

    return app
