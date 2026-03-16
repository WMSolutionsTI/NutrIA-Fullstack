# 12. Gestão de Ligações

> **Type:** n8n Flow
> **Trigger:** webhook (Retell AI call events)
> **Status:** active

## Short Description

Manages AI-powered voice calls via Retell AI integration: handles incoming call webhooks, routes calls to the AI voice secretary, and processes call completion events to update conversation history.

## Responsibilities

- Receive call initiation and completion webhooks from Retell AI
- Route inbound calls to the AI voice secretary configuration
- Extract call transcript and summary from Retell AI post-call
- Create or update Chatwoot conversation with call transcript
- Notify nutritionist of missed calls or completed consultations
- Log call metadata (duration, outcome) in NutrIA-Pro database

## Integration Points

- **Retell AI API** — call management, transcript retrieval
- **Chatwoot API** — conversation creation/update with call transcript
- **Evolution API (WhatsApp)** — missed call notifications
- **NutrIA-Pro Backend API** — call log persistence
- **Retell - Secretária v3 workflow** — voice AI configuration

## Implementation Decision

**Stay in n8n.** Retell AI webhook-based, real-time event handling, low-to-medium volume. Visual flow is valuable for managing the branching call event types (answered, missed, completed).
