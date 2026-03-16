# Retell - Secretária v3

> **Type:** n8n Flow
> **Trigger:** webhook (Retell AI voice call events)
> **Status:** active

## Short Description

AI voice secretary integration via Retell AI — handles real-time voice call routing, provides the AI with the nutritionist's context/prompt during calls, and manages the voice conversation flow.

## Responsibilities

- Configure and expose the Retell AI agent with per-tenant nutritionist prompt
- Handle real-time call events from Retell AI (call started, utterance, call ended)
- Inject nutritionist context into the voice AI agent dynamically
- Manage call state and conversation context during the call
- Post-call: generate transcript, create Chatwoot conversation record
- Handle escalation: if voice AI cannot resolve, transfer to nutritionist

## Integration Points

- **Retell AI** — voice call management, real-time LLM integration
- **NutrIA-Pro Backend API** — tenant AI prompt/config retrieval
- **Chatwoot API** — post-call conversation creation
- **Gestão de Ligações (12)** — companion workflow for call management
- **Evolution API (WhatsApp)** — post-call summary messages

## Implementation Decision

**Stay in n8n.** Real-time Retell AI webhook integration, voice AI configuration per tenant, low volume per call. Event-driven, external API — ideal for n8n. The visual flow is important for managing the complex real-time call state machine.
