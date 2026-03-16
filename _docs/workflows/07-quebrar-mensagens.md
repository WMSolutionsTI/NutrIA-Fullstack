# 07. Quebrar e Enviar Mensagens

> **Type:** Background Worker
> **Trigger:** queue (`notification.sender`)
> **Status:** active

## Short Description

Splits long AI-generated messages into shorter segments and sends them sequentially via WhatsApp/Chatwoot with appropriate delays between each part, simulating natural human typing.

## Responsibilities

- Consume message sending requests from `notification.sender` queue
- Split message text at natural breakpoints (sentences, paragraphs)
- Apply configurable delay between message segments (simulates typing)
- Send each segment via Chatwoot/Evolution API in strict order
- Handle rate limiting (429) with backoff retry
- Guarantee sequential delivery even under load

## Integration Points

- **RabbitMQ** — `notification.sender` queue (source)
- **Chatwoot API** — message sending
- **Evolution API (WhatsApp)** — direct message delivery
- **NutrIA-Pro Backend** — rate limit config per tenant

## Implementation Decision

**Convert to Worker.** Queue-based processing, rate limiting management, sequential ordering requirements, and high volume make this a better fit for a dedicated RabbitMQ consumer worker than an n8n workflow. The `NotificationSenderConsumer` worker already handles this queue.
