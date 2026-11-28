// Éditeur visuel des fiches, pour les propositions de modification (propositions.js).
//
// La fiche (Markdown MkDocs) est découpée en blocs :
// - modifiables : titres, paragraphes, listes, encadrés (Attention, Astuce…), onglets ;
// - verrouillés : encadré « Accès », vidéos, captures, blocs communs (--8<--), HTML, tableaux…
// Un bloc qui n'a pas été touché est réécrit mot pour mot : la proposition ne contient que
// les vrais changements. Un « mode avancé » donne accès au texte brut.
//
// Le modèle (lire / ecrire) n'utilise pas le DOM : il est testé avec Node
// (verification/editeur/editeur.test.js) sur toutes les fiches du dépôt.
(function (racine) {
  "use strict";

  // ======================================================================================
  // Modèle : Markdown <-> blocs
  // ======================================================================================

  var ENCADRE = /^(!!!|\?\?\?\+?)\s+([\w-]+)(?:\s+"([^"]*)")?\s*$/;
  var ONGLET = /^===(\+?)\s+"([^"]*)"\s*$/;
  var TITRE = /^(#{1,6})\s+(.*)$/;
  var IMAGE = /^!\[([^\]]*)\]\(([^)\s]+)[^)]*\)(\{[^}]*\})?\s*$/;
  var PUCE = /^([-*+]|\d+[.)])\s+(.*)$/;
  var VERROUILLES = { chemin: "Encadré « Accès » (chemin dans le menu)", video: "Tuto vidéo" };
  var TYPES_ENCADRE = { warning: "Attention", tip: "Astuce", note: "Remarque", example: "Exemple",
    info: "Info", danger: "Attention", question: "Question", success: "Réussite" };

  function vide(ligne) { return ligne.trim() === ""; }
  function indentee(ligne) { return /^( {4}|\t)/.test(ligne); }
  function desindenter(lignes) {
    return lignes.map(function (l) { return l.indexOf("    ") === 0 ? l.slice(4) : l.charAt(0) === "\t" ? l.slice(1) : l.replace(/^ {1,3}/, ""); });
  }
  function indenter(texte) {
    return texte.split("\n").map(function (l) { return l === "" ? "" : "    " + l; }).join("\n");
  }

  // Lignes d'un bloc indenté sous une ligne d'en-tête (encadré, onglet, élément de liste) :
  // lignes indentées, et lignes vides suivies d'une ligne indentée.
  function corpsIndente(lignes, i) {
    var fin = i;
    while (fin < lignes.length) {
      if (indentee(lignes[fin])) { fin++; continue; }
      if (vide(lignes[fin])) {
        var j = fin; while (j < lignes.length && vide(lignes[j])) j++;
        if (j < lignes.length && indentee(lignes[j])) { fin = j; continue; }
      }
      break;
    }
    return fin;
  }

  function texteInlineVerrouille(t) {
    return /\{\s*[.#:][^}]*\}/.test(t) || /<\/?[a-z][^>]*>/i.test(t) || /--8<--/.test(t);
  }

  // Lit un texte Markdown (sans indentation commune) et renvoie { blocs, fin }.
  function lire(texte) {
    var lignes = texte.split("\n");
    var blocs = [];
    var i = 0;
    while (true) {
      var debutEcart = i;
      while (i < lignes.length && vide(lignes[i])) i++;
      if (i >= lignes.length) return { blocs: blocs, fin: lignes.slice(debutEcart) };
      var ecart = lignes.slice(debutEcart, i);
      var bloc = lireBloc(lignes, i, blocs.length === 0 && debutEcart === 0);
      bloc.ecart = ecart;
      blocs.push(bloc);
      i = bloc._fin;
      delete bloc._fin;
    }
  }

  function brut(lignes, debut, fin) { return lignes.slice(debut, fin).join("\n"); }

  function lireBloc(lignes, i, toutDebut) {
    var l = lignes[i], m, fin;

    // En-tête YAML de la page
    if (toutDebut && l === "---") {
      fin = i + 1; while (fin < lignes.length && lignes[fin] !== "---") fin++;
      fin = Math.min(fin + 1, lignes.length);
      return { type: "verrou", libelle: "Réglages de la page", cache: true, brut: brut(lignes, i, fin), _fin: fin };
    }
    if ((m = TITRE.exec(l))) {
      return { type: "titre", niveau: m[1].length, texte: m[2], brut: l, _fin: i + 1 };
    }
    if ((m = ENCADRE.exec(l))) {
      fin = corpsIndente(lignes, i + 1);
      var corps = brut(lignes, i + 1, fin);
      if (VERROUILLES[m[2]]) {
        return { type: "verrou", libelle: VERROUILLES[m[2]], apercu: desindenter(lignes.slice(i + 1, fin)).join(" ").replace(/\*\*/g, "").replace(/\s+/g, " ").trim() || m[3],
                 brut: brut(lignes, i, fin), _fin: fin };
      }
      return { type: "encadre", marque: m[1], genre: m[2], titre: m[3] === undefined ? null : m[3],
               enfants: lire(desindenter(corps.split("\n")).join("\n")), brut: brut(lignes, i, fin), _fin: fin };
    }
    if (ONGLET.test(l)) {
      var onglets = []; fin = i;
      while (fin < lignes.length) {
        var j = fin, ecart = [];
        while (j < lignes.length && vide(lignes[j])) { ecart.push(lignes[j]); j++; }
        if (j >= lignes.length || !(m = ONGLET.exec(lignes[j]))) break;
        if (onglets.length === 0 && ecart.length) break;
        var finOnglet = corpsIndente(lignes, j + 1);
        onglets.push({ ecart: onglets.length ? ecart : [], entete: lignes[j], nom: m[2],
                       enfants: lire(desindenter(lignes.slice(j + 1, finOnglet)).join("\n")) });
        fin = finOnglet;
      }
      return { type: "onglets", onglets: onglets, brut: brut(lignes, i, fin), _fin: fin };
    }
    if ((m = IMAGE.exec(l))) {
      return { type: "image", alt: m[1], src: m[2], brut: l, _fin: i + 1 };
    }
    if (/^--8<--/.test(l)) {
      var nom = (/"([^"]+)"/.exec(l) || [])[1] || "";
      return { type: "verrou", libelle: "Bloc commun aux deux guides", apercu: nom, brut: l, _fin: i + 1 };
    }
    if (/^<!--/.test(l)) {
      fin = i; while (fin < lignes.length && lignes[fin].indexOf("-->") === -1) fin++;
      fin = Math.min(fin + 1, lignes.length);
      var contenu = brut(lignes, i, fin);
      var liste = /videos:(accueil|toutes)/.exec(contenu);
      return { type: "verrou", libelle: liste ? "Liste automatique des tutos vidéo" : "Note technique", cache: !liste,
               brut: contenu, _fin: fin };
    }
    if (/^<div\b/i.test(l)) {
      var profondeur = 0; fin = i;
      do {
        profondeur += (lignes[fin].match(/<div\b/gi) || []).length - (lignes[fin].match(/<\/div>/gi) || []).length;
        fin++;
      } while (fin < lignes.length && profondeur > 0);
      return { type: "verrou", libelle: "Mise en page spéciale", brut: brut(lignes, i, fin), _fin: fin };
    }
    if (/^</.test(l) || /^\|/.test(l)) {
      fin = i; while (fin < lignes.length && !vide(lignes[fin])) fin++;
      return { type: "verrou", libelle: /^\|/.test(l) ? "Tableau" : "Mise en page spéciale", brut: brut(lignes, i, fin), _fin: fin };
    }
    if (/^(```|~~~)/.test(l)) {
      var cloture = l.slice(0, 3); fin = i + 1;
      while (fin < lignes.length && lignes[fin].indexOf(cloture) !== 0) fin++;
      fin = Math.min(fin + 1, lignes.length);
      return { type: "verrou", libelle: "Bloc de code", brut: brut(lignes, i, fin), _fin: fin };
    }
    if (/^(-{3,}|\*{3,}|_{3,})\s*$/.test(l)) {
      return { type: "verrou", libelle: "Séparateur", brut: l, _fin: i + 1 };
    }
    if (PUCE.test(l)) {
      return lireListe(lignes, i);
    }
    // Paragraphe : jusqu'à la prochaine ligne vide
    fin = i; while (fin < lignes.length && !vide(lignes[fin])) fin++;
    var texte = brut(lignes, i, fin);
    if (texteInlineVerrouille(texte)) {
      return { type: "verrou", libelle: "Bouton ou mise en forme spéciale", apercu: texte, brut: texte, _fin: fin };
    }
    return { type: "paragraphe", texte: texte, brut: texte, _fin: fin };
  }

  function lireListe(lignes, i) {
    var elements = [], fin = i, numerotee = /^\d/.test(lignes[i]);
    while (fin < lignes.length) {
      var j = fin, ecart = [];
      while (j < lignes.length && vide(lignes[j])) { ecart.push(lignes[j]); j++; }
      if (j >= lignes.length) break;
      var m = PUCE.exec(lignes[j]);
      if (!m || /^\d/.test(m[1]) !== numerotee) break;
      if (elements.length && ecart.length > 1) break;
      var finElement = corpsIndente(lignes, j + 1);
      var sousLignes = lignes.slice(j + 1, finElement);
      elements.push({ ecart: elements.length ? ecart : [], marque: m[1], texte: m[2],
                      enfants: sousLignes.length ? lire(desindenter(sousLignes).join("\n")) : null });
      fin = finElement;
    }
    var liste = { type: "liste", numerotee: numerotee, elements: elements, brut: brut(lignes, i, fin), _fin: fin };
    return liste;
  }

  // ---------- Écriture ----------

  function ecrire(conteneur) {
    if (!conteneur.blocs.length) return conteneur.fin.join("\n");
    var morceaux = conteneur.blocs.map(function (b, k) {
      return (k ? "\n" : "") + b.ecart.map(function (e) { return e + "\n"; }).join("") + ecrireBloc(b);
    });
    return morceaux.join("") + (conteneur.fin.length ? "\n" + conteneur.fin.join("\n") : "");
  }

  function ecrireEnfants(enfants) {
    if (!enfants) return "";
    var t = ecrire({ blocs: enfants.blocs, fin: [] });
    return t;
  }

  function ecrireBloc(b) {
    if (!b.modifie) return b.brut;
    switch (b.type) {
      case "titre": return new Array(b.niveau + 1).join("#") + " " + b.texte.trim();
      case "paragraphe": return b.texte.trim();
      case "encadre":
        return b.marque + " " + b.genre + (b.titre !== null && b.titre !== undefined ? ' "' + b.titre.replace(/"/g, "'") + '"' : "") +
          "\n" + indenter(ecrireEnfants(b.enfants));
      case "onglets":
        return b.onglets.map(function (o, k) {
          return (k ? "\n" : "") + o.ecart.map(function (e) { return e + "\n"; }).join("") + o.entete + "\n" +
            indenter(ecrireEnfants(o.enfants));
        }).join("");
      case "liste":
        return b.elements.map(function (e, k) {
          var marque = b.numerotee ? (k + 1) + "." : e.marque;
          var sous = e.enfants && e.enfants.blocs.length ? "\n" + indenter(ecrireEnfants(e.enfants)) : "";
          return (k ? "\n" : "") + e.ecart.map(function (x) { return x + "\n"; }).join("") + marque + " " + e.texte.trim() + sous;
        }).join("");
      default: return b.brut;
    }
  }

  // ---------- Construction de nouveaux blocs ----------

  function nouveauBloc(genre) {
    var b;
    if (genre === "paragraphe") b = { type: "paragraphe", texte: "" };
    else if (genre === "titre") b = { type: "titre", niveau: 2, texte: "" };
    else if (genre === "puces" || genre === "numeros") {
      b = { type: "liste", numerotee: genre === "numeros", elements: [{ ecart: [], marque: genre === "numeros" ? "1." : "-", texte: "", enfants: null }] };
    } else {   // encadré : warning, tip, note
      b = { type: "encadre", marque: "!!!", genre: genre, titre: null,
            enfants: { blocs: [{ type: "paragraphe", texte: "", ecart: [], modifie: true }], fin: [] } };
    }
    b.ecart = [""];
    b.modifie = true;
    return b;
  }

  // ======================================================================================
  // Texte enrichi : Markdown en ligne <-> HTML
  // ======================================================================================

  function echapper(t) {
    return t.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
  }

  function versHtml(md) {
    var codes = [];
    var t = echapper(md).replace(/`([^`]+)`/g, function (_, c) { codes.push(c); return "\u0000" + (codes.length - 1) + "\u0000"; });
    t = t.replace(/\\([*_\[\]#])/g, function (_, c) { return "&#" + c.charCodeAt(0) + ";"; })
      .replace(/!\[([^\]]*)\]\(([^)\s]+)\)/g, "$1")
      .replace(/\[([^\]]+)\]\(([^)\s]+)\)/g, '<a href="$2">$1</a>')
      .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
      .replace(/(^|[^*\w])\*([^*\s][^*]*)\*(?!\*)/g, "$1<em>$2</em>")
      .replace(/(^|\W)_([^_\s][^_]*)_(?!\w)/g, "$1<em>$2</em>")
      .replace(/\n/g, "<br>");
    return t.replace(/\u0000(\d+)\u0000/g, function (_, n) { return "<code>" + codes[+n] + "</code>"; });
  }

  function versMarkdown(noeud) {
    var md = "";
    noeud.childNodes.forEach(function (n) {
      if (n.nodeType === 3) { md += n.nodeValue.replace(/ /g, " ").replace(/\*/g, "\\*"); return; }   // un astérisque tapé reste un astérisque
      if (n.nodeType !== 1) return;
      var tag = n.tagName.toLowerCase(), dedans = versMarkdown(n);
      // Certains navigateurs mettent en forme avec des <span style="…"> plutôt qu'avec <b> / <i>
      if (tag === "span" && n.style) {
        var poids = n.style.fontWeight, gras = poids === "bold" || parseInt(poids, 10) >= 600;
        if (gras) tag = "strong"; else if (n.style.fontStyle === "italic") tag = "em";
      }
      if (tag === "strong" || tag === "b") md += dedans.trim() ? "**" + dedans.trim() + "**" + (/\s$/.test(dedans) ? " " : "") : dedans;
      else if (tag === "em" || tag === "i") md += dedans.trim() ? "*" + dedans.trim() + "*" + (/\s$/.test(dedans) ? " " : "") : dedans;
      else if (tag === "code") md += "`" + n.textContent + "`";
      else if (tag === "a") md += "[" + dedans + "](" + (n.getAttribute("href") || "") + ")";
      else if (tag === "br") md += " ";
      else if (tag === "div" || tag === "p") md += (md ? " " : "") + dedans;
      else md += dedans;
    });
    return md;
  }

  // ======================================================================================
  // Vue : l'éditeur dans la page
  // ======================================================================================

  function creer(conteneur, markdown, options) {
    options = options || {};
    var doc = conteneur.ownerDocument;
    var modele = lire(markdown || "");
    if (!modele.blocs.length) {
      var depart = nouveauBloc("paragraphe"); depart.ecart = [];
      modele.blocs.push(depart);
    }
    var avance = false, zoneAvancee = null;

    function el(tag, classe, texte) {
      var n = doc.createElement(tag);
      if (classe) n.className = classe;
      if (texte !== undefined) n.textContent = texte;
      return n;
    }

    // Marque un bloc et tous ses conteneurs comme modifiés
    function toucher(chemin) { chemin.forEach(function (b) { b.modifie = true; }); }

    // ----- Barre d'outils -----
    var barre = el("div", "editeur-barre");
    barre.setAttribute("role", "toolbar");
    barre.setAttribute("aria-label", "Mise en forme");
    function bouton(libelle, titre, action) {
      var b = el("button", "editeur-outil", libelle);
      b.type = "button"; b.title = titre;
      b.addEventListener("mousedown", function (e) { e.preventDefault(); });   // garder la sélection
      b.addEventListener("click", action);
      barre.append(b);
      return b;
    }
    bouton("G", "Gras", function () { doc.execCommand("bold"); });
    bouton("I", "Italique", function () { doc.execCommand("italic"); });
    bouton("🔗", "Lien", function () {
      var url = racine.prompt("Adresse du lien (ou nom de fiche, par exemple adhesions-lots.md) :");
      if (url) doc.execCommand("createLink", false, url.trim());
    });
    bouton("Retirer le lien", "Retirer le lien", function () { doc.execCommand("unlink"); });
    var basculer = el("button", "editeur-outil editeur-avance", "Mode avancé (Markdown)");
    basculer.type = "button";
    basculer.addEventListener("click", function () {
      if (!avance) {
        zoneAvancee = el("textarea", "editeur-texte-brut");
        zoneAvancee.value = markdownActuel();
        zoneAvancee.rows = 18;
        zone.replaceWith(zoneAvancee);
        avance = true; basculer.textContent = "Revenir à l'éditeur visuel";
        barre.classList.add("editeur-barre--avance");
      } else {
        modele = lire(zoneAvancee.value);
        if (!modele.blocs.length) { var p = nouveauBloc("paragraphe"); p.ecart = []; modele.blocs.push(p); }
        zone = el("div", "editeur-blocs");
        rendreListe(zone, modele, []);
        zoneAvancee.replaceWith(zone);
        avance = false; basculer.textContent = "Mode avancé (Markdown)";
        barre.classList.remove("editeur-barre--avance");
      }
    });
    barre.append(basculer);

    // ----- Champs modifiables -----
    function editable(classe, md, enLigne, surChange, surEntree) {
      var n = el("div", "editeur-editable " + classe);
      n.contentEditable = "true";
      n.spellcheck = true;
      if (enLigne) n.innerHTML = versHtml(md); else n.textContent = md;
      n.addEventListener("input", function () { surChange(enLigne ? versMarkdown(n).replace(/\s+$/, "") : n.textContent); });
      n.addEventListener("click", function (e) { if (e.target.closest("a")) e.preventDefault(); });
      n.addEventListener("paste", function (e) {   // coller du texte simple, pas la mise en forme d'origine
        e.preventDefault();
        doc.execCommand("insertText", false, (e.clipboardData || racine.clipboardData).getData("text/plain").replace(/\s*\n\s*/g, " "));
      });
      n.addEventListener("keydown", function (e) {
        if (e.key === "Enter") { e.preventDefault(); if (surEntree) surEntree(n); }
      });
      return n;
    }

    // Texte après le curseur, retiré du champ (pour couper un paragraphe ou un élément de liste)
    function couperApresCurseur(n) {
      var sel = doc.getSelection();
      if (!sel.rangeCount) return "";
      var r = sel.getRangeAt(0).cloneRange();
      r.setEndAfter(n.lastChild || n);
      var morceau = r.extractContents();
      var tmp = el("div"); tmp.append(morceau);
      return versMarkdown(tmp).trim();
    }

    // ----- Rendu d'une liste de blocs (récursif) -----
    function rendreListe(cible, conteneurModele, chemin) {
      cible.textContent = "";
      conteneurModele.blocs.forEach(function (b, k) {
        cible.append(rendreBloc(b, conteneurModele, k, chemin));
        cible.append(ajouteur(conteneurModele, k + 1, chemin, cible));   // « + Ajouter » après chaque bloc
      });
      if (!conteneurModele.blocs.length) cible.append(ajouteur(conteneurModele, 0, chemin, cible));
    }

    function rerendre(cible, conteneurModele, chemin) { rendreListe(cible, conteneurModele, chemin); }

    function ajouteur(conteneurModele, position, chemin, cible) {
      var boite = el("div", "editeur-ajouter");
      var b = el("button", "editeur-plus", "+ Ajouter");
      b.type = "button";
      var menu = el("div", "editeur-menu");
      menu.hidden = true;
      [["paragraphe", "Paragraphe"], ["titre", "Sous-titre"], ["puces", "Liste à puces"], ["numeros", "Liste numérotée"],
       ["warning", "Encadré « Attention »"], ["tip", "Encadré « Astuce »"], ["note", "Encadré « Remarque »"]].forEach(function (c) {
        var o = el("button", "editeur-choix", c[1]); o.type = "button";
        o.addEventListener("click", function () {
          var nouveau = nouveauBloc(c[0]);
          if (position === 0 && !conteneurModele.blocs.length) nouveau.ecart = [];
          conteneurModele.blocs.splice(position, 0, nouveau);
          toucher(chemin);
          rerendre(cible, conteneurModele, chemin);
          var champ = cible.querySelectorAll(":scope > .editeur-bloc")[position];
          var f = champ && champ.querySelector("[contenteditable], input");
          if (f) f.focus();
        });
        menu.append(o);
      });
      b.addEventListener("click", function () { menu.hidden = !menu.hidden; });
      boite.append(b, menu);
      return boite;
    }

    function cadre(b, conteneurModele, k, chemin, contenu, supprimable) {
      var c = el("div", "editeur-bloc editeur-bloc--" + b.type);
      c.append(contenu);
      if (supprimable) {
        var sup = el("button", "editeur-supprimer", "Supprimer");
        sup.type = "button";
        sup.title = "Supprimer ce bloc";
        sup.addEventListener("click", function () {
          conteneurModele.blocs.splice(k, 1);
          if (k === 0 && conteneurModele.blocs.length) conteneurModele.blocs[0].ecart = b.ecart;
          toucher(chemin);
          rerendre(c.parentNode, conteneurModele, chemin);
        });
        c.append(sup);
      }
      return c;
    }

    function rendreBloc(b, conteneurModele, k, chemin) {
      var ici = chemin.concat([b]);
      switch (b.type) {
        case "titre": {
          var t = editable("editeur-titre editeur-titre--" + b.niveau, b.texte, false, function (v) { b.texte = v; toucher(ici); });
          t.setAttribute("data-vide", b.niveau === 1 ? "Titre de la fiche" : "Sous-titre");
          return cadre(b, conteneurModele, k, chemin, t, b.niveau > 1);
        }
        case "paragraphe": {
          var p = editable("editeur-paragraphe", b.texte, true, function (v) { b.texte = v; toucher(ici); }, function (n) {
            var suite = couperApresCurseur(n);
            b.texte = versMarkdown(n).trim(); toucher(ici);
            var nouveau = nouveauBloc("paragraphe"); nouveau.texte = suite;
            conteneurModele.blocs.splice(k + 1, 0, nouveau); toucher(chemin);
            var cible = n.closest(".editeur-bloc").parentNode;
            rerendre(cible, conteneurModele, chemin);
            var champs = cible.querySelectorAll(":scope > .editeur-bloc"); var f = champs[k + 1] && champs[k + 1].querySelector("[contenteditable]");
            if (f) f.focus();
          });
          p.setAttribute("data-vide", "Écrivez ici…");
          return cadre(b, conteneurModele, k, chemin, p, true);
        }
        case "liste": return cadre(b, conteneurModele, k, chemin, rendreElements(b, ici), true);
        case "encadre": {
          var boite = el("div", "editeur-encadre editeur-encadre--" + b.genre);
          var entete = el("div", "editeur-encadre-entete");
          var genre = el("select", "editeur-encadre-genre");
          var genres = Object.keys(TYPES_ENCADRE).filter(function (g) { return ["warning", "tip", "note", "example"].indexOf(g) !== -1 || g === b.genre; });
          genres.forEach(function (g) { var o = el("option", "", TYPES_ENCADRE[g]); o.value = g; genre.append(o); });
          genre.value = b.genre;
          genre.addEventListener("change", function () { b.genre = genre.value; boite.className = "editeur-encadre editeur-encadre--" + b.genre; toucher(ici); });
          var titre = el("input", "editeur-encadre-titre");
          titre.value = b.titre || ""; titre.placeholder = "Titre de l'encadré (facultatif)";
          titre.addEventListener("input", function () { b.titre = titre.value.trim() ? titre.value : null; toucher(ici); });
          entete.append(genre, titre);
          var corps = el("div", "editeur-blocs");
          rendreListe(corps, b.enfants, ici);
          boite.append(entete, corps);
          return cadre(b, conteneurModele, k, chemin, boite, true);
        }
        case "onglets": {
          var groupe = el("div", "editeur-onglets");
          b.onglets.forEach(function (o) {
            var section = el("div", "editeur-onglet");
            section.append(el("div", "editeur-onglet-nom", "Onglet « " + o.nom + " »"));
            var corps = el("div", "editeur-blocs");
            rendreListe(corps, o.enfants, ici);
            section.append(corps);
            groupe.append(section);
          });
          return cadre(b, conteneurModele, k, chemin, groupe, false);
        }
        case "image": {
          var fig = el("figure", "editeur-image");
          var img = el("img"); img.alt = b.alt; img.loading = "lazy";
          img.src = (options.racineImages || "") + b.src.replace(/^(\.\.\/)+/, "");
          fig.append(img, el("figcaption", "", "Capture : " + (b.alt || b.src) + " — ne se modifie pas ici"));
          return cadre(b, conteneurModele, k, chemin, fig, true);
        }
        default: {   // verrou
          var v = el("div", "editeur-verrou");
          if (b.cache) v.hidden = true;
          v.append(el("span", "editeur-verrou-libelle", b.libelle));
          if (b.apercu) v.append(el("span", "editeur-verrou-apercu", b.apercu.length > 140 ? b.apercu.slice(0, 140) + "…" : b.apercu));
          v.title = "Cet élément ne se modifie pas dans l'éditeur visuel (mode avancé possible)";
          var c = cadre(b, conteneurModele, k, chemin, v, false);
          if (b.cache) c.hidden = true;
          return c;
        }
      }
    }

    function rendreElements(b, ici) {
      var liste = el(b.numerotee ? "ol" : "ul", "editeur-liste");
      b.elements.forEach(function (e, n) {
        var li = el("li");
        var champ = editable("editeur-element", e.texte, true, function (v) { e.texte = v; toucher(ici); }, function (noeud) {
          var suite = couperApresCurseur(noeud);
          e.texte = versMarkdown(noeud).trim();
          b.elements.splice(n + 1, 0, { ecart: e.ecart.length ? e.ecart.slice() : [], marque: e.marque, texte: suite, enfants: null });
          toucher(ici);
          var nouvelle = rendreElements(b, ici); liste.replaceWith(nouvelle);
          var f = nouvelle.querySelectorAll(":scope > li > .editeur-element")[n + 1]; if (f) f.focus();
        });
        champ.setAttribute("data-vide", "Élément de liste");
        champ.addEventListener("keydown", function (ev) {
          if (ev.key === "Backspace" && !champ.textContent && !(e.enfants && e.enfants.blocs.length)) {
            ev.preventDefault();
            if (b.elements.length === 1) return;
            b.elements.splice(n, 1);
            if (n === 0) b.elements[0].ecart = [];
            toucher(ici);
            var nouvelle = rendreElements(b, ici); liste.replaceWith(nouvelle);
            var f = nouvelle.querySelectorAll(":scope > li > .editeur-element")[Math.max(0, n - 1)]; if (f) f.focus();
          }
        });
        li.append(champ);
        if (e.enfants && e.enfants.blocs.length) {
          var sous = el("div", "editeur-blocs editeur-sous-blocs");
          rendreListe(sous, e.enfants, ici);
          li.append(sous);
        }
        liste.append(li);
      });
      return liste;
    }

    function markdownActuel() {
      if (avance && zoneAvancee) return zoneAvancee.value;
      return ecrire(modele);
    }

    var zone = el("div", "editeur-blocs");
    rendreListe(zone, modele, []);
    conteneur.textContent = "";
    conteneur.classList.add("editeur-fiche");
    conteneur.append(barre, zone);

    return {
      markdown: markdownActuel,
      focus: function () { var f = conteneur.querySelector("[contenteditable]"); if (f) f.focus(); },
    };
  }

  var api = { lire: lire, ecrire: ecrire, versHtml: versHtml, versMarkdown: versMarkdown, creer: creer, nouveauBloc: nouveauBloc };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  else racine.LiguassoEditeur = api;
})(typeof window !== "undefined" ? window : globalThis);
