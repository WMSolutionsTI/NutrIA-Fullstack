# 05. Escalar Humano

> **Type:** n8n Flow + Backend Worker
> **Trigger:** webhook (called by Secretária v3 when escalation is needed)
> **Status:** active

## Short Description

Handles human escalation: disables the AI agent for a specific contact, notifies the nutritionist via WhatsApp with a direct Chatwoot conversation link, and manages the handoff to and from human attendance.

## Responsibilities

- Receive escalation event with contact, conversation, and tenant details
- Call backend API to set `ai_agent_enabled = false` for the contact
- Send client message: *"Vou transferir você para [Nome] agora. Aguarde!"*
- Format and send WhatsApp notification to nutritionist with Chatwoot conversation link
- Publish event to nutritionist's panel notification system
- (On resume) Re-enable `ai_agent_enabled = true` and send resume message to client
- Log human intervention with start/end timestamps

## Integration Points

- **NutrIA-Pro Backend API** — `PATCH /api/v1/conversations/{id}/ai-agent` toggle endpoint
- **Evolution API (WhatsApp)** — notification to nutritionist
- **Chatwoot** — conversation link construction, client message
- **RabbitMQ** — `queue.human_escalation` event source
- **HumanEscalationWorker** — backend worker handles DB state

## Implementation Decision

**n8n orchestrates + dedicated Worker for DB state.** n8n handles the notification/message flow (visual, easy to customize per tenant). The `HumanEscalationWorker` handles atomic DB state updates and retry logic. This split ensures reliability of state changes while keeping the notification flow visual and maintainable.
