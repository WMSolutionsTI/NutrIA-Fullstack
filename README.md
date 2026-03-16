<div align="center">

# 🥗 NutrIA-Pro Platform

### Plataforma SaaS para nutricionistas — automação, gestão, atendimento e fidelização em um só lugar.

---

## 📋 Índice

- [Sobre o Projeto](#sobre-o-projeto)
- [Funcionalidades Principais](#funcionalidades-principais)
- [Arquitetura Geral](#arquitetura-geral)
- [Stack Tecnológico](#stack-tecnológico)
- [Estrutura do Repositório](#estrutura-do-repositório)
- [Roadmap](#roadmap)
- [Configuração e Uso](#configuração-e-uso)
- [Segurança e Escalabilidade](#segurança-e-escalabilidade)
- [Contribuindo](#contribuindo)
- [Licença](#licença)

---

## 🎯 Sobre o Projeto

O **NutrIA-Pro** é uma plataforma SaaS multi-tenant para nutricionistas e clínicas, centralizando comunicação, automação de atendimento, agendamento, cobranças, envio de planos alimentares, acompanhamento pós-consulta e gestão de clientes. O sistema foi redesenhado para suportar milhares de profissionais simultaneamente, com foco em automação inteligente via workers Python, escalabilidade, segurança e experiência profissional.

### Problema Resolvido

Nutricionistas enfrentam desafios ao gerenciar manualmente:
- Mensagens em múltiplos canais (WhatsApp, Instagram, e-mail)
- Agendamento e confirmação de consultas
- Envio de planos alimentares e materiais
- Follow-ups pós-consulta
- Cobranças e lembretes

O NutrIA-Pro automatiza todo esse fluxo, permitindo foco total no cuidado ao cliente.

### Visão Geral do Fluxo

```
Cliente → WhatsApp/Telegram/Instagram/E-mail
              ↓
          [Chatwoot] (hub de comunicação)
              ↓ webhook
          [API FastAPI] (recebe e publica na fila)
              ↓
          [RabbitMQ] (fila de mensagens)
              ↓
          [Workers Python] (processam assincronamente)
              ↓
     ┌────────────────────────────┐
     │  Banco de Dados (PostgreSQL)│
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
| 📨 Central de Mensagens | Todas as conversas em um só lugar |
| 📅 Agendamento | Calendário integrado, confirmações automáticas |
| 🤖 Automações Inteligentes | Fluxos automáticos de boas-vindas, lembretes, follow-ups |
| 👥 CRM de Clientes | Histórico completo, anotações clínicas, arquivos |
| 📁 Gestão de Arquivos | Envio de planos alimentares, PDFs, materiais |
| 📣 Campanhas | Mensagens segmentadas para grupos |
| 💳 Cobranças | Links de pagamento (PIX, cartão), status |
| 📊 Relatórios | Métricas de atendimento, engajamento, financeiro |

### Para a Plataforma (admin)

| Funcionalidade | Descrição |
|---|---|
| 🏢 Gestão de Tenants | Ativação, suspensão, alteração de planos |
| 📦 Planos e Limites | Configuração de assinaturas, limites |
| 🔍 Monitoramento | Dashboards de métricas, saúde das filas |
| ⚡ DLQ Monitor | Reprocessamento de mensagens falhadas |

---

## 🏛️ Arquitetura Geral

1. **Hub de Comunicação Centralizado (Chatwoot):** Todos os canais conectados ao Chatwoot, cada nutricionista com sua Inbox (identificador de tenant).
2. **Processamento Assíncrono por Filas (RabbitMQ):** Webhooks publicados em filas, workers independentes processam eventos, garantindo respostas instantâneas e escalabilidade.
3. **Automação via Workers Python:** Workers executam automações, interagem com API interna, Chatwoot, banco de dados, arquivos e integrações externas.
4. **Multi-Tenancy por Isolamento de Dados:** Cada tenant isolado por `tenant_id` em todas as tabelas, enforcement na aplicação e testes automatizados.

---

## 🛠️ Stack Tecnológico

| Componente | Tecnologia | Função |
|---|---|---|
| Backend API | FastAPI (Python) | API REST, webhooks, lógica de negócio |
| Workers | Python | Automação, processamento de filas |
| Banco de Dados | PostgreSQL | Armazenamento principal |
| Fila de Mensagens | RabbitMQ | Broker, DLQ, roteamento |
| Cache | Redis | Sessões, rate limiting, locks |
| Arquivos | MinIO | Objetos S3 |
| Hub de Comunicação | Chatwoot | Centralização de canais |
| Frontend | Next.js 14+ | Dashboard e painel admin |
| Containerização | Docker | Orquestração |
| Proxy/Túnel | Cloudflared | TLS, DDoS protection |
| Hospedagem | VPS Contabo | Produção |
| Migrations | Alembic | Versionamento do schema |

---

## 📁 Estrutura do Repositório

```
backend_python/        # FastAPI, workers, migrations
frontend/              # Next.js dashboard
_infra/                # Docker, nginx, cloudflared
_docs/                 # Documentação, ADRs, roadmap
_projects/             # YAMLs de fases, scripts
_scripts/              # Scripts de deploy, setup
Makefile, README.md, etc.
```

---

## 🗺️ Roadmap

1. Inicialização e estruturação do projeto
2. Infraestrutura e ambiente
3. Backend core (API, workers)
4. Multi-tenancy e isolamento
5. Mensageria e integração Chatwoot
6. Automação via workers Python
7. Funcionalidades de negócio (anamnese, plano alimentar, acompanhamento IA)
8. Frontend Next.js
9. Observabilidade e monitoramento
10. Segurança
11. DevOps e CI/CD
12. Lançamento
13. Escalabilidade
14. IA nutricional avançada

---

## ⚙️ Configuração e Uso

1. Clone o repositório
2. Configure variáveis de ambiente (ver `_docs/environment-variables.md`)
3. Use Docker Compose ou Swarm para subir todos os serviços
4. Acesse o painel pelo endereço local
5. Para desenvolvimento, use scripts em `_scripts/` e Makefile

---

## 🔒 Segurança e Escalabilidade

- Isolamento total de tenants por `tenant_id` (ver ADR-007)
- Middleware de validação, testes de isolamento, code review obrigatório
- Webhooks verificados, rate limiting, autenticação JWT
- Escalabilidade horizontal: workers e filas independentes
- Observabilidade: logs, métricas, health checks
- Backup e restore manual por tenant

---

## 🤝 Contribuindo

Veja o guia em `CONTRIBUTING.md`. PRs devem seguir checklist de isolamento, testes, documentação e boas práticas.

---

## 📄 Licença

Projeto privado, uso restrito.

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


### 1. Hub de Comunicação Centralizado (Chatwoot)
Todos os canais de comunicação (WhatsApp, Telegram, Instagram, Facebook, e-mail, formulários web) são conectados ao Chatwoot. Cada nutricionista possui sua própria **Inbox** dentro do Chatwoot, que funciona como o **identificador do tenant** no sistema.
### 4. Multi-Tenancy por Isolamento de Dados

---

## 🛠️ Stack Tecnológico

| Componente | Tecnologia | Função |
|---|---|---|
| **Backend API** | FastAPI (Python) | API REST principal, recepção de webhooks, lógica de negócio |
| **Hub de Comunicação** | Chatwoot | Centralização de canais de atendimento |
| **Engine de Automação** | Workers Python | Automação de negócio, fluxos, follow-ups, reativação |
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
│
├── docs/
│   ├── adr/                        # Architecture Decision Records
│   ├── roadmap.md                  # Roadmap completo de desenvolvimento
│   └── runbooks/                   # Runbooks operacionais
│
├── .github/
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


## ⚙️ Configuração e Uso com Docker Swarm

### Requisitos
- Docker Engine >= 24.x
- Docker Swarm ativado (`docker swarm init`)
- Permissões para criar volumes e redes

### Passos
1. Clone o repositório
    ```bash
    git clone https://github.com/WMSolutionsTI/nutria-pro.git
    cd nutria-pro
    ```
2. Configure variáveis de ambiente (ver `_docs/environment-variables.md`)
3. Inicie o Swarm:
    ```bash
    docker swarm init
    ```
4. Faça o deploy da stack:
    ```bash
    docker stack deploy -c _infra/docker-compose.yml nutria-pro
    ```
5. Acompanhe os serviços:
    ```bash
    docker stack services nutria-pro
    docker stack ps nutria-pro
    ```
6. Para atualizar, use:
    ```bash
    docker stack deploy -c _infra/docker-compose.yml nutria-pro
    ```
7. Para remover:
    ```bash
    docker stack rm nutria-pro
    ```

### Vantagens do Swarm
- Replicação automática, alta disponibilidade
- Deploy rolling, atualização sem downtime
- Orquestração nativa de serviços distribuídos

---

## Observação
Para desenvolvimento local, Compose ainda pode ser usado. Para produção, Swarm é recomendado.

---

## 🔧 Variáveis de Ambiente


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
CHATWOOT_WEBHOOK_SECRET=seu-webhook-secret

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



O projeto utiliza **Alembic** para controle de versão do schema do banco de dados.

### Criar uma nova migration

```bash
# Gera automaticamente com base nas mudanças nos modelos

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
12. Worker avalia regras de automação do tenant e executa workflow Python
13. Worker executa automação e chama API interna
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

Workers Python são o motor de automação da plataforma. Cada worker consome filas específicas, processa eventos e executa ações diretamente, sem dependência de n8n.

### Workflows disponíveis (templates)

| Workflow | Gatilho | Ação |
|---|---|---|
| 🤝 **Boas-vindas** | Nova conversa de cliente novo | Worker BoasVindasWorker envia mensagem personalizada |
| 📅 **Confirmação de Consulta** | Consulta agendada | Worker ConsultaWorker envia confirmação com detalhes |
| ⏰ **Lembrete de Consulta** | 24h e 2h antes da consulta | Worker LembreteWorker envia lembrete e solicita confirmação |
| 📋 **Follow-up Pós-Consulta** | Consulta marcada como concluída | Worker FollowUpWorker envia follow-up e plano alimentar |
| 💤 **Reativação de Clientes** | Cliente sem interação > N dias | Worker LeadRecoveryWorker dispara mensagem de reativação |
| 💰 **Cobrança** | Manual ou agendado | Worker CobrançaWorker envia link de pagamento e faz follow-up |
| 🌙 **Fora do Horário** | Mensagem fora do horário configurado | Worker ForaHorarioWorker responde automaticamente informando o horário |

### Integrações internas (Workers → API)

Workers Python se comunicam diretamente com a API interna para executar ações:

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
| **Fase 6** | Engine de automação (workers Python) | 🔲 Planejado |
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
