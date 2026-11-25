# --- Étape 1 : construction des deux sites ---
FROM python:3.12-slim AS build
WORKDIR /projet
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN ./sync-commun.sh \
 && mkdocs build --strict -f mkdocs.association.yml \
 && mkdocs build --strict -f mkdocs.departemental.yml

# --- Étape 2 : service des sites statiques en HTTPS (Caddy) ---
FROM caddy:2-alpine AS prod
COPY Caddyfile /etc/caddy/Caddyfile
COPY --from=build /projet/site /srv
