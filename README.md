<div align="center">

# 🥗 NutrIA-Pro Platform

### Plataforma SaaS completa para nutricionistas
Automatize a comunicação, gerencie consultas e fidelize seus clientes — tudo em um só lugar.

---

[![Status](https://img.shields.io/badge/status-em%20desenvolvimento-yellow?style=flat-square)]()
[![Stack](https://img.shields.io/badge/backend-FastAPI-009688?style=flat-square&logo=fastapi)]()
[![Stack](https://img.shields.io/badge/frontend-Next.js-000000?style=flat-square&logo=next.js)]()
[![Stack](https://img.shields.io/badge/fila-RabbitMQ-FF6600?style=flat-square&logo=rabbitmq)]()
[![Stack](https://img.shields.io/badge/banco-PostgreSQL-336791?style=flat-square&logo=postgresql)]()
[![Stack](https://img.shields.io/badge/containers-Docker-2496ED?style=flat-square&logo=docker)]()
[![License](https://img.shields.io/badge/licença-Privado-red?style=flat-square)]()

</div>

---

## 📋 Índice

- [Sobre o Projeto](#sobre-o-projeto)
- [Funcionalidades Principais](#funcionalidades-principais)
- [Arquitetura Geral](#arquitetura-geral)
- [Stack Tecnológico](#stack-tecnológico)
- [Estrutura do Repositório](#estrutura-do-repositório)
- [Pré-requisitos](#pré-requisitos)
- [Configuração do Ambiente Local](#configuração-do-ambiente-local)
- [Variáveis de Ambiente](#variáveis-de-ambiente)
- [Executando os Serviços](#executando-os-serviços)
- [Migrations do Banco de Dados](#migrations-do-banco-de-dados)
- [Rodando os Testes](#rodando-os-testes)
- [Arquitetura Multi-Tenant](#arquitetura-multi-tenant)
- [Arquitetura de Mensageria](#arquitetura-de-mensageria)
- [Workers e Filas](#workers-e-filas)
- [Engine de Automação](#engine-de-automação)
- [Estratégia de Escalonamento](#estratégia-de-escalonamento)
- [Observabilidade](#observabilidade)
- [Segurança](#segurança)
- [Roadmap](#roadmap)
- [Contribuindo](#contribuindo)
- [Licença](#licença)

---

## 🎯 Sobre o Projeto

O **NutrIA-Pro** é uma plataforma SaaS multi-tenant projetada especificamente para nutricionistas e clínicas de nutrição. A plataforma centraliza toda a comunicação com clientes em um único hub (Chatwoot), automatiza fluxos de atendimento via n8n, gerencia consultas e cobranças, e oferece um painel completo de gestão — tudo isso com uma arquitetura construída para suportar milhares de profissionais simultaneamente.

### O problema que resolvemos

Nutricionistas perdem tempo valioso gerenciando manualmente:
- Mensagens de clientes em múltiplos canais (WhatsApp, Instagram, e-mail...)
- Agendamento e confirmação de consultas
- Envio de planos alimentares e materiais
- Follow-ups pós-consulta
- Cobranças e lembretes de pagamento

O NutrIA-Pro **automatiza todo esse fluxo**, permitindo que o profissional foque no que realmente importa: o cuidado com seus clientes.

### Como funciona (visão geral)

```
Cliente → WhatsApp/Telegram/Instagram/E-mail
              ↓
          [Chatwoot] (hub de comunicação)
              ↓ webhook
          [API FastAPI] (recebe e publica na fila)
              ↓
          [RabbitMQ] (fila de mensagens)
              ↓
          [Workers] (processam assincronamente)
              ↓
     ┌────────────────────────────┐
     │  Banco de Dados (PostgreSQL)│
     │  Automações (n8n)          │
     │  Arquivos (MinIO)          │
     │  Cache (Redis)             │
     └────────────────────────────┘
              ↓
     [Dashboard Next.js] ← Nutricionista visualiza tudo
```

---

## ✨ Funcionalidades Principais

### Para o Nutricionista (tenant)

| Funcionalidade | Descrição |
|---|---|
| 📨 **Central de Mensagens** | Visualize e gerencie todas as conversas com clientes em um único lugar |
| 📅 **Agendamento de Consultas** | Agende, confirme e gerencie consultas com calendário integrado |
| 🤖 **Automações Inteligentes** | Configure fluxos automáticos de boas-vindas, lembretes, follow-ups e reativação |
| 👥 **CRM de Clientes** | Histórico completo de cada cliente: conversas, consultas, anotações clínicas e arquivos |
| 📁 **Gestão de Arquivos** | Envie planos alimentares, PDFs e materiais diretamente pelo chat |
| 📣 **Campanhas** | Dispare mensagens segmentadas para grupos de clientes |
| 💳 **Cobranças** | Gere links de pagamento (PIX, cartão) e acompanhe o status |
| 📊 **Relatórios** | Métricas de atendimento, engajamento e financeiro |

### Para a Plataforma (admin)

| Funcionalidade | Descrição |
|---|---|
| 🏢 **Gestão de Tenants** | Visualize, ative, suspenda e altere planos de qualquer tenant |
| 📦 **Planos e Limites** | Configure planos de assinatura com limites e funcionalidades diferentes |
| 🔍 **Monitoramento** | Dashboards de métricas, saúde das filas e logs de execução |
| ⚡ **DLQ Monitor** | Visualize e reprocesse mensagens que falharam no processamento |

---

## 🏛️ Arquitetura Geral

A plataforma é construída em torno de **quatro pilares arquiteturais**:

### 1. Hub de Comunicação Centralizado (Chatwoot)
Todos os canais de comunicação (WhatsApp, Telegram, Instagram, Facebook, e-mail, formulários web) são conectados ao Chatwoot. Cada nutricionista possui sua própria **Inbox** dentro do Chatwoot, que funciona como o **identificador do tenant** no sistema.

### 2. Processamento Assíncrono por Filas (RabbitMQ)
Nenhuma mensagem é processada de forma síncrona. O webhook do Chatwoot publica eventos no RabbitMQ imediatamente, e workers independentes consomem e processam esses eventos. Isso garante:
- Respostas instantâneas ao webhook (sem timeout)
- Processamento confiável com retry automático
- Escalonamento horizontal sem mudanças de código

### 3. Engine de Automação (n8n)
O n8n atua como motor de automação de negócio. Workers acionam workflows do n8n via webhook, que por sua vez chamam a API interna da plataforma para executar ações (enviar mensagens, agendar tarefas, atualizar registros).

### 4. Multi-Tenancy por Isolamento de Dados
Cada nutricionista é um tenant completamente isolado. Todos os modelos de dados incluem `tenant_id`, e o sistema garante que nenhum tenant possa acessar dados de outro — tanto por design da aplicação quanto por testes automatizados de isolamento.

---

## 🛠️ Stack Tecnológico

| Componente | Tecnologia | Função |
|---|---|---|
| **Backend API** | FastAPI (Python) | API REST principal, recepção de webhooks, lógica de negócio |
| **Workers** | FastAPI + aio-pika | Consumidores de fila RabbitMQ, processamento assíncrono |
| **Banco de Dados** | PostgreSQL | Armazenamento principal de dados |
| **Fila de Mensagens** | RabbitMQ | Broker de mensagens, DLQ, roteamento de eventos |
| **Cache** | Redis | Cache de configurações, rate limiting, sessões, locks distribuídos |
| **Armazenamento de Arquivos** | MinIO | Armazenamento de objetos compatível com S3 |
| **Hub de Comunicação** | Chatwoot | Centralização de canais de atendimento |
| **Engine de Automação** | n8n | Workflows de automação de negócio |
| **Frontend** | Next.js 14+ (TypeScript) | Dashboard do nutricionista e painel admin |
| **Containerização** | Docker + Docker Compose | Empacotamento e orquestração de serviços |
| **Proxy / Túnel** | Cloudflare Tunnel (Cloudflared) | Exposição segura dos serviços, TLS, DDoS protection |
| **Hospedagem Inicial** | Contabo VPS | Servidor de produção único (expansível) |
| **Migrations** | Alembic | Controle de versão do schema do banco de dados |

---

## 📁 Estrutura do Repositório

```
nutriapro/
│
├── services/
│   ├── api/                        # Backend FastAPI
│   │   ├── app/
│   │   │   ├── main.py             # Entry point da aplicação
│   │   │   ├── config.py           # Configurações (pydantic-settings)
│   │   │   ├── database.py         # Engine e sessão SQLAlchemy
│   │   │   ├── dependencies.py     # Dependências compartilhadas FastAPI
│   │   │   ├── models/             # Modelos ORM (SQLAlchemy)
│   │   │   ├── schemas/            # Schemas Pydantic (request/response)
│   │   │   ├── routers/            # Routers FastAPI (um por domínio)
│   │   │   ├── services/           # Camada de lógica de negócio
│   │   │   ├── repositories/       # Camada de acesso a dados
│   │   │   ├── integrations/       # Clientes de serviços externos
│   │   │   ├── middleware/         # Middlewares customizados
│   │   │   └── utils/              # Utilitários compartilhados
│   │   ├── tests/
│   │   │   ├── unit/
│   │   │   ├── integration/
│   │   │   └── conftest.py
│   │   ├── alembic/                # Migrations do banco de dados
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── .env.example
│   │
│   ├── workers/                    # Workers RabbitMQ
│   │   ├── app/
│   │   │   ├── main.py             # Entry point — registra todos os consumers
│   │   │   ├── consumers/          # Um consumer por fila
│   │   │   ├── handlers/           # Lógica de negócio por tipo de evento
│   │   │   └── utils/              # Retry, idempotência, helpers
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   │
│   └── frontend/                   # Dashboard Next.js
│       ├── app/                    # App Router (Next.js 14+)
│       ├── components/             # Componentes React
│       ├── lib/                    # API client, hooks, utils
│       ├── public/
│       ├── Dockerfile
│       └── .env.example
│
├── infra/
│   ├── docker-compose.yml          # Desenvolvimento local
│   ├── docker-compose.prod.yml     # Produção
│   ├── nginx/                      # Configurações Nginx
│   └── cloudflare/                 # Configurações Cloudflare Tunnel
│
├── scripts/
│   ├── migrate.sh                  # Script de execução de migrations
│   ├── seed.sh                     # Seed de dados iniciais
│   └── backup.sh                   # Backup manual do banco
│
├── docs/
│   ├── adr/                        # Architecture Decision Records
│   ├── roadmap.md                  # Roadmap completo de desenvolvimento
│   └── runbooks/                   # Runbooks operacionais
│
├── .github/
│   └── workflows/                  # Pipelines CI/CD (GitHub Actions)
│
├── Makefile                        # Comandos utilitários
├── .editorconfig
├── .gitignore
└── README.md
```

---

## ✅ Pré-requisitos

Antes de começar, certifique-se de ter instalado em sua máquina:

- [Docker](https://docs.docker.com/get-docker/) `>= 24.x`
- [Docker Compose V2](https://docs.docker.com/compose/install/) `>= 2.x`
- [Git](https://git-scm.com/) `>= 2.x`
- [Make](https://www.gnu.org/software/make/) (opcional, mas recomendado)
- Python `>= 3.11` (apenas para desenvolvimento sem Docker)
- Node.js `>= 20.x` (apenas para desenvolvimento frontend sem Docker)

---

## ⚙️ Configuração do Ambiente Local

### 1. Clone o repositório

```bash
git clone https://github.com/WMSolutionsTI/nutria-pro.git
cd nutria-pro
```

### 2. Configure as variáveis de ambiente

Copie os arquivos de exemplo de cada serviço e preencha com seus valores locais:

```bash
# Backend API
cp services/api/.env.example services/api/.env

# Workers
cp services/workers/.env.example services/workers/.env

# Frontend
cp services/frontend/.env.example services/frontend/.env
```

> ⚠️ **Nunca commite arquivos `.env` com credenciais reais.** Os arquivos `.env` estão listados no `.gitignore`.

### 3. Suba o ambiente de desenvolvimento

```bash
# Usando Make (recomendado)
make dev

# Ou diretamente com Docker Compose
docker compose up -d
```

### 4. Execute as migrations do banco de dados

```bash
make migrate

# Ou diretamente
docker compose exec api alembic upgrade head
```

### 5. Popule os dados iniciais (planos, configurações)

```bash
make seed

# Ou diretamente
docker compose exec api python scripts/seed.py
```

### 6. Acesse os serviços

| Serviço | URL Local | Credenciais Padrão |
|---|---|---|
| **Dashboard (Frontend)** | http://localhost:3000 | — |
| **API (Swagger)** | http://localhost:8000/docs | — |
| **Chatwoot** | http://localhost:3001 | admin@example.com / changeme |
| **RabbitMQ Management** | http://localhost:15672 | guest / guest |
| **MinIO Console** | http://localhost:9001 | minioadmin / minioadmin |
| **n8n** | http://localhost:5678 | admin / changeme |
| **Grafana** | http://localhost:3002 | admin / admin |

---

## 🔧 Variáveis de Ambiente

### `services/api/.env`

```dotenv
# Aplicação
APP_ENV=local
APP_SECRET_KEY=sua-chave-secreta-aqui
DEBUG=true

# Banco de Dados
DATABASE_URL=postgresql+asyncpg://nutriapro_app:senha@postgres:5432/nutriapro

# Redis
REDIS_URL=redis://:senha@redis:6379/0

# RabbitMQ
RABBITMQ_URL=amqp://admin:senha@rabbitmq:5672/nutriapro

# MinIO
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=sua-access-key
MINIO_SECRET_KEY=sua-secret-key
MINIO_USE_SSL=false

# Chatwoot
CHATWOOT_BASE_URL=http://chatwoot-web:3000
CHATWOOT_API_TOKEN=seu-token-de-sistema
CHATWOOT_WEBHOOK_SECRET=seu-webhook-secret

# n8n
N8N_BASE_URL=http://n8n:5678
N8N_INTERNAL_API_KEY=sua-chave-interna

# JWT
JWT_PRIVATE_KEY_PATH=/app/keys/private.pem
JWT_PUBLIC_KEY_PATH=/app/keys/public.pem
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
JWT_REFRESH_TOKEN_EXPIRE_DAYS=30
```

> 📄 Consulte `services/api/.env.example` para a lista completa e documentada de todas as variáveis disponíveis.

---

## 🚀 Executando os Serviços

### Comandos Make disponíveis

```bash
make dev          # Sobe todos os serviços em modo desenvolvimento
make down         # Para todos os serviços
make logs         # Exibe logs de todos os containers em tempo real
make logs-api     # Exibe logs apenas da API
make logs-worker  # Exibe logs apenas dos workers
make build        # Reconstrói todas as imagens Docker
make test         # Executa a suíte completa de testes
make lint         # Executa todos os linters
make migrate      # Aplica as migrations pendentes
make seed         # Popula dados iniciais
make shell-api    # Abre um shell dentro do container da API
make shell-db     # Abre o psql no container do PostgreSQL
```

### Escalonando workers manualmente

```bash
# Escalar para 3 réplicas do worker de mensagens
docker compose up -d --scale worker-message=3

# Escalar para 5 réplicas
docker compose up -d --scale worker-message=5
```

> Os workers são completamente stateless. Adicionar ou remover réplicas não requer nenhuma alteração de configuração ou código.

---

## 🗃️ Migrations do Banco de Dados

O projeto utiliza **Alembic** para controle de versão do schema do banco de dados.

### Criar uma nova migration

```bash
# Gera automaticamente com base nas mudanças nos modelos
docker compose exec api alembic revision --autogenerate -m "descricao_da_mudanca"

# Cria migration vazia (para casos especiais)
docker compose exec api alembic revision -m "descricao_da_mudanca"
```

### Aplicar migrations

```bash
# Aplicar todas as migrations pendentes
docker compose exec api alembic upgrade head

# Aplicar N migrations
docker compose exec api alembic upgrade +1
```

### Reverter migrations

```bash
# Reverter a última migration
docker compose exec api alembic downgrade -1

# Reverter para uma revision específica
docker compose exec api alembic downgrade <revision_id>
```

### Boas práticas de migration

- ✅ Toda migration deve ser **backward compatible** (aditiva)
- ✅ Criação de índices deve usar `CREATE INDEX CONCURRENTLY`
- ✅ Nunca dropar colunas no mesmo deploy que remove referências no código
- ✅ Migrations são executadas **antes** do novo código ser deployado

---

## 🧪 Rodando os Testes

```bash
# Roda toda a suíte de testes
make test

# Apenas testes unitários
docker compose exec api pytest tests/unit/ -v

# Apenas testes de integração
docker compose exec api pytest tests/integration/ -v

# Com relatório de cobertura
docker compose exec api pytest --cov=app --cov-report=html

# Testes de um módulo específico
docker compose exec api pytest tests/unit/test_auth.py -v
```

> O CI bloqueia merges quando a cobertura de testes cai abaixo de **80%**.

---

## 🏢 Arquitetura Multi-Tenant

### Como o isolamento funciona

Cada nutricionista que se cadastra na plataforma é um **tenant** independente. O isolamento é garantido em múltiplas camadas:

**1. Camada de Dados**
Todos os modelos de dados possuem o campo `tenant_id`. A classe base do repositório injeta automaticamente `WHERE tenant_id = :current_tenant_id` em todas as queries, impossibilitando acesso cruzado de dados mesmo que o desenvolvedor esqueça de filtrar manualmente.

**2. Camada de API**
O JWT de cada usuário carrega o `tenant_id`. Um middleware extrai esse valor e o disponibiliza via `ContextVar` para toda a requisição. Endpoints protegidos verificam tanto autenticação quanto pertencimento ao tenant.

**3. Camada de Arquivos (MinIO)**
Todos os objetos são armazenados sob o prefixo `/{tenant_id}/`. URLs pré-assinadas são geradas somente após validar que o solicitante pertence ao tenant proprietário do arquivo.

**4. Testes de Isolamento Automatizados**
A suíte de integração inclui testes específicos que tentam acessar dados de um tenant B usando credenciais de um tenant A, e verificam que o sistema retorna `404` (não `403`, para não revelar a existência do recurso).

### O Inbox ID como identificador do tenant

```
Chatwoot Webhook → { inbox_id: 42, ... }
                           ↓
         SELECT tenant_id FROM tenants WHERE chatwoot_inbox_id = 42
                           ↓
                    tenant_id = "uuid-do-nutricionista"
                           ↓
                    Processamento isolado por tenant
```

Cada nutricionista possui exatamente um **Inbox** no Chatwoot. Esse `inbox_id` é armazenado no registro do tenant e funciona como chave de roteamento para todos os eventos de mensagem.

---

## 📨 Arquitetura de Mensageria

### Fluxo completo de uma mensagem

```
1. Cliente envia mensagem pelo WhatsApp
2. Chatwoot recebe a mensagem e dispara webhook
3. POST /webhooks/chatwoot (API FastAPI)
4. API verifica assinatura HMAC-SHA256
5. API resolve tenant pelo inbox_id
6. API publica evento no RabbitMQ (exchange: chatwoot.events)
7. API responde 200 OK para o Chatwoot (< 200ms)
8. Worker consome o evento da fila
9. Worker cria/atualiza registro do cliente no banco
10. Worker armazena a mensagem no banco
11. Worker avalia regras de automação do tenant
12. Worker aciona workflow n8n (se aplicável)
13. n8n executa automação e chama API interna
14. API interna publica mensagem de resposta na fila
15. Worker de envio chama API do Chatwoot para enviar resposta
16. Cliente recebe a resposta pelo WhatsApp
```

### Exchanges e Filas

| Exchange | Tipo | Fila | Finalidade |
|---|---|---|---|
| `chatwoot.events` | Topic | `message.processor` | Processar mensagens recebidas |
| `chatwoot.events` | Topic | `conversation.processor` | Processar eventos de conversa |
| `automation.triggers` | Topic | `automation.executor` | Executar automações |
| `notifications.outbound` | Direct | `notification.sender` | Enviar mensagens via Chatwoot |
| `scheduler.tasks` | Topic | `scheduler.executor` | Tarefas agendadas (lembretes, campanhas) |
| `billing.events` | Direct | `billing.processor` | Eventos de cobrança |
| `deadletter` | Direct | `deadletter.queue` | Mensagens que falharam no processamento |

---

## ⚙️ Workers e Filas

### Padrão de idempotência

Todo worker implementa verificação de idempotência antes de processar uma mensagem:

```
1. Extrair message_id do payload
2. Verificar Redis: worker:processed:{message_id}
3. Se existir: ACK imediato (já processado, ignorar)
4. Se não existir: processar mensagem
5. Ao concluir com sucesso: gravar Redis com TTL de 48h
6. ACK da mensagem no RabbitMQ
```

### Estratégia de retry

```
Tentativa 1 → falha transiente (ex: DB timeout)
     ↓ aguarda 2s
Tentativa 2 → falha transiente
     ↓ aguarda 4s
Tentativa 3 → falha transiente
     ↓ aguarda 8s
Tentativa 4 → NACK sem requeue → Dead Letter Queue
     ↓
  Alerta disparado → Time analisa no painel admin
```

### Dead Letter Queue (DLQ)

Mensagens que esgotam as tentativas de retry são enviadas para a DLQ. A plataforma oferece:
- Dashboard admin com listagem de mensagens na DLQ por tenant e fila
- Funcionalidade de **replay**: reprocessar manualmente uma mensagem específica
- Alertas automáticos quando o volume da DLQ ultrapassa o threshold configurado

---

## 🤖 Engine de Automação

O **n8n** é o motor de automação da plataforma. Os workers acionam workflows via webhook, e os workflows chamam de volta a API interna para executar ações.

### Workflows disponíveis (templates)

| Workflow | Gatilho | Ação |
|---|---|---|
| 🤝 **Boas-vindas** | Nova conversa de cliente novo | Envia mensagem de boas-vindas personalizada |
| 📅 **Confirmação de Consulta** | Consulta agendada | Envia confirmação com detalhes |
| ⏰ **Lembrete de Consulta** | 24h e 2h antes da consulta | Envia lembrete e solicita confirmação |
| 📋 **Follow-up Pós-Consulta** | Consulta marcada como concluída | Envia follow-up e plano alimentar |
| 💤 **Reativação de Clientes** | Cliente sem interação > N dias | Dispara mensagem de reativação |
| 💰 **Cobrança** | Manual ou agendado | Envia link de pagamento e faz follow-up |
| 🌙 **Fora do Horário** | Mensagem fora do horário configurado | Responde automaticamente informando o horário |

### Integrações internas (n8n → API)

O n8n se comunica com a API interna para executar ações:

```
POST /internal/messages/send         → Envia mensagem via Chatwoot
POST /internal/appointments/schedule → Agenda consulta
POST /internal/clients/{id}/tag      → Adiciona tag ao cliente
POST /internal/tasks/schedule        → Agenda tarefa futura
```

---

## 📈 Estratégia de Escalonamento

### Escalonamento horizontal de workers (zero mudanças de código)

```bash
# Situação atual: alta demanda → fila crescendo
docker compose up -d --scale worker-message=5 --scale worker-automation=3

# Após redução de demanda
docker compose up -d --scale worker-message=2 --scale worker-automation=1
```

Como workers são completamente **stateless**, o RabbitMQ distribui automaticamente as mensagens entre todas as réplicas disponíveis.

### Quando escalar

| Métrica | Threshold | Ação |
|---|---|---|
| Profundidade da fila `message.processor` | > 500 por 2 min | Adicionar réplicas do worker-message |
| Profundidade da fila `automation.executor` | > 300 por 2 min | Adicionar réplicas do worker-automation |
| CPU do VPS | > 80% por 5 min | Avaliar migração para multi-node |
| RAM do VPS | > 85% por 5 min | Avaliar migração para multi-node |

### Roadmap de escalonamento de infraestrutura

```
Estágio 1 (atual): VPS único Contabo
      ↓ (quando CPU/RAM saturar)
Estágio 2: Segundo VPS dedicado para workers
      ↓ (quando banco saturar)
Estágio 3: PostgreSQL em servidor dedicado ou managed service
      ↓ (quando RabbitMQ saturar)
Estágio 4: CloudAMQP ou RabbitMQ dedicado
      ↓ (escala enterprise)
Estágio 5: Docker Swarm / Kubernetes
```

---

## 🔍 Observabilidade

### Stack de monitoramento

| Ferramenta | Função | URL Local |
|---|---|---|
| **Prometheus** | Coleta de métricas | http://localhost:9090 |
| **Grafana** | Dashboards e visualização | http://localhost:3002 |
| **Loki** | Agregação de logs | — (via Grafana) |
| **Alertmanager** | Gerenciamento de alertas | http://localhost:9093 |

### Dashboards disponíveis no Grafana

- **Visão Geral do Sistema** — CPU, RAM, disco, rede do VPS
- **Performance da API** — taxa de requisições, latência (p50/p95/p99), taxa de erros
- **Saúde das Filas** — profundidade, consumers ativos, volume de DLQ
- **Performance dos Workers** — throughput, tempo de processamento, taxa de erros
- **Métricas de Negócio** — mensagens/hora, tenants ativos, automações executadas
- **Uso por Tenant** — volume de mensagens, limites atingidos

### Alertas configurados

| Condição | Severidade | Notificação |
|---|---|---|
| Taxa de erros da API > 5% por 2 min | 🔴 Crítico | Slack + E-mail |
| Profundidade de fila > 1.000 por 5 min | 🟡 Warning | Slack |
| Consumer count = 0 em qualquer fila | 🔴 Crítico | Slack + E-mail |
| Volume DLQ > 50 mensagens | 🟡 Warning | Slack |
| Uso de disco > 80% | 🟡 Warning | Slack |
| Latência p99 > 2s por 5 min | 🟡 Warning | Slack |

---

## 🔒 Segurança

### Práticas implementadas

- **Autenticação JWT com RS256** — chaves assimétricas, tokens de curta duração
- **Refresh token rotation** — cada uso do refresh token emite um novo e invalida o anterior
- **Argon2 para hashing de senhas** — algoritmo moderno e resistente a ataques de GPU
- **Rate limiting por tenant** — proteção contra abuso via Redis sliding window
- **Verificação de assinatura de webhooks** — HMAC-SHA256 com comparação em tempo constante
- **Isolamento de tenant em múltiplas camadas** — banco, API, arquivos, cache
- **Criptografia de secrets em banco** — tokens Chatwoot criptografados com AES-256-GCM
- **Proteção CORS** — apenas o domínio do frontend é permitido em produção
- **Headers de segurança** — HSTS, X-Frame-Options, CSP, X-Content-Type-Options
- **Lockout após tentativas falhas** — 5 tentativas → bloqueio de 10 minutos
- **Scan de vulnerabilidades em CI** — pip-audit, npm audit, trivy nas imagens Docker
- **Tunnel Cloudflare** — nenhuma porta exposta diretamente ao VPS (tudo via Cloudflare)

---

## 🗺️ Roadmap

Consulte o arquivo [`docs/roadmap.md`](docs/roadmap.md) para o roadmap completo e detalhado de desenvolvimento, incluindo todas as fases, milestones, tarefas e estratégias técnicas.

### Resumo das fases

| Fase | Descrição | Status |
|---|---|---|
| **Fase 0** | Inicialização do projeto e fundação | 🔲 Planejado |
| **Fase 1** | Infraestrutura e ambiente | 🔲 Planejado |
| **Fase 2** | Core da API backend | 🔲 Planejado |
| **Fase 3** | Arquitetura multi-tenant | 🔲 Planejado |
| **Fase 4** | Integração Chatwoot e pipeline de mensagens | 🔲 Planejado |
| **Fase 5** | Sistema de workers e filas | 🔲 Planejado |
| **Fase 6** | Engine de automação (n8n) | 🔲 Planejado |
| **Fase 7** | Funcionalidades de negócio | 🔲 Planejado |
| **Fase 8** | Frontend (Next.js) | 🔲 Planejado |
| **Fase 9** | Observabilidade e monitoramento | 🔲 Planejado |
| **Fase 10** | Hardening de segurança | 🔲 Planejado |
| **Fase 11** | DevOps e CI/CD | 🔲 Planejado |
| **Fase 12** | Preparação para o lançamento | 🔲 Planejado |
| **Fase 13** | Prontidão para escala | 🔲 Contínuo |

---

## 🤝 Contribuindo

### Fluxo de desenvolvimento

```bash
# 1. Crie uma branch a partir de develop
git checkout develop
git pull origin develop
git checkout -b feat/api/nome-da-feature

# 2. Desenvolva e commite usando Conventional Commits
git commit -m "feat(api): adiciona endpoint de agendamento de consultas"
git commit -m "fix(worker): corrige retry em falha de conexão com Chatwoot"
git commit -m "chore(infra): atualiza versão do PostgreSQL para 16"

# 3. Abra um Pull Request para develop
# 4. Aguarde review e aprovação
# 5. Merge após CI passar
```

### Conventional Commits

| Prefixo | Quando usar |
|---|---|
| `feat:` | Nova funcionalidade |
| `fix:` | Correção de bug |
| `chore:` | Atualização de dependências, configurações |
| `docs:` | Apenas documentação |
| `test:` | Adição ou correção de testes |
| `refactor:` | Refatoração sem mudança de comportamento |
| `perf:` | Melhoria de performance |
| `ci:` | Mudanças no pipeline de CI/CD |

### Checklist de Pull Request

Antes de abrir um PR, verifique:

- [ ] Testes unitários escritos e passando
- [ ] Cobertura de testes não reduziu abaixo de 80%
- [ ] Linter e type checker passando sem erros
- [ ] Migration backward compatible (se aplicável)
- [ ] Documentação atualizada (se aplicável)
- [ ] Nenhum secret ou credencial no código
- [ ] `tenant_id` presente em todos os novos modelos e queries

---

## 📄 Licença

Este projeto é **proprietário e privado**. Todos os direitos reservados a WMSolutions TI.

Nenhuma parte deste software pode ser reproduzida, distribuída ou transmitida de qualquer forma ou por qualquer meio, sem a permissão prévia por escrito dos proprietários.

---

<div align="center">

**Desenvolvido com ❤️ por [WMSolutions TI](https://github.com/WMSolutionsTI)**

*Construindo o futuro da nutrição digital.*

</div>
