# 13. Agente de Recuperação de Leads

> **Type:** Background Worker
> **Trigger:** cron / `scheduler.tasks` queue
> **Status:** active

## Short Description

Scheduled lead recovery agent that identifies inactive clients or unresponsive leads and sends targeted re-engagement messages to recover potential lost business.

## Responsibilities

- Periodically query database for clients inactive beyond a configured threshold
- Segment leads by inactivity period and last interaction type
- Generate personalized re-engagement messages (via LLM or templates)
- Send recovery messages via WhatsApp/Chatwoot
- Tag clients as `inactive` or `recovered` based on response
- Apply campaign limits to avoid spam (respect daily message quotas)
- Track recovery campaign effectiveness metrics

## Integration Points

- **RabbitMQ** — `scheduler.tasks` queue (trigger)
- **NutrIA-Pro Backend DB** — inactive client queries, tag updates
- **Chatwoot API** — re-engagement message delivery
- **Evolution API (WhatsApp)** — direct message channel
- **LLM** — optional personalized message generation

## Implementation Decision

**Convert to Worker.** Cron-based, DB-heavy bulk processing, requires campaign quotas and rate limiting, retry logic for delivery failures. The `SchedulerWorker` infrastructure handles the scheduling and the worker handles the bulk processing pattern efficiently.
