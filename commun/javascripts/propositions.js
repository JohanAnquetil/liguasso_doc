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
        ? "Modifiez le texte ci-dessous. Il est écrit en Markdown : **gras**, « - » pour une liste, « ## » pour un titre. Laissez tels quels les blocs qui commencent par « !!! », « === » ou « --8<-- » si vous ne savez pas à quoi ils servent. L'équipe relira votre proposition avant toute publication."
        : "Décrivez la démarche, étape par étape. Pas besoin d'une mise en forme parfaite : l'équipe relira, complétera et ajoutera les captures d'écran avant publication." });
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

    var formulaire = el("form", { classe: "proposition-formulaire", novalidate: "" },
      type === "nouvelle" ? champ("Titre de la fiche", champTitre) : null,
      champ(type === "modification" ? "Texte de la fiche" : "Contenu", texte),
      champ("Résumé de votre proposition", resume),
      champ("Pseudo", pseudo),
      el("label", { classe: "commentaires-piege" }, "Ne pas remplir ", piege),
      widget, message, el("div", { classe: "commentaires-boutons" }, envoyer, annuler));
    fenetre.append(fermer, titre, aide, formulaire);
    document.body.append(fenetre);
    fenetre.showModal();

    var versions = {};
    if (type === "modification") {
      texte.value = "Chargement du texte de la fiche…";
      texte.disabled = true; envoyer.disabled = true;
      C.appel("/propositions/source?page=" + encodeURIComponent(C.PAGE)).then(function (s) {
        texte.value = s.texte; versions = s;
        texte.disabled = false; envoyer.disabled = false;
        texte.focus(); texte.setSelectionRange(0, 0); texte.scrollTop = 0;   // début de la fiche
      }).catch(function (e) { texte.value = ""; message.textContent = e.message; });
    } else {
      champTitre.focus();
    }

    function clore() { fenetre.close(); fenetre.remove(); }
    fermer.addEventListener("click", clore);
    annuler.addEventListener("click", clore);
    fenetre.addEventListener("cancel", function () { fenetre.remove(); });

    formulaire.addEventListener("submit", function (e) {
      e.preventDefault();
      if ((type === "nouvelle" && !champTitre.value.trim()) || !texte.value.trim() || !resume.value.trim() || !pseudo.value.trim()) {
        message.textContent = "Tous les champs sont obligatoires.";
        return;
      }
      envoyer.disabled = true;
      message.textContent = "Envoi…";
      C.payloadAltcha(widget).then(function (charge) {
        return C.appel("/propositions", { method: "POST", corps: {
          type: type, page: C.PAGE, titre: champTitre.value, texte: texte.value, resume: resume.value,
          pseudo: pseudo.value, blob_sha: versions.blob_sha || "", commit_sha: versions.commit_sha || "",
          site_web: piege.value, altcha: charge } });
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
