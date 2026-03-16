# 06. Integração Asaas

> **Type:** n8n Flow
> **Trigger:** webhook (inbound payment events from Asaas)
> **Status:** active

## Short Description

Handles all payment-related events from the Asaas payment platform: payment confirmations, overdue notices, charge creation, and payment link generation for clients of nutritionists.

## Responsibilities

- Receive payment webhooks from Asaas (payment confirmed, overdue, cancelled)
- Route events by type to appropriate processing branches
- Update appointment or subscription status on payment confirmation
- Send payment receipt or overdue notification to client via WhatsApp/Chatwoot
- Generate and send payment links to clients when requested
- Sync payment data with NutrIA-Pro backend

## Integration Points

- **Asaas API** — payment processing, charge creation, payment links
- **NutrIA-Pro Backend API** — update appointment/subscription status
- **Chatwoot API** — send payment notifications to clients
- **Evolution API (WhatsApp)** — payment-related messages

## Implementation Decision

**Stay in n8n.** Webhook-based external payment integration, event-driven, moderate volume. Asaas credentials are per tenant (each nutritionist has their own account). n8n handles the per-tenant credential routing natively.
