// Noyau des scripts du guide : les règles pures, sans page ni réseau.
// Utilisé par commentaires.js, propositions.js, impression.js et videos.js (window.LiguassoNoyau),
// et testé avec Node : verification/noyau/noyau.test.js (npm run test:noyau).
(function (racine) {
  "use strict";

  // ---------- Guide et page ----------

  // Guide d'après le nom du site (rédaction locale, où chaque guide est servi à la racine)
  function guideDuSite(nomSite) {
    nomSite = nomSite || "";
    if (/\[TEST\]|bac à sable/i.test(nomSite)) return "test";
    if (/—\s*Associations/i.test(nomSite)) return "association";
    return "departemental";
  }

  // Clé d'une page pour le service : « departemental/adhesions-lots », « association » (accueil)…
  //   chemin : location.pathname ; racine : chemin de la racine du guide (« /departemental/ » ou « / »)
  function clePage(chemin, racineGuide, nomSite) {
    var relatif = chemin.slice(racineGuide.length).replace(/(index\.html)?\/?$/, "");
    var guide = racineGuide.replace(/^\/|\/$/g, "") || guideDuSite(nomSite);
    return guide + (relatif ? "/" + relatif : "");
  }

  function estAccueil(page) { return /^[a-z]+$/.test(page); }

  // ---------- Textes affichés ----------

  // « il y a 5 min », « il y a 3 h », « le 12 novembre 2026 »
  function quand(iso, maintenant) {
    var s = ((maintenant === undefined ? Date.now() : maintenant) - new Date(iso).getTime()) / 1000;
    if (s < 3600) return "il y a " + Math.max(1, Math.round(s / 60)) + " min";
    if (s < 86400) return "il y a " + Math.round(s / 3600) + " h";
    return "le " + new Date(iso).toLocaleDateString("fr-FR", { day: "numeric", month: "long", year: "numeric" });
  }

  // ---------- Impression et PDF ----------

  function publicDuGuide(nomSite) {
    return guideDuSite(nomSite) === "association" ? "Gestion Associative" : "Gestion Départementale";
  }

  // « Mis à jour le … » pour un PDF préparé à la mise en ligne, « Extrait le … » à l'impression
  function dateEntete(pdfPrepare, date) {
    return (pdfPrepare ? "Mis à jour le " : "Extrait le ") + (date || new Date()).toLocaleDateString("fr-FR");
  }

  // Bas de page : « Chapitre › Fiche », ou la fiche seule si c'est elle le chapitre
  function basDePage(chapitre, titre) {
    return chapitre && chapitre !== titre ? chapitre + " › " + titre : titre;
  }

  function nomFichierPdf(titre) {
    return "Ligu'asso - " + titre.replace(/[\\/:*?"<>|]/g, "").trim() + ".pdf";
  }

  // ---------- Propositions : place dans le menu ----------

  var NOUVELLE = "__nouvelle__";

  // Choix du formulaire -> champs envoyés au service, ou une erreur à afficher
  function placeDansLeMenu(choix) {
    var nouvelleRubrique = choix.rubrique === NOUVELLE;
    var nouvelleSous = choix.sousRubrique === NOUVELLE;
    var rubrique = (nouvelleRubrique ? choix.nomRubrique : choix.rubrique || "").trim();
    var sous = (nouvelleSous ? choix.nomSousRubrique : choix.sousRubrique || "").trim();
    if ((nouvelleRubrique && !rubrique) || (rubrique && nouvelleSous && !sous)) {
      return { erreur: "Donnez un nom à la nouvelle rubrique ou sous-rubrique." };
    }
    if (!rubrique) return { menu_rubrique: "", menu_sous_rubrique: "", menu_libelle: "" };
    return { menu_rubrique: rubrique, menu_sous_rubrique: sous, menu_libelle: (choix.libelle || "").trim() };
  }

  // ---------- Vidéos : repère ▶ dans le menu ----------

  // Chemins (pathname) des fiches qui ont une vidéo, d'après videos.json
  function fichesAvecVideo(videos, racineUrl) {
    var chemins = {};
    videos.forEach(function (v) { chemins[new URL(v.fiche, racineUrl).pathname] = true; });
    return chemins;
  }

  // Un lien du menu (pas de la table des matières) vers une fiche avec vidéo ?
  function lienAvecVideo(href, dansTableDesMatieres, pageCourante, fiches) {
    if (!href || href.indexOf("#") !== -1 || dansTableDesMatieres) return false;
    return !!fiches[new URL(href, pageCourante).pathname];
  }

  var api = {
    guideDuSite: guideDuSite, clePage: clePage, estAccueil: estAccueil, quand: quand,
    publicDuGuide: publicDuGuide, dateEntete: dateEntete, basDePage: basDePage, nomFichierPdf: nomFichierPdf,
    NOUVELLE: NOUVELLE, placeDansLeMenu: placeDansLeMenu, fichesAvecVideo: fichesAvecVideo, lienAvecVideo: lienAvecVideo,
  };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  else racine.LiguassoNoyau = api;
})(typeof window !== "undefined" ? window : globalThis);
