# ==========================================================================
# Finix — imagem de PRODUÇÃO (usada pela pipeline de CI/CD).
#
# Multi-stage: o estágio 1 compila o frontend (React/Vite) e o estágio 2 empacota
# a API FastAPI servindo esse build estático. Uma imagem = uma unidade de deploy,
# promovida sem rebuild de staging para production.
#
# Os Dockerfiles em backend/ e frontend/ continuam sendo os de DESENVOLVIMENTO
# (docker compose, hot reload).
# ==========================================================================

# ---------- Estágio 1: build do frontend ----------
FROM node:20-alpine AS frontend

WORKDIR /frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

COPY frontend/ ./
# Mesma origem da API: chamadas relativas ("/health"), sem CORS entre domínios.
ENV VITE_API_URL=""
RUN npm run build


# ---------- Estágio 2: runtime da API ----------
FROM python:3.12-slim AS runtime

# Commit que gerou a imagem (passado pela pipeline) — exposto em /health/version.
ARG GIT_SHA=dev

# FORWARDED_ALLOW_IPS: atrás do proxy do provedor (TLS terminado lá), confia no
# X-Forwarded-For para o rate limit por IP enxergar o cliente real.
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    GIT_SHA=${GIT_SHA} \
    STATIC_DIR=/app/static \
    PORT=8000 \
    FORWARDED_ALLOW_IPS=*

WORKDIR /app

# Só dependências de runtime (sem o extra [dev]: pytest, ruff, mypy...).
COPY backend/pyproject.toml ./
COPY backend/app ./app
RUN pip install .

COPY backend/alembic.ini ./
COPY backend/alembic ./alembic
COPY --from=frontend /frontend/dist ./static

# Não roda como root.
RUN useradd --create-home --uid 1000 finix
USER 1000

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD python -c "import os, urllib.request; urllib.request.urlopen(f'http://127.0.0.1:{os.environ[\"PORT\"]}/health', timeout=4)"

# Aplica as migrations e sobe a API. "sh -c" expande ${PORT}, definido pelo
# provedor (o Render usa 10000).
CMD ["sh", "-c", "alembic upgrade head && exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT} --proxy-headers"]
