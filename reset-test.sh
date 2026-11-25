#!/bin/sh
# Remet le bac à sable /test à l'identique du guide départemental.
#   ./reset-test.sh
# Écrase : docs-test/ (pages + test.css) et la navigation de mkdocs.test.yml.
# Ne touche pas : le bandeau (overrides-test/), les vrais guides, commun/.
# Les modifications perdues restent récupérables dans l'historique git.
set -e
cd "$(dirname "$0")"

# 1. Pages : on vide docs-test (sauf les ressources recopiées par sync-commun.sh)
find docs-test -mindepth 1 -maxdepth 1 ! -name img ! -name stylesheets -exec rm -rf {} +
for f in docs-departemental/* docs-departemental/.[!.]*; do
  [ -e "$f" ] || continue
  case "$(basename "$f")" in img|stylesheets) continue ;; esac
  cp -R "$f" docs-test/
done

# 2. Feuille de style propre au bac à sable (vide au départ)
cat > docs-test/test.css <<'EOF'
/* Styles essayés uniquement sur /test.
   Une fois validés, les reporter dans commun/stylesheets/extra.css
   (attention : ce fichier-là s'applique aux deux vrais guides). */
EOF

# 3. Configuration : en-tête du bac à sable + navigation du guide départemental
{
  cat <<'EOF'
INHERIT: ./mkdocs.base.yml
site_name: "[TEST] Guide Ligu'asso — bac à sable"
site_description: "Copie de test du guide départemental, pour essayer des modifications"
docs_dir: docs-test
site_dir: site/test

# Bandeau « Site de test » (overrides-test/main.html)
theme:
  custom_dir: overrides-test

# Styles communs + styles essayés uniquement ici
extra_css:
  - stylesheets/extra.css
  - test.css

EOF
  sed -n '/^nav:/,$p' mkdocs.departemental.yml
} > mkdocs.test.yml

echo "Bac à sable remis à l'identique du guide départemental."
echo "Vérifier avec 'git status', puis committer et pousser pour publier."
