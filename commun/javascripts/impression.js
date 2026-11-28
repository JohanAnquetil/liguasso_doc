// Bouton « PDF » en haut de chaque page, et préparation de la version imprimée :
// entête du guide, onglets tous affichés avec leur nom, pied de page avec l'adresse et la date.
// La mise en forme imprimée est dans stylesheets/extra.css (@media print).
//
// Sur le site publié, le PDF de chaque page est préparé à la mise en ligne (generer-pdf.py,
// fichier page.pdf à côté de la page) : le bouton le télécharge, identique pour tous les
// navigateurs. S'il n'existe pas (rédaction locale), le bouton ouvre l'impression du navigateur.
// generer-pdf.py ouvre chaque page avec ?pdf=<adresse publique de la page>.
document.addEventListener("DOMContentLoaded", function () {
  var article = document.querySelector("article.md-content__inner");
  var titre = article && article.querySelector("h1");
  if (!titre) return;
  var titrePage = titre.textContent.replace(/¶/g, "").trim();
  var adressePdf = new URLSearchParams(location.search).get("pdf");

  // Bouton
  var bouton = document.createElement("a");
  bouton.className = "bouton-pdf";
  bouton.href = "#";
  bouton.title = "Enregistrer cette page en PDF";
  bouton.innerHTML =
    '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 20h14v-2H5v2zM19 9h-4V3H9v6H5l7 7 7-7z"/></svg>PDF';
  bouton.addEventListener("click", function (e) {
    if (bouton.hasAttribute("download")) return; // PDF préparé : téléchargement direct
    e.preventDefault();
    window.print();
  });
  article.insertBefore(bouton, article.firstChild);
  if (!adressePdf && location.protocol.indexOf("http") === 0) {
    fetch("page.pdf", { method: "HEAD" }).then(function (r) {
      if (!r.ok || !/pdf/i.test(r.headers.get("content-type") || "")) return;
      bouton.href = "page.pdf";
      bouton.setAttribute("download", "Ligu'asso - " + titrePage.replace(/[\\/:*?"<>|]/g, "") + ".pdf");
    }).catch(function () {});
  }

  // Entête : reprend la couverture du guide PDF complet
  // (logo ligu'asso, date, « Guide d'utilisation », public du guide)
  var config = document.getElementById("__config");
  var base = config ? JSON.parse(config.textContent).base : ".";
  var logos = base + "/img/logos/";
  var nom = (document.querySelector(".md-header__topic .md-ellipsis") || {}).textContent || "";
  var public_ = /départementales/i.test(nom) ? "Gestion Départementale" : "Gestion Associative";
  var date = (adressePdf ? "Mis à jour le " : "Extrait le ") + new Date().toLocaleDateString("fr-FR");

  var entete = document.createElement("div");
  entete.className = "impression-entete";
  entete.innerHTML =
    '<div class="impression-entete__haut">' +
      '<img src="' + logos + 'liguasso.svg" alt="ligu\'asso">' +
      '<span>' + date + '</span>' +
    '</div>' +
    '<div class="impression-entete__titre">Guide d\u2019utilisation</div>' +
    '<div class="impression-entete__public">' + public_ + '</div>';
  article.insertBefore(entete, article.firstChild);

  // Bas de chaque page imprimée : chapitre et page, numéro de page / total.
  // Le texte vient de la page (onglet actif du menu du guide), d'où un style écrit ici.
  var onglet = document.querySelector(".md-tabs__item--active .md-tabs__link");
  var chapitre = onglet ? onglet.textContent.trim() : "";
  var bas = chapitre && chapitre !== titrePage ? chapitre + " \u203a " + titrePage : titrePage;
  var style = document.createElement("style");
  style.textContent =
    "@media print { @page {" +
      " @bottom-left { content: " + JSON.stringify(bas) + "; }" +
      " @bottom-right { content: \"Page \" counter(page) \" / \" counter(pages); }" +
    " } }";
  document.head.appendChild(style);

  // Onglets (Ligue, UFOLEP, USEP) : leur nom au-dessus de chaque contenu
  document.querySelectorAll(".tabbed-set").forEach(function (set) {
    var noms = set.querySelectorAll(":scope > .tabbed-labels > label");
    set.querySelectorAll(":scope > .tabbed-content > .tabbed-block").forEach(function (bloc, i) {
      if (!noms[i]) return;
      var p = document.createElement("p");
      p.className = "impression-onglet";
      p.textContent = noms[i].textContent.trim();
      bloc.insertBefore(p, bloc.firstChild);
    });
  });

  // Pied : logos des fédérations, adresse de la page, support
  var pied = document.createElement("div");
  pied.className = "impression-pied";
  pied.innerHTML =
    '<div class="impression-pied__logos">' +
      '<img src="' + logos + 'ufolep.png" alt="UFOLEP">' +
      '<img src="' + logos + 'usep.png" alt="USEP">' +
      '<img src="' + logos + 'ligue-enseignement.png" alt="La Ligue de l\'enseignement">' +
    '</div>' +
    '<p>' + (adressePdf || location.href.split(/[?#]/)[0]) + '<br>Support : support.liguasso@laligue.org · 01 43 58 96 08</p>';
  article.appendChild(pied);
});
