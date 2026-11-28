// Tutos vidéo : lecture au clic (youtube-nocookie) et repère ▶ dans le menu.
// Les cartes et vignettes sont produites à la construction par hooks/videos.py.
document.addEventListener("DOMContentLoaded", function () {
  // Lecture : l'image d'aperçu est remplacée par le lecteur YouTube seulement au clic
  document.querySelectorAll(".tuto-video__lecteur").forEach(function (bouton) {
    bouton.addEventListener("click", function () {
      var cadre = document.createElement("iframe");
      cadre.src = "https://www.youtube-nocookie.com/embed/" + bouton.dataset.youtube + "?autoplay=1&rel=0";
      cadre.title = bouton.getAttribute("aria-label");
      cadre.allow = "autoplay; encrypted-media; picture-in-picture; fullscreen";
      cadre.allowFullscreen = true;
      var conteneur = document.createElement("div");
      conteneur.className = "tuto-video__cadre";
      conteneur.append(cadre);
      bouton.replaceWith(conteneur);
      cadre.focus();
    });
  });

  // Repère ▶ dans le menu, à côté des fiches qui ont une vidéo
  var config = document.getElementById("__config");
  var base = config ? JSON.parse(config.textContent).base : ".";
  var racine = new URL(base.replace(/\/?$/, "/"), location.href);
  var N = window.LiguassoNoyau;   // règles pures (noyau.js)
  fetch(new URL("videos.json", racine)).then(function (r) { return r.ok ? r.json() : []; }).then(function (videos) {
    var fiches = N.fichesAvecVideo(videos, racine);
    document.querySelectorAll(".md-nav__link[href]").forEach(function (lien) {
      if (!N.lienAvecVideo(lien.getAttribute("href"), !!lien.closest(".md-nav--secondary"), location.href, fiches)) return;
      if (lien.querySelector(".repere-video")) return;
      var repere = document.createElement("span");
      repere.className = "repere-video";
      repere.title = "Cette fiche a un tuto vidéo";
      repere.setAttribute("aria-label", "(tuto vidéo)");
      lien.append(repere);
    });
  }).catch(function () {});
});
