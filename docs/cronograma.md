# Cronograma de Execução
_Duração: 15 dias_

> #### Princípios do cronograma
>
> - **Vertical antes de horizontal:** primeiro um fluxo fim-a-fim magro (subir OFX → ver dashboard), depois aprofundar.
> - **Backend antes do frontend** em cada fatia, mas com o front aparecendo cedo (dia 10) para validar contratos da API.
> - **Testes junto, não no fim:** parsers e engine de regras nascem com teste (dias 6 e 8).
> - **Buffer real no dia 15** — projeto solo sempre escorrega; o buffer é parte do plano, não um luxo.
> - Itens **Could/v2** (PDF, recorrências, orçamentos, export) ficam **fora** destes 15 dias por design.


## Semana 1 [26/06/2026-01/07/2026]
_Fundação + Ingestão (backend)_

### Dia 1 [26/06/2026]
_Fundação do projeto_
- [ ] Setup do repo, estrutura de pastas, README inicial
- [ ] Docker Compose: backend + db + frontend
- [ ] Configuração por variáveis de ambiente + .env.example
- [ ] **Entregável:** `docker compose up` levanta FastAPI vazio + Postgres + shell do front. Repo no GitHub com estrutura das pastas do PROJECT.md.

### Dia 2 [27/06/2026]
_CI + base do backend + Auth (parte 1)_
- [ ] Pipeline de CI: lint + testes
- [ ] Cadastro/login com hash de senha — modelo `User`, Argon2/bcrypt, migration Alembic inicial.
- [ ] **Entregável:** CI verde no primeiro push; endpoint de signup/login funcional retornando usuário.

### Dia 3 [28/06/2026]
_Auth (parte 2) + hardening de borda_
- [ ] JWT + refresh token + middleware de auth
- [ ] Rate limiting nas rotas sensíveis
- [ ] **Entregável:** rotas protegidas por JWT, refresh funcionando, rate limit em `/auth` e `/upload`.

### Dia 4 [29/06/2026]
_Ingestão: OFX_
- [ ] Parser OFX → modelo normalizado — interface `StatementParser` + implementação OFX.
- [ ] **Entregável:** dado um `.ofx`, sai uma lista de transações normalizadas (data, valor, descrição, tipo).

### Dia 5 [30/06/2026]
_Ingestão: CSV + upload_
- [ ] Parser CSV com mapeamento de colunas
- [ ] Detecção de formato + validação de upload — tipo, tamanho, conteúdo.
- [ ] **Entregável:** endpoint `POST /statements` aceita OFX e CSV, detecta formato e rejeita arquivo inválido sem corromper nada.

### Dia 6 [01/07/2026]
_Dedup + testes de parser_
- [ ] Deduplicação por hash
- [ ] Testes dos parsers e da engine de regras — parte 1: parsers
- [ ] **Entregável:** reimportar o mesmo extrato não duplica transações; suíte de testes de parser passando no CI.

---

## Semana 2 [02/07/2026-10/07/2026]
_Categorização + Análise + Frontend_

### Dia 7 [02/07/2026]
_Classificação + engine de regras_
- [ ] Classificar entrada/saída
- [ ] Engine de regras de categorização + seed de categorias padrão — dicionário keyword/regex, prioridade.
- [ ] **Entregável:** transações importadas já vêm com tipo e categoria via regras determinísticas.

### Dia 8 [03/07/2026]
_Fechar engine + testes_
- [ ] Testes dos parsers e da engine de regras — parte 2: categorização
- [ ] Ajuste fino do seed e das regras com extrato real anonimizado.
- [ ] **Entregável:** ≥80% das transações categorizadas sem LLM; cobertura do core ≥70%.

### Dia 9 [04/07/2026]
_Análise / agregações_
- [ ] Agregações por categoria/período — totais, saldo, maiores categorias, por mês.
- [ ] **Entregável:** endpoint de resumo do período retornando o JSON que o dashboard vai consumir.

### Dia 10 [05/07/2026]
_Frontend: auth + cliente de API_
- [ ] Telas de login/cadastro
- [ ] Setup do client + hooks (TanStack Query), React Router, Tailwind.
- [ ] **Entregável:** login/logout no navegador guardando o token; rotas privadas.

### Dia 11 [06/07/2026]
_Frontend: upload_
- [ ] Tela de upload com feedback de progresso/erro
- [ ] **Entregável:** subir extrato pelo navegador e ver mensagem de sucesso/erro clara.

### Dia 12 [07/07/2026]
_Frontend: dashboard_
- [ ] Dashboard com gráficos por categoria — Recharts, totais, pizza/barras.
- [ ] **Entregável:** **MVP fechado** — "subo o extrato e vejo para onde foi o dinheiro".

### Dia 13 [08/07/2026]
_Frontend: transações + edição_
- [ ] Lista de transações com filtros/busca/edição
- [ ] Correção manual gera/atualiza regra — feedback que melhora as regras.
- [ ] **Entregável:** listar/filtrar/buscar transações e corrigir categoria, com a correção virando regra.

### Dia 14 [09/07/2026]
_Início do v1: segurança + comparação_
- [ ] Criptografia em repouso de campos sensíveis
- [ ] Comparação com período anterior
- [ ] **Entregável:** campos sensíveis criptografados; dashboard mostra "vs. mês anterior".

### Dia 15 [10/07/2026]
_Insights, anonimização e fechamento_
- [ ] Anonimização antes de enviar ao LLM
- [ ] Geração de narrativa + recomendações — LLM/template — degrada para template sem LLM.
- [ ] Scan de dependências no CI
- [ ] README com prints/GIF, ADRs das decisões, revisão geral. **Buffer para o que escorregou.**
- [ ] **Entregável:** insights narrativos opcionais + projeto apresentável no portfólio.

---

<!-- ## Mapa cronograma → milestones

| Milestone | Dias | Conteúdo |
|---|---|---|
| **MVP** | 1–13 | Fundação, auth, ingestão OFX/CSV, dedup, categorização por regras, agregações, dashboard, transações. |
| **v1** (início) | 14–15 | Criptografia em repouso, comparação de períodos, anonimização, insights narrativos, scan de deps. |
| **v2** (fora do escopo destes 15 dias) | — | PDF, recorrências, orçamentos, export, guia self-host. | -->

