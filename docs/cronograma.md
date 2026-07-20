# Cronograma de Execução

> #### Princípios do cronograma
>
> - **Vertical antes de horizontal:** primeiro um fluxo fim-a-fim magro (subir OFX → ver dashboard), depois aprofundar.
> - **Backend antes do frontend** em cada fatia, mas com o front aparecendo cedo para validar contratos da API.
> - **Testes junto, não no fim:** parsers e engine de regras nascem com teste.
> - **Ritmo sustentável:** os 14 dias de trabalho restantes (Dia 2 ao Dia 15) são espalhados pelos dias úteis de julho no padrão trabalho→trabalho→descanso, além dos fins de semana normais — o mês todo vira o "sprint", não só duas semanas corridas.
> - **Buffer real no fim do mês (31/07)** — projeto solo sempre escorrega; o buffer é parte do plano, não um luxo.
> - Itens **Could/v2** (PDF, recorrências, orçamentos, export) ficam **fora** deste cronograma por design.

---

## Já concluído (antes de julho)

### Dia 1 [26/06/2026]
_Fundação do projeto_
- [x] Setup do repo, estrutura de pastas, README inicial
- [x] Docker Compose: backend + db + frontend
- [x] Configuração por variáveis de ambiente + .env.example
- [x] **Entregável:** `docker compose up` levanta FastAPI vazio + Postgres + shell do front. Repo no GitHub com estrutura das pastas do PROJECT.md.

---

## Semana 1 [29/06/2026 – 05/07/2026]

### Dia 2 [03/07/2026] (sex)
_CI + base do backend + Auth (parte 1)_
- [x] Pipeline de CI: lint + testes
- [x] Cadastro/login com hash de senha — modelo `User`, Argon2/bcrypt, migration Alembic inicial.
- [x] **Entregável:** CI verde no primeiro push; endpoint de signup/login funcional retornando usuário.


---

## Semana 2 [06/07/2026 – 12/07/2026]

### Dia 3 [06/07/2026] (seg)
_Auth (parte 2) + hardening de borda_
- [ ] JWT + refresh token + middleware de auth
- [ ] Rate limiting nas rotas sensíveis
- [ ] **Entregável:** rotas protegidas por JWT, refresh funcionando, rate limit em `/auth` e `/upload`.


### Dia 4 [08/07/2026] (qua)
_Ingestão: OFX_
- [ ] Parser OFX → modelo normalizado — interface `StatementParser` + implementação OFX.
- [ ] **Entregável:** dado um `.ofx`, sai uma lista de transações normalizadas (data, valor, descrição, tipo).

### Dia 5 [09/07/2026] (qui)
_Ingestão: CSV + upload_
- [ ] Parser CSV com mapeamento de colunas
- [ ] Detecção de formato + validação de upload — tipo, tamanho, conteúdo.
- [ ] **Entregável:** endpoint `POST /statements` aceita OFX e CSV, detecta formato e rejeita arquivo inválido sem corromper nada.

---

## Semana 3 [13/07/2026 – 19/07/2026]

### Dia 6 [13/07/2026] (seg)
_Dedup + testes de parser_
- [ ] Deduplicação por hash
- [ ] Testes dos parsers e da engine de regras — parte 1: parsers
- [ ] **Entregável:** reimportar o mesmo extrato não duplica transações; suíte de testes de parser passando no CI.

### Dia 7 [14/07/2026] (ter)
_Classificação + engine de regras_
- [ ] Classificar entrada/saída
- [ ] Engine de regras de categorização + seed de categorias padrão — dicionário keyword/regex, prioridade.
- [ ] **Entregável:** transações importadas já vêm com tipo e categoria via regras determinísticas.


### Dia 8 [16/07/2026] (qui)
_Fechar engine + testes_
- [ ] Testes dos parsers e da engine de regras — parte 2: categorização
- [ ] Ajuste fino do seed e das regras com extrato real anonimizado.
- [ ] **Entregável:** ≥80% das transações categorizadas sem LLM; cobertura do core ≥70%.

### Dia 9 [17/07/2026] (sex)
_Análise / agregações_
- [ ] Agregações por categoria/período — totais, saldo, maiores categorias, por mês.
- [ ] **Entregável:** endpoint de resumo do período retornando o JSON que o dashboard vai consumir.


---

## Semana 4 [20/07/2026 – 26/07/2026]


### Dia 10 [21/07/2026] (ter)
_Frontend: auth + cliente de API_
- [ ] Telas de login/cadastro
- [ ] Setup do client + hooks (TanStack Query), React Router, Tailwind.
- [ ] **Entregável:** login/logout no navegador guardando o token; rotas privadas.

### Dia 11 [22/07/2026] (qua)
_Frontend: upload_
- [ ] Tela de upload com feedback de progresso/erro
- [ ] **Entregável:** subir extrato pelo navegador e ver mensagem de sucesso/erro clara.


### Dia 12 [24/07/2026] (sex)
_Frontend: dashboard_
- [ ] Dashboard com gráficos por categoria — Recharts, totais, pizza/barras.
- [ ] **Entregável:** **MVP fechado** — "subo o extrato e vejo para onde foi o dinheiro".


---

## Semana 5 [27/07/2026 – 31/07/2026]

### Dia 13 [27/07/2026] (seg)
_Frontend: transações + edição_
- [ ] Lista de transações com filtros/busca/edição
- [ ] Correção manual gera/atualiza regra — feedback que melhora as regras.
- [ ] **Entregável:** listar/filtrar/buscar transações e corrigir categoria, com a correção virando regra.


### Dia 14 [29/07/2026] (qua)
_Início do v1: segurança + comparação_
- [ ] Criptografia em repouso de campos sensíveis
- [ ] Comparação com período anterior
- [ ] **Entregável:** campos sensíveis criptografados; dashboard mostra "vs. mês anterior".

### Dia 15 [30/07/2026] (qui)
_Insights, anonimização e fechamento_
- [ ] Anonimização antes de enviar ao LLM
- [ ] Geração de narrativa + recomendações — LLM/template — degrada para template sem LLM.
- [ ] Scan de dependências no CI
- [ ] README com prints/GIF, ADRs das decisões, revisão geral.
- [ ] **Entregável:** insights narrativos opcionais + projeto apresentável no portfólio.


---

<!-- ## Mapa cronograma → milestones

| Milestone | Datas | Conteúdo |
|---|---|---|
| **MVP** | 26/06 – 24/07 | Fundação, auth, ingestão OFX/CSV, dedup, categorização por regras, agregações, dashboard, transações. |
| **v1** (início) | 27/07 – 30/07 | Criptografia em repouso, comparação de períodos, anonimização, insights narrativos, scan de deps. |
| **Buffer** | 31/07 | Ajustes finais, revisão, folga. |
| **v2** (fora do escopo deste cronograma) | — | PDF, recorrências, orçamentos, export, guia self-host. | -->