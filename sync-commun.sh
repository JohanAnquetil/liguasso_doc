#!/bin/sh
# Recopie les ressources partagées (images, CSS) dans chaque site avant construction.
set -e
for site in docs-association docs-departemental docs-test; do
  mkdir -p "$site/img" "$site/stylesheets"
  cp -f commun/img/*        "$site/img/"
  cp -f commun/stylesheets/* "$site/stylesheets/"
done
echo "Ressources partagées synchronisées."
