# Workflow Decision Matrix — n8n vs. Background Worker

This document defines which n8n workflows remain as n8n flows and which should be converted to dedicated backend workers.

## Decision Matrix

| Workflow | File | Decision | Reason |
|----------|------|----------|--------|
| 00. Configurações | `00. Configurações.json` | **n8n** | Global config/env vars, referenced by all workflows |
| 01. Secretária v3 | `01. Secretária v3.json` | **n8n** | Event-driven, visual LLM flow, complex multi-step branching |
| 02. Google Drive | `02. Baixar e enviar arquivo do Google Drive.json` | **n8n** | External API, webhook-triggered, low volume |
| 03. Google Calendar Slots | `03. Buscar janelas disponíveis Google Calendar.json` | **n8n** | External API, per-tenant OAuth, sub-workflow |
| 04. Criar Evento Calendar | `04. Criar evento Google Calendar.json` | **n8n** | External API, event-driven, low volume |
| 04.1 Atualizar Agendamento | `4.1 [EXTRA] Atualizar agendamento.json` | **n8n** | External API, event-driven, low volume |
| 05. Escalar Humano | `05. Escalar humano.json` | **n8n + Worker** | n8n orchestrates; dedicated Worker manages DB state and retry |
| 06. Integração Asaas | `06. Integração Asaas.json` | **n8n** | Webhook-based payment integration, external callbacks |
| 07. Quebrar Mensagens | `07. Quebrar e enviar mensagens.json` | **Worker** | Queue-based, rate limiting, sequential delivery required |
| 08. Agente Assistente Interno | `08. Agente Assistente Interno.json` | **n8n** | LLM calls, admin panel queries, low volume |
| 09. Desmarcar Agendamento | `09. Desmarcar agendamento e enviar alerta.json` | **n8n** | External calendar API + notification, event-driven |
| 10. Buscar/Criar Contato | `10. Buscar ou criar contato + conversa.json` | **n8n** | Chatwoot API calls, used as sub-workflow by others |
| 11. Lembretes Agendamento | `11. Agente de Lembretes de Agendamento.json` | **Worker** | Cron-based, DB-heavy, high volume, retry logic needed |
| 12. Gestão de Ligações | `12. Gestão de ligações.json` | **n8n** | Retell AI webhooks, real-time events, low volume |
| 13. Recuperação de Leads | `13. Agente de Recuperação de Leads.json` | **Worker** | Cron-based, bulk DB processing, retry, high volume |
| Retell - Secretária v3 | `Retell - Secretária v3.json` | **n8n** | Voice AI webhooks, Retell integration, event-driven |

## Decision Criteria

### Stay in n8n
- Triggered by **webhooks** or **external events** (Chatwoot, Asaas, Retell, Google)
- Requires **visual flow** for complex LLM/AI branching logic
- **Low-to-medium volume** (< 1,000 executions/hour)
- Integrates with **external APIs** requiring OAuth per tenant
- Needs easy modification by non-developers (visual editor)
- Sub-workflows called by other n8n workflows

### Convert to Dedicated Worker
- **Cron/schedule-based** execution at high volume
- Requires sophisticated **retry logic** and dead-letter handling
- **Heavy database operations** — bulk reads/writes/updates
- **Rate limiting** and queue backpressure management
- **Stateful operations** requiring atomic DB + queue transactions
- Volume > 1,000 executions/hour

## Worker Queue Mapping

| Workflow → Worker | Queue |
|-------------------|-------|
| 05. Escalar Humano → HumanEscalationWorker | `queue.human_escalation` |
| 07. Quebrar Mensagens → MessageSplitterWorker | `notification.sender` |
| 11. Lembretes → AppointmentReminderWorker | `scheduler.executor` |
| 13. Recuperação de Leads → LeadRecoveryWorker | `scheduler.tasks` |
