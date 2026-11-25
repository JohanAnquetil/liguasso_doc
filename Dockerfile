# --- Étape 1 : construction des deux sites ---
FROM python:3.12-slim AS build
WORKDIR /projet
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN ./sync-commun.sh \
 && mkdocs build --strict -f mkdocs.association.yml \
 && mkdocs build --strict -f mkdocs.departemental.yml
# Bac à sable /test : construit sans --strict, et son échec ne bloque jamais les vrais guides
RUN mkdocs build -f mkdocs.test.yml || echo "ATTENTION : le site de test n'a pas pu être construit"

# --- Étape 2 : service des sites statiques en HTTPS (Caddy) ---
FROM caddy:2-alpine AS prod
COPY Caddyfile /etc/caddy/Caddyfile
COPY --from=build /projet/site /srv
