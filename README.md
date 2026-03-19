<div align="center">

# 🥗 NutrIA-Fullstack

### Plataforma SaaS para nutricionistas: automação, atendimento, agendamento e fidelização integrados.

---

[![Status](https://img.shields.io/badge/status-em%20desenvolvimento-yellow?style=flat-square)]()
[![Backend](https://img.shields.io/badge/backend-FastAPI-009688?style=flat-square&logo=fastapi)]()
[![Frontend](https://img.shields.io/badge/frontend-Next.js-000000?style=flat-square&logo=next.js)]()
[![Mensageria](https://img.shields.io/badge/fila-RabbitMQ-FF6600?style=flat-square&logo=rabbitmq)]()
[![Banco](https://img.shields.io/badge/banco-PostgreSQL-336791?style=flat-square&logo=postgresql)]()
[![Docker](https://img.shields.io/badge/containers-Docker-2496ED?style=flat-square&logo=docker)]()
[![Licença](https://img.shields.io/badge/licença-Privado-red?style=flat-square)]()

</div>

---

## 📌 Visão Geral

**NutrIA-Fullstack** é uma plataforma SaaS multi-tenant para nutricionistas e clínicas que unifica atendimento (WhatsApp/Instagram/Telegram/e-mail), automação de fluxos, agendamento de consultas, cobrança e gestão de clientes. O objetivo é liberar tempo dos profissionais para se concentrarem no cuidado clínico, enquanto o sistema cuida da orquestração operacional.

### Objetivos principais

- Centralizar a comunicação em um único hub (Chatwoot)
- Processar eventos de forma assíncrona e resiliente via filas (RabbitMQ)
- Oferecer automações configuráveis (workers Python)
- Garantir isolamento de dados entre tenants (multi-tenant)
- Permitir escalabilidade horizontal com pouca fricção
- Fornecer experiências modernas via dashboard Next.js

---

## ⚙️ Funcionalidades Principais

### Para o nutricionista (tenant)

- 📨 **Central de mensagens** (WhatsApp, Telegram, Instagram, e-mail)
- 📅 **Agendamento e confirmação automática de consultas**
- 🤖 **Automações inteligentes** (boas-vindas, lembretes, follow-ups, reativação)
- 👥 **CRM de clientes** (histórico completo, anotações, tags)
- 📁 **Gestão de arquivos** (planos alimentares, PDFs, materiais)
- 📣 **Campanhas segmentadas**
- 💳 **Cobranças e links de pagamento**
- 📊 **Relatórios e métricas de uso**

### Para a plataforma (admin)

- 🏢 **Gestão de tenants** (ativar, suspender, alterar planos)
- 📦 **Configuração de planos e limites**
- 🔍 **Monitoramento e observabilidade**
- ⚡ **Monitor de DLQ (fila de mensagens falhadas)**

---

## 🏛️ Arquitetura (Resumo)

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
     │  PostgreSQL (dados)         │
     │  Redis (cache / idempotência)│
     │  MinIO (arquivos)           │
     │  n8n (automações opcionais) │
     └────────────────────────────┘
              ↓
     [Dashboard Next.js] ← Nutricionista visualiza tudo
```

### Componentes principais

- **Chatwoot**: centraliza canais e notifica via webhooks
- **API FastAPI**: roteia eventos, autentica tenants, publica filas
- **RabbitMQ**: broker de eventos, DLQ e roteamento por tenant
- **Workers Python**: processam mensagens, executam automações e comunicam com Chatwoot
- **Next.js**: painel do nutricionista e painel administrativo
- **PostgreSQL**: armazenamento relacional multi-tenant
- **Redis**: cache, rate limiting, idempotência
- **MinIO**: armazenamento de arquivos (S3 compatível)

---

## 📁 Estrutura do Repositório

```
NutrIA-Fullstack/
├── backend_python/       # FastAPI + workers + migrations + integrações
├── frontend/             # Next.js dashboard
├── _infra/               # Docker Compose, nginx, cloudflared
├── _docs/                # Documentação, ADRs, workflow, roadmap
├── _projects/            # Planejamento em YAML, scripts
├── _scripts/             # Scripts utilitários (deploy, setup, manutenção)
├── Makefile              # Atalhos de desenvolvimento
├── CONTRIBUTING.md       # Guia de contribuição
└── README.md             # Este documento
```

---

## 🛠️ Pré-requisitos

- [Docker](https://docs.docker.com/get-docker/) (>= 24.x)
- [Docker Compose V2](https://docs.docker.com/compose/install/) (>= 2.x)
- [Git](https://git-scm.com/) (>= 2.x)
- [Make](https://www.gnu.org/software/make/) (opcional)

Opcional (desenvolvimento sem Docker):
- Python `>= 3.11`
- Node.js `>= 20.x`

---

## 🚀 Iniciando (Desenvolvimento)

### 1) Clone o repositório

```bash
git clone https://github.com/WMSolutionsTI/NutrIA-Fullstack.git
cd NutrIA-Fullstack
```

### 2) Configure variáveis de ambiente

As variáveis necessárias estão documentadas em `_docs/environment-variables.md`.
A maioria dos serviços possui um `.env.example` dentro de sua pasta.

### 3) Subir os serviços (Docker Compose)

```bash
make dev
```

### 4) Parar os serviços

```bash
make down
```

### 5) Logs e debugging

```bash
make logs        # logs de todos os serviços
make logs-api    # logs apenas da API
make logs-worker # logs apenas dos workers
```

> 💡 Para escalar workers localmente:
> `docker compose up -d --scale worker-message=3 --scale worker-automation=2`

---

## 🔧 Variáveis de Ambiente

Os detalhes completos estão em `_docs/environment-variables.md`. Abaixo há um exemplo simplificado para referência:

```dotenv
APP_ENV=local
APP_SECRET_KEY=changeme

DATABASE_URL=postgresql+asyncpg://nutriapro:secret@postgres:5432/nutriapro
REDIS_URL=redis://:secret@redis:6379/0
RABBITMQ_URL=amqp://admin:secret@rabbitmq:5672/nutriapro

MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=minio
MINIO_SECRET_KEY=minio123

CHATWOOT_BASE_URL=http://chatwoot:3000
CHATWOOT_WEBHOOK_SECRET=changeme
```

---

## 🧪 Testes

```bash
make test
```

Os testes estão localizados em `backend_python/tests/`.

---

## 🧠 Multi-Tenancy (Isolamento de Dados)

O sistema é multi-tenant por design. Cada tenant (nutricionista) tem dados completamente isolados.

- **Banco de dados:** todas as tabelas possuem `tenant_id` e o repositório injeta o filtro automaticamente.
- **API:** o JWT contém o `tenant_id` que é extraído por middleware e usado para resolver permissões.
- **Arquivos:** objetos no MinIO são armazenados com prefixo `/{tenant_id}/`, e URLs pré-assinadas só são geradas após validação.
- **Testes:** existe cobertura dedicada que tenta acessar dados de um tenant usando credenciais de outro e garante que o retorno seja `404`.

---

## 🔁 Mensageria e Workers

### Como funciona uma mensagem
1. Cliente envia mensagem (WhatsApp/Instagram/Telegram)
2. Chatwoot dispara webhook para o backend
3. Backend valida assinatura e resolve o tenant
4. Backend publica evento no RabbitMQ
5. Worker consome o evento e executa a lógica (salva no banco, dispara automação, envia resposta)

### Estratégias de robustez

- **Idempotência:** cada evento é registrado em Redis para evitar processamento duplicado
- **Retries exponenciais:** falhas transitórias são reprocessadas com backoff
- **DLQ:** mensagens que excedem retries vão para a fila de dead letter (DLQ) e podem ser reprocessadas manualmente

---

## 📌 Documentação Complementar

- `_docs/adr/` — Architecture Decision Records
- `_docs/workflows/` — Descrições de fluxos e processos
- `_docs/roadmap.md` — Roadmap completo por fases

---

## 🤝 Contribuindo

Leia `CONTRIBUTING.md` para o fluxo de contribuição, padrões de commit (Conventional Commits) e checklist de PRs.

---

## 📄 Licença

Este projeto é **privado** e de uso restrito. Todos os direitos reservados a WMSolutions TI.

