"""Hook des tutos vidéo : syntaxe « !!! video », cartes, vignettes, vidéothèque, videos.json."""
import json
from types import SimpleNamespace as Objet

import pytest

BLOC = '''!!! video "Importer un fichier"
    https://www.youtube-nocookie.com/embed/lMVnP_gSw5U · 7 min
    Choisir la saison, déposer le fichier,
    puis valider.
'''


def page(url):
    return Objet(url=url)


@pytest.mark.parametrize("adresse", [
    "https://www.youtube-nocookie.com/embed/lMVnP_gSw5U", "https://youtu.be/lMVnP_gSw5U",
    "https://www.youtube.com/watch?v=lMVnP_gSw5U&t=3", "https://www.youtube.com/embed/lMVnP_gSw5U?rel=0"])
def test_identifiant_reconnu_dans_tous_les_formats(videos, adresse):
    assert videos._lire("T", f"    {adresse}\n")["id"] == "lMVnP_gSw5U"


def test_lire_un_bloc(videos):
    corps = videos.BLOC.search(BLOC)
    v = videos._lire(corps["titre"], corps["corps"])
    assert v == {"id": "lMVnP_gSw5U", "titre": "Importer un fichier", "duree": "7 min",
                 "resume": "Choisir la saison, déposer le fichier, puis valider."}


@pytest.mark.parametrize("corps, message", [("\n", "manquante"), ("    https://exemple.org/video\n", "non reconnue")])
def test_erreurs_de_saisie(videos, corps, message):
    with pytest.raises(ValueError, match=message):
        videos._lire("T", corps)


def test_carte_lecture_au_clic_et_lien_sans_cookie(videos, tmp_path):
    config = {"docs_dir": str(tmp_path)}
    html = videos._carte({"id": "lMVnP_gSw5U", "titre": "<Import>", "duree": "7 min", "resume": "R & D"},
                         page("departemental/adhesions-import/"), config)
    assert 'data-youtube="lMVnP_gSw5U"' in html and "<iframe" not in html                # rien de chargé avant le clic
    assert "&lt;Import&gt;" in html and "R &amp; D" in html                               # texte échappé
    assert 'href="https://www.youtube-nocookie.com/embed/lMVnP_gSw5U"' in html
    assert 'src="https://i.ytimg.com/vi/lMVnP_gSw5U/hqdefault.jpg"' in html             # pas d'aperçu local


def test_apercu_local_prefere(videos, tmp_path):
    (tmp_path / "img" / "videos").mkdir(parents=True)
    (tmp_path / "img" / "videos" / "lMVnP_gSw5U.jpg").write_bytes(b"jpg")
    html = videos._carte({"id": "lMVnP_gSw5U", "titre": "T", "duree": "", "resume": ""}, page("a/b/"), {"docs_dir": str(tmp_path)})
    assert 'src="../../img/videos/lMVnP_gSw5U.jpg"' in html                                # chemin relatif à la page
    assert "tuto-video__duree" not in html and "tuto-video__resume" not in html


def test_vignettes(videos, tmp_path):
    config = {"docs_dir": str(tmp_path)}
    assert "Aucune vidéo" in videos._vignettes([], page(""), config, "grille")
    html = videos._vignettes([{"id": "abcdefghijk", "titre": "T", "duree": "4 min", "fiche": "connexion/", "titre_fiche": "Se connecter"}],
                             page("videos/"), config, "grille")
    assert 'href="../connexion/#video-abcdefghijk"' in html and "Fiche : Se connecter" in html


def test_construction_complete(videos, tmp_path):
    """on_files recense, on_page_markdown remplace blocs et marqueurs, on_post_build écrit videos.json."""
    docs, site = tmp_path / "docs", tmp_path / "site"
    docs.mkdir(); site.mkdir()
    (docs / "import.md").write_text("# Importer un fichier\n\n" + BLOC)
    (docs / "index.md").write_text("# Accueil\n\n<!-- videos:accueil -->\n")
    fichiers = [Objet(abs_src_path=str(docs / n), url=u, name=n[:-3]) for n, u in (("import.md", "import/"), ("index.md", ""))]
    config = {"docs_dir": str(docs), "site_dir": str(site)}

    videos.on_files(Objet(documentation_pages=lambda: fichiers), config)
    fiche = videos.on_page_markdown((docs / "import.md").read_text(), page("import/"), config, None)
    accueil = videos.on_page_markdown("<!-- videos:accueil -->\n<!-- videos:toutes -->", page(""), config, None)
    videos.on_post_build(config)

    assert '<div class="tuto-video" id="video-lMVnP_gSw5U">' in fiche and "!!! video" not in fiche
    assert accueil.count('class="vignette-video"') == 2 and "Fiche : Importer un fichier" in accueil
    assert json.loads((site / "videos.json").read_text()) == [{"fiche": "import/", "titre": "Importer un fichier", "id": "lMVnP_gSw5U"}]


def test_nouvelle_construction_repart_de_zero(videos, tmp_path):
    docs = tmp_path / "docs"; docs.mkdir()
    (docs / "a.md").write_text(BLOC)
    f = [Objet(abs_src_path=str(docs / "a.md"), url="a/", name="a")]
    for _ in range(2):
        videos.on_files(Objet(documentation_pages=lambda: f), {"docs_dir": str(docs)})
    assert len(videos._videos) == 1
