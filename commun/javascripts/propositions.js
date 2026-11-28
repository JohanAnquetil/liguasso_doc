// Proposer une modification de la fiche, ou une nouvelle fiche (ouvert à tous).
// Chaque proposition est relue par un admin ; une fois acceptée, elle devient une pull request
// GitHub. Utilise les outils de commentaires.js (window.LiguassoContrib) et n'apparaît que
// si le service de commentaires répond.
document.addEventListener("liguasso:contributions", function () {
  var C = window.LiguassoContrib;
  var article = document.querySelector("article.md-content__inner");
  if (!C || !article) return;
  var el = C.el;
  var titrePage = article.querySelector("h1").textContent.replace(/¶/g, "").trim();
  var estAccueil = /^[a-z]+$/.test(C.PAGE);   // page d'accueil d'un guide

  // Bouton en haut de la fiche, à côté du bouton PDF
  if (!estAccueil) {
    var modifier = el("button", { type: "button", classe: "bouton-pdf bouton-modifier", title: "Proposer une modification de cette fiche" });
    modifier.innerHTML = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04a1 1 0 0 0 0-1.41l-2.34-2.34a1 1 0 0 0-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z"/></svg>Modifier';
    modifier.addEventListener("click", function () { ouvrir("modification"); });
    var pdf = article.querySelector(".bouton-pdf");
    article.insertBefore(modifier, pdf ? pdf.nextSibling : article.firstChild);
  }

  // Encadré avant les commentaires
  var nouvelle = el("button", { type: "button", classe: "md-button", texte: "Proposer une nouvelle fiche" });
  nouvelle.addEventListener("click", function () { ouvrir("nouvelle"); });
  var encadre = el("div", { classe: "contribuer" },
    el("p", {}, el("strong", { texte: "Une erreur, un oubli ? " }),
      estAccueil ? "Proposez une fiche qui manque au guide." :
        "Proposez une correction de cette fiche avec le bouton « Modifier » en haut de page, ou une fiche qui manque au guide."),
    nouvelle);
  C.section.parentNode.insertBefore(encadre, C.section);

  // --- Fenêtre de proposition ---
  function ouvrir(type) {
    var fenetre = el("dialog", { classe: "proposition md-typeset" });   // md-typeset : styles du guide (boutons)
    var fermer = el("button", { type: "button", classe: "proposition-fermer", "aria-label": "Fermer", texte: "×" });
    var titre = el("h2", { texte: type === "modification" ? "Proposer une modification : " + titrePage : "Proposer une nouvelle fiche" });
    var aide = el("p", { classe: "proposition-aide",
      texte: type === "modification"
        ? (window.LiguassoEditeur
            ? "Cliquez dans un texte pour le modifier ; la barre d'outils met en gras, en italique ou ajoute un lien. « + Ajouter » insère un paragraphe, une liste ou un encadré. Les éléments grisés (encadré Accès, captures, blocs communs) ne se modifient pas ici. L'équipe relira votre proposition avant toute publication."
            : "Modifiez le texte ci-dessous. Il est écrit en Markdown : **gras**, « - » pour une liste, « ## » pour un titre. Laissez tels quels les blocs qui commencent par « !!! », « === » ou « --8<-- ». L'équipe relira votre proposition avant toute publication.")
        : "Décrivez la démarche, étape par étape : « + Ajouter » permet d'insérer une liste numérotée, un sous-titre ou un encadré. Pas besoin d'une mise en forme parfaite : l'équipe relira, complétera et ajoutera les captures d'écran avant publication." });
    var message = el("p", { classe: "commentaires-message", role: "status" });
    var champTitre = el("input", { name: "titre", maxlength: "120", placeholder: "Ex. : Rembourser une adhésion" });
    var texte = el("textarea", { name: "texte", rows: "16", spellcheck: "true",
      placeholder: type === "nouvelle" ? "1. Dans le menu, cliquez sur …\n2. …" : "" });
    var resume = el("input", { name: "resume", maxlength: "300",
      placeholder: type === "modification" ? "Ex. : correction du nom du bouton" : "Ex. : fiche manquante sur les remboursements" });
    var pseudo = el("input", { name: "pseudo", maxlength: "40", autocomplete: "nickname", placeholder: "Prénom ou pseudo" });
    pseudo.value = localStorage.getItem("liguasso-pseudo") || "";
    var piege = el("input", { name: "site_web", tabindex: "-1", autocomplete: "off", "aria-hidden": "true" });
    var widget = C.widgetAltcha();
    var envoyer = el("button", { type: "submit", classe: "md-button md-button--primary", texte: "Envoyer la proposition" });
    var annuler = el("button", { type: "button", classe: "md-button", texte: "Annuler" });
    var champ = function (libelle, entree) { return el("label", { classe: "commentaires-champ" }, el("span", { texte: libelle }), entree); };

    // Place dans le menu (nouvelle fiche) : rubrique, sous-rubrique, nom dans le menu
    var NOUVELLE = "__nouvelle__";
    var menuRubrique = el("select", { name: "menu_rubrique" }, el("option", { value: "", texte: "Chargement du menu…" }));
    var menuNouvelleRubrique = el("input", { name: "menu_nouvelle_rubrique", maxlength: "60", placeholder: "Nom de la nouvelle rubrique", hidden: "" });
    var menuSous = el("select", { name: "menu_sous_rubrique" });
    var menuNouvelleSous = el("input", { name: "menu_nouvelle_sous_rubrique", maxlength: "60", placeholder: "Nom de la nouvelle sous-rubrique", hidden: "" });
    var menuLibelle = el("input", { name: "menu_libelle", maxlength: "60", placeholder: "Par défaut : le titre de la fiche" });
    var rubriques = [];
    function option(valeur, texte) { return el("option", { value: valeur, texte: texte }); }
    function remplirSous() {
      var r = rubriques.filter(function (x) { return x.titre === menuRubrique.value; })[0];
      menuSous.replaceChildren(option("", "Aucune : directement dans la rubrique"));
      (r ? r.sous_rubriques : []).forEach(function (s) { menuSous.append(option(s, s)); });
      menuSous.append(option(NOUVELLE, "+ Nouvelle sous-rubrique…"));
      menuNouvelleSous.hidden = true;
    }
    menuRubrique.addEventListener("change", function () {
      menuNouvelleRubrique.hidden = menuRubrique.value !== NOUVELLE;
      if (!menuNouvelleRubrique.hidden) menuNouvelleRubrique.focus();
      remplirSous();
    });
    menuSous.addEventListener("change", function () {
      menuNouvelleSous.hidden = menuSous.value !== NOUVELLE;
      if (!menuNouvelleSous.hidden) menuNouvelleSous.focus();
    });
    function placeDansLeMenu() {
      var rub = menuRubrique.value === NOUVELLE ? menuNouvelleRubrique.value.trim() : menuRubrique.value;
      var sous = menuSous.value === NOUVELLE ? menuNouvelleSous.value.trim() : menuSous.value;
      return { menu_rubrique: rub || "", menu_sous_rubrique: rub ? sous || "" : "", menu_libelle: rub ? menuLibelle.value.trim() : "" };
    }
    var blocMenu = el("fieldset", { classe: "proposition-menu" },
      el("legend", { texte: "Place dans le menu" }),
      el("p", { classe: "proposition-menu-aide", texte: "Choisissez où la fiche apparaîtra dans le menu du guide, ou créez une rubrique. L'équipe pourra l'ajuster." }),
      champ("Rubrique", el("span", { classe: "proposition-menu-ligne" }, menuRubrique, menuNouvelleRubrique)),
      champ("Sous-rubrique (facultatif)", el("span", { classe: "proposition-menu-ligne" }, menuSous, menuNouvelleSous)),
      champ("Nom dans le menu", menuLibelle));
    if (type === "nouvelle") {
      C.appel("/propositions/menu?page=" + encodeURIComponent(C.PAGE)).then(function (liste) {
        rubriques = liste;
        menuRubrique.replaceChildren(option("", "Je ne sais pas : l'équipe choisira"));
        liste.forEach(function (r) { menuRubrique.append(option(r.titre, r.titre)); });
        menuRubrique.append(option(NOUVELLE, "+ Nouvelle rubrique…"));
        remplirSous();
      }).catch(function () { blocMenu.hidden = true; });
    }

    // Éditeur visuel (editeur-fiche.js) ; à défaut, la zone de texte Markdown
    var Editeur = window.LiguassoEditeur, editeur = null;
    var zone = el("div", { classe: "proposition-zone" });
    var config = document.getElementById("__config");
    var racineImages = new URL((config ? JSON.parse(config.textContent).base : ".").replace(/\/?$/, "/"), location.href).href;
    function installer(markdown) {
      if (Editeur) { editeur = Editeur.creer(zone, markdown, { racineImages: racineImages }); }
      else { zone.replaceChildren(texte); texte.value = markdown; }
    }
    function valeurTexte() { return editeur ? editeur.markdown() : texte.value; }

    var formulaire = el("form", { classe: "proposition-formulaire", novalidate: "" },
      type === "nouvelle" ? champ("Titre de la fiche", champTitre) : null,
      type === "nouvelle" ? blocMenu : null,
      el("div", { classe: "commentaires-champ" }, el("span", { texte: type === "modification" ? "Texte de la fiche" : "Contenu" }), zone),
      champ("Résumé de votre proposition", resume),
      champ("Pseudo", pseudo),
      el("label", { classe: "commentaires-piege" }, "Ne pas remplir ", piege),
      widget, message, el("div", { classe: "commentaires-boutons" }, envoyer, annuler));
    fenetre.append(fermer, titre, aide, formulaire);
    document.body.append(fenetre);
    fenetre.showModal();

    var versions = {};
    if (type === "modification") {
      zone.replaceChildren(el("p", { classe: "proposition-chargement", texte: "Chargement du texte de la fiche…" }));
      envoyer.disabled = true;
      C.appel("/propositions/source?page=" + encodeURIComponent(C.PAGE)).then(function (s) {
        versions = s;
        installer(s.texte);
        envoyer.disabled = false;
        if (editeur) editeur.focus(); else { texte.focus(); texte.setSelectionRange(0, 0); texte.scrollTop = 0; }
      }).catch(function (e) { zone.replaceChildren(); message.textContent = e.message; });
    } else {
      installer("");
      champTitre.focus();
    }

    function clore() { fenetre.close(); fenetre.remove(); }
    fermer.addEventListener("click", clore);
    annuler.addEventListener("click", clore);
    fenetre.addEventListener("cancel", function () { fenetre.remove(); });

    formulaire.addEventListener("submit", function (e) {
      e.preventDefault();
      if ((type === "nouvelle" && !champTitre.value.trim()) || !valeurTexte().trim() || !resume.value.trim() || !pseudo.value.trim()) {
        message.textContent = "Tous les champs sont obligatoires.";
        return;
      }
      var place = type === "nouvelle" ? placeDansLeMenu() : {};
      if ((menuRubrique.value === NOUVELLE && !place.menu_rubrique) || (menuSous.value === NOUVELLE && !menuNouvelleSous.value.trim())) {
        message.textContent = "Donnez un nom à la nouvelle rubrique ou sous-rubrique.";
        return;
      }
      envoyer.disabled = true;
      message.textContent = "Envoi…";
      C.payloadAltcha(widget).then(function (charge) {
        return C.appel("/propositions", { method: "POST", corps: {
          type: type, page: C.PAGE, titre: champTitre.value, texte: valeurTexte(), resume: resume.value,
          pseudo: pseudo.value, blob_sha: versions.blob_sha || "", commit_sha: versions.commit_sha || "",
          menu_rubrique: place.menu_rubrique || "", menu_sous_rubrique: place.menu_sous_rubrique || "",
          menu_libelle: place.menu_libelle || "", site_web: piege.value, altcha: charge } });
      }).then(function () {
        localStorage.setItem("liguasso-pseudo", pseudo.value.trim());
        formulaire.replaceWith(el("div", { classe: "proposition-merci" },
          el("p", { texte: "Merci ! Votre proposition a bien été envoyée. L'équipe Ligu'asso la relira avant toute publication." }),
          (function () { var b = el("button", { type: "button", classe: "md-button md-button--primary", texte: "Fermer" });
            b.addEventListener("click", clore); return b; })()));
        aide.remove();
      }).catch(function (err) {
        message.textContent = err.message;
        envoyer.disabled = false;
        if (widget.reset) widget.reset();
      });
    });
  }
});
