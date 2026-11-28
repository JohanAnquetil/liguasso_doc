# Service de commentaires du guide (API /api/commentaires, derrière Caddy)
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
 && useradd --system --uid 10001 commentaires \
 && mkdir /donnees && chown commentaires /donnees
COPY app.py ./
COPY liguasso_contrib ./liguasso_contrib
USER commentaires
ENV DONNEES=/donnees
VOLUME /donnees
EXPOSE 8000
# Un seul processus : la base SQLite est partagée en mémoire par un verrou
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1", \
     "--proxy-headers", "--forwarded-allow-ips", "*", "--no-server-header"]
