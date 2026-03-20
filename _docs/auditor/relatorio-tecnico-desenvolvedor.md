# Relatorio Tecnico para Desenvolvedor - NutrIA-Fullstack

## 1. Resumo tecnico

Projeto auditado com foco em prontidao de producao, coerencia de contratos e reducao de risco operacional. O repositório contem uma base ampla de backend FastAPI, frontend Next.js, workers e documentacao extensa, mas o estado observado e heterogeneo: ha modulos reais convivendo com mocks, contratos quebrados e infraestrutura inconsistente.

Esta rodada implementou a primeira correção estrutural de maior impacto:

- consolidacao do fluxo de autenticacao backend
- normalizacao inicial de sessao entre frontend e backend
- autorizacao minima no modulo de clientes
- correção do entrypoint do container backend
- reforco dos testes de autenticacao

## 2. Arquitetura real observada

### Backend

- stack principal: FastAPI + SQLAlchemy sync + JWT + passlib
- banco default local: SQLite (`backend_python/app/db/__init__.py`)
- modulos de API: auth, clientes, conversas, chatwoot, arquivos, relatorios, monitor e outros
- workers: RabbitMQ, Chatwoot, MinIO, lembretes, automacoes e especializacoes diversas
- servico de IA: camada simples sobre OpenAI com prompts por persona

### Frontend

- stack principal: Next.js App Router + React
- painel do nutricionista com varias paginas
- cliente HTTP centralizado em duas abordagens coexistentes:
  - `frontend/src/lib/api.ts`
  - `frontend/src/lib/api/client.ts` e `frontend/src/lib/api/auth.ts`

### Infra

- `backend_python/docker-compose.yml` sobe apenas backend + RabbitMQ + Redis + MinIO + nginx
- `_infra/docker-compose.yml` esta estruturalmente inconsistente e nao deve ser tratado como fonte confiavel de execucao no estado atual
- `backend_python/Dockerfile` estava apontando para `app.main:app`, mas o app real esta em `main.py`

## 3. Achados por severidade

### Bloqueadores

1. Dockerfile do backend apontava para modulo inexistente.
   - Evidencia: `backend_python/Dockerfile`
   - Impacto: container da API falharia em runtime ao subir com `uvicorn app.main:app`
   - Status: corrigido nesta rodada para `main:app`

2. Ambiente local nao possui dependencias para validacao automatica.
   - Evidencia: `python3 -m pytest -q` falhou com `No module named pytest`; `npm ls --depth=0` mostrou dependencias frontend ausentes
   - Impacto: sem validacao confiavel de teste, lint e build
   - Status: nao corrigido por depender de instalacao de dependencias no ambiente

3. `_infra/docker-compose.yml` apresenta estrutura corrompida/misturada.
   - Evidencia: o arquivo comeca com blocos de servico antes do cabecalho principal e contem nesting invalido de `version` e `services` dentro de `api.build`
   - Impacto: compose nao e confiavel para ambiente real
   - Status: pendente de reconstrução

### Criticos

1. Autenticacao usava SHA-256 direto como hash de senha.
   - Evidencia anterior: `backend_python/app/api/v1/auth.py`
   - Impacto: seguranca insuficiente para credenciais
   - Status: corrigido com bcrypt via passlib e fallback de migracao para hash legado

2. Frontend e backend consumiam contratos de auth divergentes.
   - Evidencia:
     - frontend esperava `/v1/auth/login`, `/v1/auth/me`, `/v1/auth/logout`
     - backend expunha apenas `/api/v1/auth/token`, `/register`, `/verify`
   - Impacto: login real nao funcionava ponta a ponta
   - Status: corrigido com endpoints `/api/v1/auth/login`, `/me`, `/refresh`, `/logout`

3. Sessao do frontend estava fragmentada entre cookie manual e localStorage sem integracao.
   - Evidencia:
     - `frontend/src/lib/auth.ts`
     - `frontend/src/lib/api/client.ts`
     - `frontend/src/middleware.ts`
   - Impacto: middleware, componentes e cliente HTTP nao compartilhavam a mesma sessao
   - Status: parcialmente corrigido ao sincronizar token em cookie e localStorage via `setTokens`/`clearTokens`

4. Tabela/entidade `Nutricionista` estava semanticamente quebrada.
   - Evidencia: `backend_python/app/domain/models/nutricionista.py`
   - Problema: comentario engolindo campos conceituais (`papel`, `contexto_ia`) e codigo dependente dessas propriedades em outros modulos
   - Impacto: risco alto de comportamento incoerente
   - Status: corrigido por propriedades derivadas sem exigir alteracao fisica de schema existente

5. Multi-tenancy prometido mas nao aplicado transversalmente.
   - Evidencia:
     - README e roadmap descrevem isolamento forte por tenant
     - diversos endpoints consultam registros sem filtro por tenant
   - Impacto: risco de vazamento logico de dados
   - Status: mitigacao inicial aplicada apenas no modulo de clientes; restante continua pendente

### Medios

1. `backend_python/docker-compose.yml` nao sobe Postgres, embora a documentacao prometa stack maior.
2. `frontend/src/app/admin/page.tsx` continua simulando login.
3. `frontend/src/app/nutricionista/cadastro/page.tsx` coleta muitos campos que ainda nao sao persistidos de forma estruturada.
4. `backend_python/app/api/v1/chatwoot.py` e `backend_python/app/api/v1/monitor.py` ainda possuem trechos mockados.
5. `backend_python/app/api/v1/conversa.py` e outros modulos seguem usando `dict` cru em request/response, sem schemas fortes.
6. `backend_python/app/services/ai_service.py` nao tinha fallback seguro para ambiente sem chave; nesta rodada foi convertido para resposta mockada quando nao ha `OPENAI_API_KEY`.

## 4. Mudancas implementadas nesta rodada

### Auth e seguranca

- reescrita de `backend_python/app/api/v1/auth.py`
- login por JSON com resposta padronizada
- endpoint `GET /api/v1/auth/me`
- endpoint `POST /api/v1/auth/refresh`
- endpoint `POST /api/v1/auth/logout`
- bcrypt como hash principal
- migracao transparente de hash legado em login bem-sucedido

### Autorizacao minima

- reforco de acesso em `backend_python/app/api/v1/cliente.py`
- restricao de listagem e acesso de cliente por usuario/tenant basico
- bloqueio de vinculacao indevida de clientes

### Frontend

- ajuste de `frontend/src/lib/api/auth.ts` para contratos reais do backend
- ajuste de `frontend/src/lib/api/client.ts` para sincronizar cookie e localStorage
- ajuste de `frontend/src/lib/api.ts` para enviar `Authorization` nas chamadas antigas
- login do nutricionista deixou de ser simulado
- cadastro do nutricionista passou a chamar backend real e autenticar apos criar conta
- layout do modulo do nutricionista nao aplica sidebar/navbar nas telas de auth
- adicao da rota `frontend/src/app/nutricionista/login/page.tsx`

### Operacao

- correção do `CMD` do backend Dockerfile para `main:app`
- ampliacao de `backend_python/tests/test_auth.py`

## 5. Matriz prometido vs implementado

| Area | Prometido | Estado real |
|---|---|---|
| Auth SaaS | login, sessao, roles, tenant no JWT | parcial, com base funcional melhorada nesta rodada |
| Multi-tenancy | isolamento completo em DB/API/arquivos | parcial e inconsistente |
| Painel Next.js | dashboard completo do nutricionista/admin | parcial; varias telas existem, nem todas estao integradas |
| Chatwoot | hub de mensageria operacional | parcial, com webhook e fluxo base implementados |
| Workers | processamento assíncrono robusto | parcial; muitos workers existem, maturidade varia |
| Observabilidade | monitoramento e alertas | basico/mockado |
| CI/CD | pipeline profissional | ausente ou nao validado |
| Infra local/prod | compose confiavel | inconsistente |

## 6. Testes e validacao executados

### Executado com sucesso

- `python3 -m py_compile` nos arquivos alterados do backend
- `python3 -m py_compile tests/test_auth.py`

### Nao executado por restricao do ambiente

- `python3 -m pytest -q`
  - falha: `No module named pytest`
- `npx tsc --noEmit`
  - inviavel no estado atual porque o frontend esta sem dependencias instaladas
- `npm ls --depth=0`
  - confirmou varias dependencias ausentes

## 7. Backlog tecnico recomendado

### Fase 1 - Fechar risco operacional imediato

- reconstruir `_infra/docker-compose.yml`
- instalar dependencias dev e travar processo de setup local
- validar `make dev`, `make test`, `make build`
- padronizar variaveis de ambiente e remover defaults inseguros
- revisar CORS e segredos JWT/OpenAI/MinIO/RabbitMQ

### Fase 2 - Consolidar dominio e contratos

- substituir `dict` cru por schemas Pydantic nas rotas criticas
- normalizar nomes de rotas e recursos
- consolidar cliente HTTP do frontend em uma unica camada
- remover duplicidade entre `lib/auth.ts`, `lib/api.ts` e `lib/api/client.ts`
- formalizar contratos de auth, clientes, conversas e arquivos

### Fase 3 - Multi-tenancy e autorizacao reais

- aplicar filtro de tenant em todos os repositorios e endpoints
- padronizar papeis (`admin`, `owner`, `nutri`, `secretaria`)
- auditar arquivos e conversas quanto a isolamento de dados
- adicionar testes de regressao para acesso cruzado entre tenants

### Fase 4 - Produto e completude

- transformar telas simuladas em fluxos reais
- concluir agenda, cobrancas, campanhas, relatorios e admin
- padronizar estados de erro/sucesso no frontend
- documentar o que ainda e mockado

### Fase 5 - Qualidade e operacao

- CI com backend tests + frontend build/type-check
- coverage minima por modulo critico
- observabilidade real com logs estruturados e health/readiness
- pipeline de deploy versionado e rollback

## 8. Checklist tecnico

### Seguranca

- [x] substituir hash fraco de senha
- [x] adicionar `me` e `refresh`
- [ ] rotacao e armazenamento seguro de secrets
- [ ] auditoria completa de autorizacao
- [ ] webhook verification forte
- [ ] controles de upload e validacao MIME/tamanho

### Backend

- [x] corrigir contrato basico de auth
- [x] corrigir entrypoint do container
- [ ] substituir requests `dict` por schemas
- [ ] tratar erros de forma padronizada
- [ ] remover mocks permanentes ou explicita-los

### Frontend

- [x] login real do nutricionista
- [x] sessao compartilhada entre cookie e localStorage
- [ ] consolidar camada unica de API
- [ ] remover fluxos simulados restantes
- [ ] validar build/type-check

### Infra e DX

- [ ] corrigir compose da pasta `_infra`
- [ ] garantir setup reprodutivel
- [ ] instalar ferramentas de teste/lint localmente
- [ ] validar containers, healthchecks e rede

## 9. Conclusao tecnica

O projeto tem boa densidade de codigo e boa ambicao de produto, mas ainda opera com muita divergencia entre intencao arquitetural e realidade executavel. A melhor estrategia continua sendo a refatoracao incremental: fechar primeiro os riscos estruturais e de seguranca, depois consolidar contratos e, por fim, completar os fluxos de produto.

Esta rodada reduziu o risco no nucleo de autenticacao e restaurou o fluxo minimo de login do nutricionista. O proximo ganho real de maturidade virá de reconstruir a infra de desenvolvimento/producao, aplicar tenant isolation de forma sistemica e remover os mocks dos fluxos centrais.
