# 03. Buscar Janelas Disponíveis Google Calendar

> **Type:** n8n Flow
> **Trigger:** webhook (called by Secretária v3 during scheduling conversation)
> **Status:** active

## Short Description

Queries the nutritionist's Google Calendar to find available appointment slots within a given date range, returning available times to the AI secretary for client scheduling.

## Responsibilities

- Receive date range and tenant credentials via webhook payload
- Authenticate with Google Calendar using tenant's OAuth credentials
- Fetch busy slots from the nutritionist's calendar (freebusy query)
- Calculate and return available time windows based on nutritionist's working hours
- Format results for consumption by the Secretária v3 workflow

## Integration Points

- **Google Calendar API** — freebusy query with per-tenant OAuth
- **NutrIA-Pro Backend** — tenant working hours configuration
- **Secretária v3 (01)** — called as sub-workflow

## Implementation Decision

**Stay in n8n.** External API call per tenant, event-driven sub-workflow, low volume. OAuth per tenant is handled natively in n8n.
