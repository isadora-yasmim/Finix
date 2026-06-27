FROM python:3.12-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app

# Dependências do sistema (psycopg precisa de libpq em runtime; a wheel binary já
# traz o necessário, mas mantemos curl para healthcheck opcional).
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# Instala dependências a partir do pyproject. Copiamos o mínimo primeiro para
# aproveitar o cache de camadas.
COPY pyproject.toml ./
COPY app ./app
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir ".[dev]"

# O restante do código é montado via volume em dev (ver docker-compose.yml),
# mas copiamos também para a imagem ficar autossuficiente.
COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
