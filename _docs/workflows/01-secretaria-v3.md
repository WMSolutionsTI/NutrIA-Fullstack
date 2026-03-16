# 01. Secretária v3

> **Type:** n8n Flow
> **Trigger:** webhook (inbound message from Chatwoot/WhatsApp)
> **Status:** active

## Short Description

The main AI secretary agent — receives inbound client messages, processes them through an LLM using the nutritionist's configured prompt/context, and sends the AI-generated response back via WhatsApp/Chatwoot. This is the core of the NutrIA-Pro autonomous client communication system.

## Responsibilities

- Receive inbound message webhooks from the backend message processor
- Verify `ai_agent_enabled` flag for the contact before processing
- Fetch the nutritionist's configured AI prompt/context from the database (per tenant)
- Send message + context to LLM (OpenAI/Anthropic) and generate response
- Split long responses and send sequentially via workflow 07
- Detect escalation triggers and route to workflow 05 (Escalar Humano)
- Call sub-workflows: 10 (contact lookup), 02 (file sending), 03/04 (scheduling)

## Integration Points

- **Chatwoot** — receives message events, sends responses
- **Evolution API (WhatsApp)** — message delivery channel
- **LLM (OpenAI/Anthropic)** — AI response generation
- **NutrIA-Pro Backend API** — tenant config, `ai_agent_enabled` flag
- **RabbitMQ** — receives triggers from `message.processor` queue
- Sub-workflows: 05, 07, 10, 02, 03, 04

## Implementation Decision

**Stay in n8n.** This workflow has complex visual branching logic, LLM integration, and calls multiple sub-workflows. The visual editor is essential for maintaining and extending the AI conversation flow. Multi-tenant adaptation needed: inject `tenant_id` via webhook header and fetch prompt dynamically per tenant.
