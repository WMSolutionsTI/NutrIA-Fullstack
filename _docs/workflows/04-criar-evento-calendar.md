# 04. Criar Evento Google Calendar

> **Type:** n8n Flow
> **Trigger:** webhook (called by Secretária v3 after client confirms appointment)
> **Status:** active

## Short Description

Creates a new appointment event in the nutritionist's Google Calendar and registers the appointment in the NutrIA-Pro database, completing the scheduling flow initiated by the AI secretary.

## Responsibilities

- Receive appointment details (client, date/time, type) via webhook
- Authenticate with Google Calendar using tenant's OAuth credentials
- Create the calendar event with client details and meeting link
- Call NutrIA-Pro backend to persist the appointment record
- Send confirmation message back to client via Chatwoot
- Trigger appointment reminder scheduling (24h and 2h reminders)

## Integration Points

- **Google Calendar API** — event creation with per-tenant OAuth
- **Chatwoot API** — confirmation message to client
- **NutrIA-Pro Backend API** — persist appointment, schedule reminders
- **Secretária v3 (01)** — called as sub-workflow

## Implementation Decision

**Stay in n8n.** Event-driven, external API, low-to-medium volume. Visual flow needed for confirmation branching logic.
