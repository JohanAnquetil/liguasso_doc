# --- Étape 1 : construction des deux sites ---
FROM python:3.12-slim AS build
WORKDIR /projet
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# Chromium pour créer le PDF de chaque page (generer-pdf.py). Couche mise en cache : réinstallée
# seulement si cette ligne change.
RUN apt-get update && apt-get install -y --no-install-recommends libatomic1 \
 && pip install --no-cache-dir "playwright>=1.49,<2" \
 && playwright install --with-deps chromium \
 && rm -rf /var/lib/apt/lists/*
COPY . .
RUN ./sync-commun.sh \
 && mkdocs build --strict -f mkdocs.association.yml \
 && mkdocs build --strict -f mkdocs.departemental.yml
# PDF de chaque page, pour le bouton « PDF ». En cas d'échec, le site est publié quand même :
# le bouton revient alors à l'impression du navigateur.
ARG DOMAINE=guide-liguasso.laligue.org
RUN DOMAINE="$DOMAINE" python generer-pdf.py site/association site/departemental \
 || echo "ATTENTION : les PDF n'ont pas pu être créés"
# Bac à sable /test : construit sans --strict, et son échec ne bloque jamais les vrais guides
RUN mkdocs build -f mkdocs.test.yml || echo "ATTENTION : le site de test n'a pas pu être construit"

# --- Étape 2 : service des sites statiques en HTTPS (Caddy) ---
FROM caddy:2-alpine AS prod
COPY Caddyfile /etc/caddy/Caddyfile
COPY --from=build /projet/site /srv
