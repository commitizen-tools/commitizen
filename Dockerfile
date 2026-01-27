FROM python:3.13-slim AS builder

WORKDIR /app

# Installer UV pour une installation rapide des dépendances
RUN pip install --no-cache-dir uv

# Argument de build pour la version (passé depuis GitHub Actions)
ARG CZ_VERSION
RUN test -n "$CZ_VERSION" || (echo "CZ_VERSION not set" && false)

# Installer commitizen avec UV
RUN uv pip install --system --no-cache commitizen==${CZ_VERSION}

# Stage runtime
FROM python:3.13-slim

LABEL org.opencontainers.image.source="https://github.com/commitizen-tools/commitizen"
LABEL org.opencontainers.image.description="Commitizen is a release management tool designed for teams"
LABEL org.opencontainers.image.licenses="MIT"

# Installer git (requis pour le fonctionnement de commitizen)
RUN apt-get update && \
    apt-get install -y --no-install-recommends git && \
    rm -rf /var/lib/apt/lists/*

# Copier les packages Python et binaires depuis le builder
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin/cz /usr/local/bin/cz
COPY --from=builder /usr/local/bin/git-cz /usr/local/bin/git-cz

# Répertoire de travail
WORKDIR /workspace

# Point d'entrée sur la commande cz
ENTRYPOINT ["cz"]

# Commande par défaut : afficher la version
CMD ["version"]
