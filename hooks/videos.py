"""Tutos vidéo du guide (hook MkDocs).

Dans une fiche, une vidéo s'écrit ainsi :

    !!! video "Importer un fichier de licences"
        https://youtu.be/lMVnP_gSw5U · 7 min
        Préparer le fichier, l'importer, puis vérifier le lot créé.

- 1re ligne : l'adresse YouTube (watch, youtu.be ou embed), puis la durée après « · » (facultatif) ;
- lignes suivantes (facultatif) : ce qu'on apprend dans la vidéo.

Le hook remplace le bloc par une carte vidéo (YouTube ne se charge qu'au clic) et recense
toutes les vidéos du guide pour :
- `<!-- videos:accueil -->` : les vidéos à mettre en avant (page d'accueil) ;
- `<!-- videos:toutes -->`  : la vidéothèque complète ;
- `videos.json` à la racine du site : le repère ▶ dans le menu (javascripts/videos.js).

Image d'aperçu : img/videos/<identifiant>.jpg si elle existe (aucune requête vers Google
avant le clic), sinon celle de YouTube.
"""
from __future__ import annotations

import html
import json
import re
from pathlib import Path

BLOC = re.compile(r'^!!! video "(?P<titre>[^"]+)"\n(?P<corps>(?:(?: {4}.*)?\n)+)', re.M)
IDENTIFIANT = re.compile(r"(?:youtu\.be/|[?&]v=|/embed/)([A-Za-z0-9_-]{11})")
MAX_ACCUEIL = 3

_videos: list[dict] = []          # recensement de la construction en cours


def _lire(titre: str, corps: str) -> dict:
    lignes = [l[4:] if l.startswith("    ") else l.strip() for l in corps.splitlines()]
    lignes = [l for l in lignes if l.strip()]
    if not lignes:
        raise ValueError(f"Vidéo « {titre} » : adresse YouTube manquante")
    adresse, _, duree = lignes[0].partition("·")
    trouve = IDENTIFIANT.search(adresse)
    if not trouve:
        raise ValueError(f"Vidéo « {titre} » : adresse YouTube non reconnue ({adresse.strip()})")
    return {"id": trouve.group(1), "titre": titre.strip(), "duree": duree.strip(),
            "resume": " ".join(l.strip() for l in lignes[1:])}


def _titre_de_fiche(texte: str, defaut: str) -> str:
    h1 = re.search(r"^# (.+)$", texte, re.M)
    return h1.group(1).strip() if h1 else defaut


def on_files(files, config, **kwargs):
    """Recense les vidéos de toutes les fiches avant de construire les pages."""
    _videos.clear()
    for f in files.documentation_pages():
        texte = Path(f.abs_src_path).read_text(encoding="utf-8")
        for bloc in BLOC.finditer(texte):
            video = _lire(bloc["titre"], bloc["corps"])
            video.update(fiche=f.url, titre_fiche=_titre_de_fiche(texte, f.name))
            _videos.append(video)
    return files


def _racine(page) -> str:
    """Chemin relatif de la page vers la racine du site."""
    return "../" * page.url.count("/")


def _apercu(video: dict, racine: str, config) -> str:
    local = Path(config["docs_dir"]) / "img" / "videos" / f"{video['id']}.jpg"
    if local.exists():
        return f"{racine}img/videos/{video['id']}.jpg"
    return f"https://i.ytimg.com/vi/{video['id']}/hqdefault.jpg"


def _carte(video: dict, page, config) -> str:
    e = html.escape
    duree = f'<span class="tuto-video__duree">{e(video["duree"])}</span>' if video["duree"] else ""
    resume = f'<p class="tuto-video__resume">{e(video["resume"])}</p>' if video["resume"] else ""
    lien = f"https://youtu.be/{video['id']}"
    return (
        f'<div class="tuto-video" id="video-{video["id"]}">\n'
        f'<div class="tuto-video__entete"><span class="tuto-video__badge">Tuto vidéo</span>{duree}</div>\n'
        f'<p class="tuto-video__titre">{e(video["titre"])}</p>\n'
        f'<button type="button" class="tuto-video__lecteur" data-youtube="{video["id"]}" '
        f'aria-label="Lire la vidéo : {e(video["titre"])}">'
        f'<img src="{_apercu(video, _racine(page), config)}" alt="" loading="lazy">'
        f'<span class="tuto-video__play" aria-hidden="true"></span></button>\n'
        f'{resume}\n'
        f'<p class="tuto-video__lien">Regarder sur YouTube : <a href="{lien}">{lien}</a></p>\n'
        f'</div>\n'
    )


def _vignettes(videos: list[dict], page, config, classe: str) -> str:
    if not videos:
        return '<p class="videos-vide">Aucune vidéo pour le moment.</p>'
    e, racine = html.escape, _racine(page)
    cartes = []
    for v in videos:
        duree = f'<span class="vignette-video__duree">{e(v["duree"])}</span>' if v["duree"] else ""
        cartes.append(
            f'<a class="vignette-video" href="{racine}{v["fiche"]}#video-{v["id"]}">'
            f'<span class="vignette-video__image"><img src="{_apercu(v, racine, config)}" alt="" loading="lazy">'
            f'<span class="tuto-video__play" aria-hidden="true"></span>{duree}</span>'
            f'<span class="vignette-video__titre">{e(v["titre"])}</span>'
            f'<span class="vignette-video__fiche">Fiche : {e(v["titre_fiche"])}</span></a>')
    return f'<div class="{classe}">\n' + "\n".join(cartes) + "\n</div>\n"


def on_page_markdown(markdown, page, config, files, **kwargs):
    markdown = BLOC.sub(lambda b: _carte(_lire(b["titre"], b["corps"]), page, config) + "\n", markdown)
    markdown = markdown.replace("<!-- videos:accueil -->",
                                _vignettes(_videos[:MAX_ACCUEIL], page, config, "videos-grille videos-grille--accueil"))
    markdown = markdown.replace("<!-- videos:toutes -->",
                                _vignettes(_videos, page, config, "videos-grille"))
    return markdown


def on_post_build(config, **kwargs):
    index = [{"fiche": v["fiche"], "titre": v["titre"], "id": v["id"]} for v in _videos]
    (Path(config["site_dir"]) / "videos.json").write_text(json.dumps(index, ensure_ascii=False), encoding="utf-8")
