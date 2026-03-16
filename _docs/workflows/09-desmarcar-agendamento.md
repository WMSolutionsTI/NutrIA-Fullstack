# 09. Desmarcar Agendamento e Enviar Alerta

> **Type:** n8n Flow
> **Trigger:** webhook (client requests cancellation or nutritionist cancels)
> **Status:** active

## Short Description

Cancels an existing appointment in Google Calendar and the NutrIA-Pro database, then sends cancellation alerts to both the client and the nutritionist.

## Responsibilities

- Receive cancellation request with appointment and tenant details
- Delete the event from Google Calendar using tenant OAuth credentials
- Update appointment status to `cancelled` in NutrIA-Pro database
- Send cancellation confirmation to the client via WhatsApp/Chatwoot
- Send cancellation alert to the nutritionist via WhatsApp
- Optionally offer rescheduling by triggering workflow 04.1

## Integration Points

- **Google Calendar API** — event deletion with per-tenant OAuth
- **Chatwoot API** — client cancellation notification
- **Evolution API (WhatsApp)** — nutritionist alert
- **NutrIA-Pro Backend API** — update appointment record
- **Secretária v3 (01)** — may trigger for rescheduling offer

## Implementation Decision

**Stay in n8n.** Event-driven, external API, low volume. Multi-step notification logic is well-suited to visual flow.
