# --- Étape 1 : construction des deux sites ---
# (aussi utilisée par les services de rédaction locale : docker compose up asso / dep / test)
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

# --- Étape 2 : PDF de chaque page, pour le bouton « PDF » (generer-pdf.py) ---
# Étape à part : Chromium n'alourdit pas l'image de rédaction. Son installation est mise en
# cache et ne se refait que si ces lignes changent.
FROM python:3.12-slim AS pdf
RUN apt-get update && apt-get install -y --no-install-recommends libatomic1 \
 && pip install --no-cache-dir "playwright>=1.49,<2" \
 && playwright install --with-deps chromium \
 && rm -rf /var/lib/apt/lists/*
WORKDIR /projet
COPY generer-pdf.py .
COPY --from=build /projet/site site
# En cas d'échec, le site est publié quand même : le bouton revient à l'impression du navigateur.
ARG DOMAINE=guide-liguasso.laligue.org
RUN DOMAINE="$DOMAINE" python generer-pdf.py site/association site/departemental \
 || echo "ATTENTION : les PDF n'ont pas pu être créés"

# --- Étape 3 : service des sites statiques en HTTPS (Caddy) ---
FROM caddy:2-alpine AS prod
COPY Caddyfile /etc/caddy/Caddyfile
COPY --from=pdf /projet/site /srv
# Page d'accueil à la racine du site : choix entre le guide des associations et le guide départemental
COPY accueil/ /srv/
