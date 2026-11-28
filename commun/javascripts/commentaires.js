// Commentaires en bas de chaque page du guide (service commentaires/, API /api/commentaires).
// Pseudo seul, anti-robot ALTCHA, publication après validation d'un admin.
// Si le service ne répond pas (rédaction locale sans lui), la section n'apparaît pas.
(function () {
  var API = window.LIGUASSO_COMMENTAIRES_API || "/api/commentaires";

  document.addEventListener("DOMContentLoaded", function () {
    var article = document.querySelector("article.md-content__inner");
    if (!article || !article.querySelector("h1")) return;

    var config = document.getElementById("__config");
    var base = config ? JSON.parse(config.textContent).base : ".";
    var racine = new URL(base.replace(/\/?$/, "/"), location.href).pathname;   // ex. /departemental/
    var relatif = location.pathname.slice(racine.length).replace(/(index\.html)?\/?$/, "");
    var guide = racine.replace(/^\/|\/$/g, "") || guideLocal();
    var PAGE = guide + (relatif ? "/" + relatif : "");
    var visiteur = identifiantVisiteur();
    var scriptAltcha = new URL(base.replace(/\/?$/, "/") + "javascripts/altcha/", location.href).href;

    function guideLocal() {   // rédaction locale : un seul guide par port, servi à la racine
      var nom = (document.querySelector(".md-header__topic .md-ellipsis") || {}).textContent || "";
      return /test/i.test(nom) ? "test" : /associations/i.test(nom) ? "association" : "departemental";
    }

    function identifiantVisiteur() {
      var id = localStorage.getItem("liguasso-visiteur");
      if (!id) {
        var octets = crypto.getRandomValues(new Uint8Array(18));
        id = btoa(String.fromCharCode.apply(null, octets)).replace(/\+/g, "-").replace(/\//g, "_").replace(/=/g, "");
        localStorage.setItem("liguasso-visiteur", id);
      }
      return id;
    }

    function appel(chemin, options) {
      options = options || {};
      return fetch(API + chemin, {
        method: options.method || "GET",
        headers: { "Content-Type": "application/json", "X-Visiteur": visiteur },
        body: options.corps ? JSON.stringify(options.corps) : undefined,
      }).then(function (r) {
        return r.json().catch(function () { return {}; }).then(function (d) {
          if (!r.ok) throw new Error(d.detail && typeof d.detail === "string" ? d.detail : "Une erreur est survenue. Réessayez.");
          return d;
        });
      });
    }

    function el(tag, attrs) {
      var n = document.createElement(tag);
      for (var k in attrs || {}) {
        if (k === "texte") n.textContent = attrs[k];
        else if (k === "classe") n.className = attrs[k];
        else n.setAttribute(k, attrs[k]);
      }
      for (var i = 2; i < arguments.length; i++) if (arguments[i] != null) n.append(arguments[i]);
      return n;
    }

    function quand(iso) {
      var s = (Date.now() - new Date(iso).getTime()) / 1000;
      if (s < 3600) return "il y a " + Math.max(1, Math.round(s / 60)) + " min";
      if (s < 86400) return "il y a " + Math.round(s / 3600) + " h";
      return "le " + new Date(iso).toLocaleDateString("fr-FR", { day: "numeric", month: "long", year: "numeric" });
    }

    // --- Anti-robot ALTCHA (chargé à la première utilisation) ---
    var altchaPret = null;
    function chargerAltcha() {
      if (!altchaPret) {
        altchaPret = import(scriptAltcha + "altcha.min.js").then(function () {
          return import(scriptAltcha + "fr-fr.js");
        });
      }
      return altchaPret;
    }

    function widgetAltcha() {
      var w = el("altcha-widget", {
        challenge: API + "/defi", language: "fr-fr", auto: "onfocus", name: "altcha",
        configuration: JSON.stringify({ hideLogo: true, hideFooter: true }),
      });
      chargerAltcha();
      return w;
    }

    // Attend la fin de la vérification (lancée dès qu'on touche au formulaire) et renvoie sa preuve
    function payloadAltcha(widget) {
      function valeur() {
        var formulaire = widget.closest("form");
        var champ = formulaire && formulaire.querySelector('input[name="altcha"]');
        return champ && champ.value;
      }
      function etat() { return widget.getState ? widget.getState() : ""; }
      return chargerAltcha().then(function () {
        return new Promise(function (ok, ko) {
          var debut = Date.now();
          if ((etat() === "unverified" || etat() === "expired") && widget.verify) widget.verify();
          (function verifier() {
            if (valeur()) return ok(valeur());
            if (etat() === "error" || Date.now() - debut > 60000) {
              return ko(new Error("La vérification anti-robot a échoué. Réessayez."));
            }
            if (etat() === "expired" && widget.verify) widget.verify();
            setTimeout(verifier, 150);
          })();
        });
      });
    }

    // --- Section ---
    var section = el("section", { classe: "commentaires", id: "commentaires" });
    var titre = el("h2", { texte: "Commentaires" });
    var intro = el("p", { classe: "commentaires-intro",
      texte: "Une question, une astuce, une précision ? Les commentaires sont publiés après relecture par l'équipe Ligu'asso." });
    var liste = el("ol", { classe: "commentaires-liste" });
    var message = el("p", { classe: "commentaires-message", role: "status" });
    var formulaire = construireFormulaire();
    section.append(titre, intro, liste, message, formulaire);

    var commentaires = [];

    function charger() {
      return appel("?page=" + encodeURIComponent(PAGE)).then(function (donnees) {
        commentaires = donnees;
        if (!section.isConnected) article.append(section);
        afficher();
      });
    }

    function afficher() {
      var publies = commentaires.filter(function (c) { return !c.en_attente; }).length;
      titre.textContent = publies ? "Commentaires (" + publies + ")" : "Commentaires";
      var enfants = {};
      commentaires.forEach(function (c) { if (c.parent_id) (enfants[c.parent_id] = enfants[c.parent_id] || []).push(c); });
      liste.replaceChildren.apply(liste, commentaires.filter(function (c) { return !c.parent_id; }).map(function (c) {
        var item = carte(c);
        if (enfants[c.id]) item.append(el.apply(null, ["ol", { classe: "commentaires-reponses" }].concat(enfants[c.id].map(carte))));
        return item;
      }));
    }

    function carte(c) {
      var entete = el("div", { classe: "commentaire-entete" },
        el("strong", { texte: c.pseudo }),
        c.equipe ? el("span", { classe: "commentaire-equipe", texte: "Équipe" }) : null,
        el("span", { classe: "commentaire-date", texte: quand(c.cree_le) }));
      var item = el("li", { classe: "commentaire" + (c.en_attente ? " commentaire--attente" : ""), id: "commentaire-" + c.id },
        entete, el("p", { classe: "commentaire-texte", texte: c.texte }));
      if (c.en_attente) {
        item.append(el("p", { classe: "commentaire-statut", texte: "En attente de validation — visible par vous seul·e pour l'instant." }));
        return item;
      }
      var actions = el("div", { classe: "commentaire-actions" });
      var like = el("button", { type: "button", classe: "commentaire-like", "aria-pressed": String(c.aime),
        title: c.aime ? "Je n'aime plus" : "J'aime" }, el("span", { "aria-hidden": "true", texte: "♥" }), " " + c.likes);
      like.addEventListener("click", function () {
        like.disabled = true;
        appel("/" + c.id + "/like", { method: "POST" }).then(function (r) {
          c.aime = r.aime; c.likes = r.likes; afficher();
        }).catch(function (e) { alert(e.message); like.disabled = false; });
      });
      actions.append(like);
      var repondre = el("button", { type: "button", texte: "Répondre" });
      repondre.addEventListener("click", function () { ouvrirReponse(c, item); });
      actions.append(repondre);
      if (!c.equipe && !c.de_moi) {
        var signaler = el("button", { type: "button", classe: "commentaire-signaler", texte: "Signaler" });
        signaler.addEventListener("click", function () { ouvrirSignalement(c, item, signaler); });
        actions.append(signaler);
      }
      item.append(actions);
      return item;
    }

    // --- Formulaire (nouveau commentaire ou réponse) ---
    var parentId = null;
    function construireFormulaire() {
      var f = el("form", { classe: "commentaires-formulaire", novalidate: "" });
      var contexte = el("p", { classe: "commentaires-contexte", hidden: "" });
      var pseudo = el("input", { name: "pseudo", maxlength: "40", required: "", autocomplete: "nickname",
        placeholder: "Prénom ou pseudo" });
      pseudo.value = localStorage.getItem("liguasso-pseudo") || "";
      var texte = el("textarea", { name: "texte", maxlength: "2000", required: "", rows: "4",
        placeholder: "Votre commentaire" });
      var piege = el("input", { name: "site_web", tabindex: "-1", autocomplete: "off", "aria-hidden": "true" });
      var champPiege = el("label", { classe: "commentaires-piege" }, "Ne pas remplir ", piege);
      var widget = widgetAltcha();
      var envoyer = el("button", { type: "submit", classe: "md-button md-button--primary", texte: "Envoyer" });
      var annuler = el("button", { type: "button", classe: "md-button", texte: "Annuler la réponse", hidden: "" });
      var mentions = el("p", { classe: "commentaires-mentions",
        texte: "Seuls le pseudo et le texte sont publiés. Aucune adresse mail n'est demandée ; votre adresse IP n'est pas conservée en clair." });
      f.append(contexte,
        el("label", { classe: "commentaires-champ" }, el("span", { texte: "Pseudo" }), pseudo),
        el("label", { classe: "commentaires-champ" }, el("span", { texte: "Commentaire" }), texte),
        champPiege, widget, el("div", { classe: "commentaires-boutons" }, envoyer, annuler), mentions);

      annuler.addEventListener("click", function () { fermerReponse(); });
      f.addEventListener("submit", function (e) {
        e.preventDefault();
        if (!pseudo.value.trim() || !texte.value.trim()) {
          message.textContent = "Indiquez un pseudo et votre commentaire.";
          return;
        }
        envoyer.disabled = true;
        message.textContent = "Envoi…";
        payloadAltcha(widget).then(function (charge) {
          return appel("", { method: "POST", corps: {
            page: PAGE, pseudo: pseudo.value, texte: texte.value, parent_id: parentId,
            site_web: piege.value, altcha: charge } });
        }).then(function () {
          localStorage.setItem("liguasso-pseudo", pseudo.value.trim());
          texte.value = "";
          message.textContent = "Merci ! Votre commentaire sera visible après validation par l'équipe.";
          fermerReponse();
          return charger();
        }).catch(function (err) {
          message.textContent = err.message;
        }).then(function () {
          envoyer.disabled = false;
          if (widget.reset) widget.reset();
        });
      });
      f._contexte = contexte; f._annuler = annuler; f._texte = texte;
      return f;
    }

    function ouvrirReponse(c, item) {
      parentId = c.id;
      formulaire._contexte.textContent = "Réponse à " + c.pseudo;
      formulaire._contexte.hidden = false;
      formulaire._annuler.hidden = false;
      item.append(formulaire);
      formulaire._texte.focus();
    }

    function fermerReponse() {
      parentId = null;
      formulaire._contexte.hidden = true;
      formulaire._annuler.hidden = true;
      section.insertBefore(formulaire, null);
    }

    // --- Signalement ---
    function ouvrirSignalement(c, item, bouton) {
      if (item.querySelector(".commentaire-signalement")) return;
      var motif = el("select", { name: "motif" },
        el("option", { value: "spam", texte: "Spam ou publicité" }),
        el("option", { value: "propos", texte: "Propos inappropriés" }),
        el("option", { value: "faux", texte: "Information fausse" }),
        el("option", { value: "autre", texte: "Autre" }));
      var precision = el("input", { name: "precision", maxlength: "300", placeholder: "Précision (facultatif)" });
      var widget = widgetAltcha();
      var envoyer = el("button", { type: "submit", classe: "md-button md-button--primary", texte: "Signaler" });
      var annuler = el("button", { type: "button", classe: "md-button", texte: "Annuler" });
      // novalidate : sinon le widget anti-robot bloque l'envoi par la validation native du navigateur
      var f = el("form", { classe: "commentaire-signalement", novalidate: "" },
        el("p", { texte: "Pourquoi signalez-vous ce commentaire ?" }), motif, precision, widget,
        el("div", { classe: "commentaires-boutons" }, envoyer, annuler));
      annuler.addEventListener("click", function () { f.remove(); });
      f.addEventListener("submit", function (e) {
        e.preventDefault();
        envoyer.disabled = true;
        payloadAltcha(widget).then(function (charge) {
          return appel("/" + c.id + "/signaler", { method: "POST",
            corps: { motif: motif.value, precision: precision.value, altcha: charge } });
        }).then(function (r) {
          f.replaceWith(el("p", { classe: "commentaire-statut",
            texte: r.deja_signale ? "Vous avez déjà signalé ce commentaire." : "Merci, l'équipe va examiner ce commentaire." }));
          bouton.remove();
        }).catch(function (err) {
          alert(err.message); envoyer.disabled = false; if (widget.reset) widget.reset();
        });
      });
      item.append(f);
      motif.focus();
    }

    charger().catch(function () { /* service indisponible : pas de section */ });
  });
})();
