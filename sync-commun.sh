#!/bin/sh
# Recopie les ressources partagées (images, CSS, JavaScript) dans chaque site avant construction.
set -e
for site in docs-association docs-departemental docs-test; do
  mkdir -p "$site/img" "$site/stylesheets" "$site/javascripts"
  cp -Rf commun/img/.        "$site/img/"
  cp -f commun/stylesheets/* "$site/stylesheets/"
  cp -Rf commun/javascripts/. "$site/javascripts/"
done
echo "Ressources partagées synchronisées."
