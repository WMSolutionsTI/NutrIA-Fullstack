# 11. Agente de Lembretes de Agendamento

> **Type:** Background Worker
> **Trigger:** cron / `scheduler.executor` queue
> **Status:** active

## Short Description

Scheduled agent that queries upcoming appointments and sends automated reminder messages to clients at configured intervals (e.g., 24h and 2h before the appointment).

## Responsibilities

- Poll database for appointments with upcoming reminders due
- Send 24-hour reminder messages to clients via WhatsApp/Chatwoot
- Send 2-hour reminder messages with appointment details
- Handle delivery failures with retry logic
- Update reminder status in database to prevent duplicate sends
- Support per-tenant customizable reminder message templates

## Integration Points

- **RabbitMQ** — `scheduler.executor` queue (trigger)
- **NutrIA-Pro Backend DB** — appointment and reminder task queries
- **Chatwoot API** — reminder message delivery
- **Evolution API (WhatsApp)** — direct reminder messages
- **SchedulerWorker** — polls and publishes reminder tasks

## Implementation Decision

**Convert to Worker.** Cron-based, high volume as platform scales (potentially thousands of reminders/day), requires retry logic, DB-heavy (query + update per reminder). The existing `SchedulerWorker` and `SchedulerExecutorConsumer` infrastructure handles this pattern natively.
