<div align="center">

# 🔥 Finix

**Transforme seus dados financeiros em oportunidades de crescimento e recuperação.**

[![Status](https://img.shields.io/badge/status-em%20desenvolvimento-blue)]()
[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python&logoColor=white)]()
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)]()
[![React](https://img.shields.io/badge/React-TypeScript-61DAFB?logo=react&logoColor=white)]()
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-336791?logo=postgresql&logoColor=white)]()
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)]()
[![Licença](https://img.shields.io/badge/licença-MIT-lightgrey)]()

</div>

---

## O que é o Finix?

**Finix** é um agente financeiro pessoal que recebe o seu extrato bancário, separa entradas e saídas, **categoriza os gastos automaticamente**, identifica para onde o dinheiro está indo e devolve **análises e recomendações práticas** — tudo isso através de uma plataforma web pensada para uso real e seguro com dados financeiros sensíveis.

O nome nasce da junção de **Finance** + **Phoenix**: assim como a fênix renasce das próprias cinzas, o Finix existe para ajudar você a renascer financeiramente — transformando extratos bagunçados em clareza, e gastos descontrolados em oportunidades de crescimento.

> 📄 A documentação completa de arquitetura, requisitos e roadmap está em [`PROJECT.md`](./PROJECT.md).

---

## Principais ideias

- **Upload de extratos** em OFX, CSV ou PDF
- **Categorização híbrida** — regras locais primeiro, IA opcional para casos ambíguos
- **Dashboards e histórico** para acompanhar a evolução mês a mês
- **Insights em linguagem natural** com recomendações práticas
- **Privacidade em primeiro lugar** — arquitetura local-first, dados sob seu controle

---

## Stack

| Camada | Tecnologias |
|---|---|
| **Backend** | Python 3.12, FastAPI, Pydantic v2, SQLAlchemy 2.0, Alembic |
| **Banco** | PostgreSQL 16 |
| **Frontend** | React + TypeScript, Vite, Tailwind CSS |
| **Infra** | Docker Compose, GitHub Actions (CI) |

---

## Como rodar

### Pré-requisitos
- [Docker](https://docs.docker.com/get-docker/) e Docker Compose

### Passos

```bash
# 1. Clone o repositório
git clone https://github.com/<seu-usuario>/finix.git
cd finix

# 2. Crie seu arquivo de ambiente a partir do exemplo
cp .env.example .env
# (ajuste os valores se quiser; os padrões já funcionam para desenvolvimento)

# 3. Suba tudo
docker compose up --build
```

Pronto. Os serviços ficam disponíveis em:

| Serviço | URL | Descrição |
|---|---|---|
| **Frontend** | http://localhost:5173 | Shell da SPA (mostra o status do backend) |
| **Backend** | http://localhost:8000 | API FastAPI |
| **Docs da API** | http://localhost:8000/docs | Swagger UI interativo |
| **Health check** | http://localhost:8000/health | Liveness da API |
| **Health do DB** | http://localhost:8000/health/db | Verifica a conexão com o Postgres |
| **Postgres** | localhost:5432 | Banco (usuário/senha do `.env`) |

Para parar: `Ctrl+C` e depois `docker compose down` (use `docker compose down -v` para apagar também o volume do banco).

---

## Desenvolvimento

### Backend (fora do Docker, opcional)

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install ".[dev]"
# Aponte o DATABASE_URL para localhost no seu .env, então:
uvicorn app.main:app --reload
pytest          # roda os testes
ruff check .    # lint
```

### Frontend (fora do Docker, opcional)

```bash
cd frontend
npm install
npm run dev
```

---

## Estrutura do projeto

```
finix/
├── docker-compose.yml      # sobe backend + db + frontend
├── .env.example            # modelo de variáveis de ambiente
├── PROJECT.md              # documentação completa (arquitetura, backlog, roadmap)
├── .github/workflows/ci.yml
│
├── backend/                # API FastAPI
│   ├── app/
│   │   ├── api/            # rotas
│   │   ├── services/       # regras de negócio
│   │   ├── repositories/   # acesso a dados
│   │   ├── parsers/        # OFX, CSV, PDF
│   │   ├── categorization/ # engine de regras + LLM adapter
│   │   ├── analysis/       # agregações e insights
│   │   ├── models/         # SQLAlchemy
│   │   ├── schemas/        # Pydantic
│   │   ├── core/           # config, db, security
│   │   └── main.py
│   ├── alembic/            # migrations
│   └── tests/
│
└── frontend/               # SPA React + TS
    └── src/
        ├── components/
        ├── pages/
        ├── api/
        └── lib/
```

---

## Roadmap (resumo)

- 🟢 **MVP** — importar extrato (OFX/CSV), categorizar por regras, dashboard básico
- 🔵 **v1** — comparação entre períodos, insights narrativos, regras personalizadas, criptografia em repouso
- 🟣 **v2** — PDF, recorrências/assinaturas, orçamentos e alertas, exportação

Detalhes completos em [`PROJECT.md`](./PROJECT.md).

---

<div align="center">

*Documento vivo — atualizado conforme o Finix evolui.* 🔥

</div>
