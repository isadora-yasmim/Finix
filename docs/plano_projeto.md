# Agente Financeiro Pessoal

> Um agente que recebe o extrato bancário, separa entradas e saídas, categoriza gastos, identifica para onde o dinheiro está indo, gera análises e dá recomendações — através de uma plataforma web pensada para uso real e seguro com dados financeiros sensíveis.

**Nome de trabalho:** Finix

---

## Sumário

1. [Visão geral](#1-visão-geral)
2. [Objetivos e não-objetivos](#2-objetivos-e-não-objetivos)
3. [Decisões arquiteturais](#3-decisões-arquiteturais)
4. [Stack tecnológica](#4-stack-tecnológica)
5. [Arquitetura do sistema](#5-arquitetura-do-sistema)
6. [Fluxo principal (pipeline)](#6-fluxo-principal-pipeline)
7. [Modelo de dados](#7-modelo-de-dados)
8. [Requisitos funcionais](#8-requisitos-funcionais)
9. [Requisitos não-funcionais](#9-requisitos-não-funcionais)
10. [Segurança e privacidade (LGPD)](#10-segurança-e-privacidade-lgpd)
11. [Categorização híbrida](#11-categorização-híbrida)
12. [Backlog](#12-backlog)
13. [Roadmap / Milestones](#13-roadmap--milestones)
14. [Estrutura de pastas sugerida](#14-estrutura-de-pastas-sugerida)
15. [Métricas de sucesso](#15-métricas-de-sucesso)
16. [Riscos e mitigações](#16-riscos-e-mitigações)
17. [Como destacar no portfólio](#17-como-destacar-no-portfólio)

---

## 1. Visão geral

O **Finix** é uma aplicação web em que o usuário faz upload do extrato do banco (OFX, CSV ou PDF) e recebe de volta:

- Transações **estruturadas e classificadas** (entrada vs. saída).
- **Categorização automática** dos gastos (alimentação, transporte, moradia, lazer, etc.).
- Um **resumo do período**: total gasto, total recebido, saldo, maiores categorias.
- Uma **análise em linguagem natural** ("você gastou 32% a mais com delivery que no mês passado") e **recomendações práticas**.
- **Dashboards e histórico** para acompanhar a evolução mês a mês.

O diferencial do projeto — tanto para uso pessoal quanto como peça de portfólio — é tratar **dados financeiros como dados sensíveis de verdade**: arquitetura local-first, mínima exposição, e a IA usada de forma opcional e controlada.

---

## 2. Objetivos e não-objetivos

### Objetivos
- Importar extratos de diferentes bancos sem digitação manual.
- Classificar e categorizar transações com boa precisão e de forma corrigível pelo usuário.
- Gerar insights acionáveis, não só gráficos bonitos.
- Ser **realmente usável** no dia a dia pelo próprio autor.
- Demonstrar boas práticas de engenharia: testes, segurança, arquitetura limpa, CI.

### Não-objetivos (pelo menos no início)
- ❌ Integração via Open Finance / conexão direta com bancos (escopo regulatório alto).
- ❌ Multiusuário em SaaS público com dados de terceiros (risco e responsabilidade altos no v1).
- ❌ Conciliação contábil profissional / emissão fiscal.
- ❌ App mobile nativo (a web responsiva cobre o MVP).

---

## 3. Decisões arquiteturais

| Decisão | Escolha | Justificativa |
|---|---|---|
| **Backend** | Python + FastAPI | Tipagem com Pydantic, async, ótimo ecossistema de dados, fácil de testar. |
| **Frontend** | React + TypeScript | SPA com componentes reaproveitáveis e boa vitrine de portfólio. |
| **Onde rodar** | **Local-first** (Docker Compose na sua máquina), com caminho para self-host | *Recomendação:* dados financeiros não saem do seu controle. Evita o risco e a responsabilidade legal de hospedar dado sensível em cloud pública multiusuário logo de cara. Quando quiser mostrar online, suba uma instância single-user na sua VPS protegida por VPN/auth. |
| **Categorização** | **Híbrida**: regras locais primeiro, LLM opcional depois | A maioria das transações resolve com regras determinísticas (rápido, grátis, offline, privado). O LLM entra só nos casos ambíguos e na geração da análise narrativa — e é opcional/desligável. |

> **Sobre "tanto faz, me recomende":** comece **100% local com Docker Compose**. É o ambiente mais seguro para os seus dados e o mais simples de desenvolver. A camada de deploy fica desenhada desde o início (12-factor, config por variáveis de ambiente), então migrar para uma VPS self-hosted depois é trivial e vira mais um item de portfólio ("deploy seguro single-tenant").

---

## 4. Stack tecnológica

### Backend
- **Python 3.12+**
- **FastAPI** — API REST.
- **Pydantic v2** — validação e schemas.
- **SQLAlchemy 2.0 + Alembic** — ORM e migrations.
- **PostgreSQL** — banco principal (ou SQLite no modo 100% local single-user).
- **ofxparse / pandas** — parsing de extratos OFX e CSV.
- **pdfplumber** — extração de PDF (fase posterior).
- **pytest** — testes.

### Frontend
- **React + TypeScript**
- **Vite** — build/dev server.
- **TanStack Query** — data fetching/cache.
- **React Router** — navegação.
- **Recharts** (ou Chart.js) — gráficos.
- **Tailwind CSS** — estilização.
- **Zod** — validação de formulários.

### IA / Análise (camada opcional)
- Provedor de LLM via API (ex.: Anthropic ou OpenAI) **atrás de uma interface abstrata**, para poder trocar ou desligar.
- Engine de regras própria (dicionário de palavras-chave + regex) para a categorização determinística.

### Infra / DevX
- **Docker + Docker Compose** — ambiente reproduzível.
- **GitHub Actions** — CI (lint, testes, build).
- **Ruff + Black + mypy** (Python) e **ESLint + Prettier** (front).
- **pre-commit** — hooks de qualidade.

---

## 5. Arquitetura do sistema

```
┌──────────────────────────────────────────────────────────┐
│                     Frontend (React SPA)                   │
│  Upload · Dashboard · Transações · Categorias · Insights   │
└───────────────────────────┬──────────────────────────────┘
                            │ HTTPS / JSON
┌───────────────────────────▼──────────────────────────────┐
│                      Backend (FastAPI)                     │
│                                                            │
│  ┌──────────┐  ┌───────────────┐  ┌────────────────────┐  │
│  │  Auth    │  │  Ingestão     │  │  Análise/Insights  │  │
│  │  (JWT)   │  │  (parsers)    │  │                    │  │
│  └──────────┘  └───────┬───────┘  └─────────┬──────────┘  │
│                        │                     │             │
│             ┌──────────▼──────────┐  ┌───────▼─────────┐   │
│             │ Categorização       │  │  LLM Adapter    │   │
│             │ (regras) ──────────►│  │  (opcional)     │   │
│             └──────────┬──────────┘  └─────────────────┘   │
└────────────────────────┼──────────────────────────────────┘
                         │
              ┌──────────▼──────────┐
              │     PostgreSQL       │
              │  (dados criptog.)    │
              └─────────────────────┘
```

**Princípios:**
- Camadas separadas: `api` (rotas) → `services` (regras de negócio) → `repositories` (acesso a dados).
- Parsers desacoplados por formato, atrás de uma interface comum (`StatementParser`).
- O `LLMAdapter` é uma interface — a aplicação funciona inteira **sem** LLM (degradação graciosa).

---

## 6. Fluxo principal (pipeline)

1. **Upload** — usuário envia o arquivo do extrato.
2. **Detecção de formato** — identifica OFX / CSV / PDF e o banco de origem.
3. **Parsing** — normaliza para um modelo único de transação (data, valor, descrição, tipo).
4. **Deduplicação** — evita reimportar transações já existentes (hash da transação).
5. **Classificação entrada/saída** — pelo sinal do valor / tipo da transação.
6. **Categorização** — regras locais primeiro; ambíguos vão para o LLM (se habilitado).
7. **Persistência** — grava transações + categorias.
8. **Análise** — calcula agregados, compara com períodos anteriores, detecta anomalias.
9. **Insights** — gera o texto de recomendações (LLM opcional, sobre dados **agregados/anonimizados**).
10. **Apresentação** — front exibe dashboard, transações e insights; usuário pode **corrigir** categorias (feedback que melhora as regras).

---

## 7. Modelo de dados

```
User
 ├─ id, email, password_hash, created_at
 └─ settings (llm_enabled, currency, ...)

Account                 (conta/banco do usuário)
 ├─ id, user_id, name, bank, type

Statement               (cada arquivo importado)
 ├─ id, account_id, source_format, period_start, period_end, imported_at, file_hash

Transaction
 ├─ id, account_id, statement_id
 ├─ date, amount, type (INCOME|EXPENSE)
 ├─ description, normalized_description
 ├─ category_id, category_source (RULE|LLM|USER)
 ├─ dedup_hash
 └─ created_at

Category
 ├─ id, name, parent_id (subcategorias), icon, is_default

CategoryRule            (regras de categorização)
 ├─ id, user_id, pattern, match_type (keyword|regex), category_id, priority

Insight                 (análises geradas por período)
 ├─ id, user_id, period, summary_json, narrative_text, generated_at
```

---

## 8. Requisitos funcionais

| ID | Requisito | Prioridade |
|---|---|---|
| RF-01 | Cadastro e login de usuário | Must |
| RF-02 | Upload de extrato (OFX/CSV) | Must |
| RF-03 | Parsing e normalização das transações | Must |
| RF-04 | Deduplicação de transações reimportadas | Must |
| RF-05 | Classificar transações em entrada/saída | Must |
| RF-06 | Categorizar gastos automaticamente (regras) | Must |
| RF-07 | Listar/filtrar/buscar transações | Must |
| RF-08 | Editar categoria de uma transação manualmente | Must |
| RF-09 | Dashboard com totais e gráficos por categoria | Must |
| RF-10 | Comparar período atual com o anterior | Should |
| RF-11 | Gerar análise narrativa + recomendações (LLM opcional) | Should |
| RF-12 | Criar regras de categorização personalizadas | Should |
| RF-13 | Detectar gastos recorrentes / assinaturas | Could |
| RF-14 | Suporte a upload de PDF | Could |
| RF-15 | Definir orçamento por categoria e alertar estouro | Could |
| RF-16 | Exportar relatório (CSV/PDF) | Could |

---

## 9. Requisitos não-funcionais

| ID | Requisito |
|---|---|
| RNF-01 | **Segurança**: dados sensíveis criptografados em repouso; secrets fora do código (ver seção 10). |
| RNF-02 | **Privacidade**: a aplicação funciona 100% offline sem o LLM; dados nunca saem da máquina por padrão. |
| RNF-03 | **Performance**: importar um extrato mensal típico (< 500 transações) em < 3s (sem LLM). |
| RNF-04 | **Confiabilidade**: parsing tolerante a falhas — um arquivo inválido nunca corrompe dados existentes. |
| RNF-05 | **Testabilidade**: cobertura mínima de 70% no core (parsers + categorização). |
| RNF-06 | **Portabilidade**: sobe inteiro com `docker compose up`. |
| RNF-07 | **Manutenibilidade**: arquitetura em camadas, tipagem estática, lint no CI. |
| RNF-08 | **Usabilidade**: responsivo, feedback claro de erros de upload. |

---

## 10. Segurança e privacidade (LGPD)

Esta é a parte que diferencia o projeto. Tratar como requisito de primeira classe.

**Dados e armazenamento**
- Criptografia em repouso para campos sensíveis (ex.: descrições/valores) ou disco/volume criptografado.
- HTTPS obrigatório (TLS) — usar `mkcert` em dev, certificado real no self-host.
- Senhas com **Argon2** ou **bcrypt**; nunca em texto puro.
- Secrets via variáveis de ambiente / `.env` (fora do git) — `.env.example` versionado sem valores reais.

**Autenticação e acesso**
- JWT com expiração curta + refresh token; cookies `HttpOnly` + `Secure` + `SameSite`.
- Rate limiting nas rotas de auth e upload.
- No self-host: colocar atrás de VPN ou auth de borda; instância **single-tenant** (só você).

**Privacidade e LLM**
- LLM é **opt-in** e desligável por config.
- Quando ligado, enviar **apenas dados agregados/anonimizados** (ex.: "categoria X = R$ 1.200, +20% vs. mês anterior"), nunca a transação bruta com identificadores.
- Documentar claramente o que é enviado e para onde (transparência = ponto de portfólio).

**Boas práticas gerais**
- Validar e sanitizar todo upload (tipo, tamanho, conteúdo) — proteger contra arquivos maliciosos.
- Nunca logar dados financeiros em texto puro.
- Dependabot / scan de dependências no CI.
- Política de retenção: permitir o usuário apagar tudo (direito à exclusão / LGPD).

---

## 11. Categorização híbrida

**Camada 1 — Regras (determinística, padrão, offline)**
- Dicionário de palavras-chave → categoria (ex.: `IFOOD`, `UBER`, `99` → Transporte/Alimentação).
- Regex para padrões de descrição de banco.
- Regras do usuário têm prioridade sobre as padrão.
- Resolve a maioria das transações de forma rápida, grátis e privada.

**Camada 2 — LLM (opcional, só para ambíguos)**
- Transações que nenhuma regra cobriu vão em lote para o LLM classificar.
- A resposta vira **uma nova regra sugerida** → o sistema "aprende" e fica menos dependente do LLM com o tempo.

**Camada 3 — Correção humana (a fonte de verdade)**
- Toda categoria pode ser corrigida pelo usuário.
- Correção do usuário pode gerar/atualizar uma regra automaticamente.

**Análise narrativa**
- Gerada pelo LLM sobre o **resumo agregado** do período, não sobre transações cruas.
- Sem LLM: cair para insights baseados em templates ("Sua maior categoria foi X com R$ Y").

---

## 12. Backlog

Organizado em épicos. Prioridade em **MoSCoW** (Must/Should/Could) e estimativa relativa em pontos (P).

### Épico A — Fundação do projeto
- [ ] (Must, 2P) Setup do repo, estrutura de pastas, README inicial.
- [ ] (Must, 2P) Docker Compose (backend + db + frontend).
- [ ] (Must, 2P) Pipeline de CI (lint + testes).
- [ ] (Must, 1P) Configuração por variáveis de ambiente + `.env.example`.

### Épico B — Autenticação e usuário
- [ ] (Must, 3P) Cadastro/login com hash de senha. *(RF-01)*
- [ ] (Must, 3P) JWT + refresh token + middleware de auth. *(RF-01)*
- [ ] (Must, 2P) Rate limiting nas rotas sensíveis. *(RNF-01)*

### Épico C — Ingestão de extratos
- [ ] (Must, 3P) Parser OFX → modelo normalizado. *(RF-02, RF-03)*
- [ ] (Must, 3P) Parser CSV (com mapeamento de colunas). *(RF-02, RF-03)*
- [ ] (Must, 2P) Detecção de formato + validação de upload. *(RF-02, RNF-04)*
- [ ] (Must, 2P) Deduplicação por hash. *(RF-04)*
- [ ] (Could, 5P) Parser PDF. *(RF-14)*

### Épico D — Classificação e categorização
- [ ] (Must, 2P) Classificar entrada/saída. *(RF-05)*
- [ ] (Must, 5P) Engine de regras de categorização + seed de categorias padrão. *(RF-06)*
- [ ] (Should, 3P) Regras personalizadas pelo usuário. *(RF-12)*
- [ ] (Should, 3P) Adapter de LLM para categorizar ambíguos. *(RF-11)*
- [ ] (Should, 2P) Correção manual gera/atualiza regra. *(RF-08)*

### Épico E — Análise e insights
- [ ] (Must, 3P) Agregações por categoria/período. *(RF-09)*
- [ ] (Should, 3P) Comparação com período anterior. *(RF-10)*
- [ ] (Should, 3P) Geração de narrativa + recomendações (LLM/template). *(RF-11)*
- [ ] (Could, 3P) Detecção de recorrências/assinaturas. *(RF-13)*
- [ ] (Could, 3P) Orçamento por categoria + alertas. *(RF-15)*

### Épico F — Frontend
- [ ] (Must, 3P) Telas de login/cadastro.
- [ ] (Must, 3P) Tela de upload com feedback de progresso/erro. *(RF-02)*
- [ ] (Must, 4P) Dashboard com gráficos por categoria. *(RF-09)*
- [ ] (Must, 3P) Lista de transações com filtros/busca/edição. *(RF-07, RF-08)*
- [ ] (Should, 3P) Tela de insights/recomendações. *(RF-11)*
- [ ] (Could, 2P) Tela de configurações (ligar/desligar LLM, moeda). *(RNF-02)*

### Épico G — Segurança e privacidade
- [ ] (Must, 3P) Criptografia em repouso de campos sensíveis. *(RNF-01)*
- [ ] (Must, 2P) Anonimização antes de enviar ao LLM. *(RNF-02)*
- [ ] (Should, 2P) Exclusão total de dados do usuário (LGPD). *(seção 10)*
- [ ] (Should, 2P) Scan de dependências no CI.

### Épico H — Qualidade e deploy
- [ ] (Must, 3P) Testes dos parsers e da engine de regras. *(RNF-05)*
- [ ] (Should, 2P) Guia de self-host na VPS.
- [ ] (Could, 2P) Exportar relatório CSV/PDF. *(RF-16)*

---

## 13. Roadmap / Milestones

### 🟢 MVP — "Importar e ver" *(núcleo usável por você)*
Épicos A, B (mínimo), C (OFX+CSV), D (entrada/saída + regras), E (agregações), F (upload + dashboard + transações).
> **Resultado:** você já consegue subir o extrato e ver para onde o dinheiro foi.

### 🔵 v1 — "Entender e agir"
Comparação entre períodos, insights narrativos, regras personalizadas, correção manual, configurações, criptografia em repouso, anonimização no LLM.
> **Resultado:** vira ferramenta de verdade + bom case de segurança no portfólio.

### 🟣 v2 — "Refinar"
PDF, recorrências/assinaturas, orçamentos e alertas, exportação de relatórios, guia de self-host.

> Sugestão de ritmo para projeto pessoal: feche o **MVP primeiro e use de verdade por um mês** antes de partir pro v1 — o uso real vai redirecionar o backlog melhor que qualquer plano.

---

## 14. Estrutura de pastas sugerida

```
Finix/
├── README.md
├── PROJECT.md                 # este documento
├── docker-compose.yml
├── .env.example
├── .github/workflows/ci.yml
│
├── backend/
│   ├── app/
│   │   ├── api/               # rotas FastAPI
│   │   ├── services/          # regras de negócio
│   │   ├── repositories/      # acesso a dados
│   │   ├── parsers/           # ofx.py, csv.py, pdf.py (+ base.py)
│   │   ├── categorization/    # engine de regras + llm_adapter.py
│   │   ├── analysis/          # agregações e insights
│   │   ├── models/            # SQLAlchemy
│   │   ├── schemas/           # Pydantic
│   │   ├── core/              # config, security, db
│   │   └── main.py
│   ├── alembic/
│   ├── tests/
│   └── pyproject.toml
│
└── frontend/
    ├── src/
    │   ├── components/
    │   ├── pages/             # Login, Upload, Dashboard, Transactions, Insights
    │   ├── api/               # client + hooks (TanStack Query)
    │   ├── lib/
    │   └── App.tsx
    ├── package.json
    └── vite.config.ts
```

---

## 15. Métricas de sucesso

**Do produto (uso real)**
- % de transações categorizadas automaticamente (meta: > 80% sem LLM após algumas correções).
- Tempo de import por extrato.
- Você consegue responder "para onde foi meu dinheiro?" em < 10s.

**Do projeto (portfólio)**
- Cobertura de testes do core ≥ 70%.
- CI verde, README claro com prints/GIF.
- Documentação de segurança visível e honesta.

---

## 16. Riscos e mitigações

| Risco | Impacto | Mitigação |
|---|---|---|
| Formatos de extrato variam muito entre bancos | Alto | Começar por **OFX** (padrão); arquitetura de parsers plugável; testes com arquivos reais anonimizados. |
| Vazamento de dado financeiro | Crítico | Local-first, criptografia, secrets fora do git, single-tenant, anonimização no LLM. |
| Categorização imprecisa frustra o uso | Médio | Correção manual fácil + regras que aprendem; LLM como reforço. |
| Custo/dependência de LLM | Médio | LLM opcional e desligável; regras resolvem o grosso. |
| Escopo crescer demais | Médio | MoSCoW rígido; fechar o MVP e usar antes de expandir. |

---

## 17. Como destacar no portfólio

- **README com história:** problema real → solução → decisões técnicas → prints/GIF do dashboard.
- **Seção de segurança no README:** mostre que você pensou em ameaças e LGPD. Isso te diferencia de quem só faz CRUD.
- **ADRs (Architecture Decision Records):** registre as escolhas (por que local-first, por que híbrido). Mostra maturidade.
- **Diagrama de arquitetura** versionado no repo.
- **Demo segura:** se for mostrar online, use uma instância com **dados fictícios** — nunca os seus reais em ambiente público.
- **Conventional commits + CI verde** dão credibilidade ao histórico.

---

*Documento vivo — ajuste o backlog conforme você usa a ferramenta de verdade.*
