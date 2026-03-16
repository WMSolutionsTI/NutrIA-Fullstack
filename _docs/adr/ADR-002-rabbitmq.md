# ADR-002: RabbitMQ como message broker

**Data:** 2026-03-09
**Status:** Aceito

---

## Contexto

O NutrIA-Pro precisa processar mensagens de forma assíncrona: envio de WhatsApp, escalação humana, campanhas em massa, notificações. Um message broker confiável é necessário para desacoplar produtores de consumidores e garantir entrega das mensagens.

## Decisão

Usar **RabbitMQ** como message broker principal.

## Alternativas Consideradas

| Alternativa | Por que descartada |
|---|---|
| Kafka | Over-engineering para o volume inicial; requer cluster ZooKeeper/KRaft; operação complexa |
| Redis Streams | Funcionalidades de broker limitadas; sem DLQ nativa robusta; Redis já usado para cache |
| AWS SQS | Vendor lock-in; custo em escala; requer AWS como infra |
| Celery + Redis | Abstração adicional desnecessária; RabbitMQ direto é mais transparente |

## Path para Kafka

Se o volume de mensagens ultrapassar **1 milhão/dia** ou surgir necessidade de **replay de eventos** (event sourcing), migrar para Kafka. RabbitMQ e Kafka têm semânticas diferentes (queue vs. log), então a migração requer refatoração dos consumidores.

## Consequências

### Positivas
- **Confiabilidade**: suporte a DLQ (Dead Letter Queue) nativo para mensagens com falha
- **Flexibilidade**: exchanges, routing keys e bindings permitem roteamento sofisticado
- **Operação simples**: single node suficiente para até ~100k mensagens/dia
- **Management UI**: interface web nativa para monitoramento de filas
- **Acks manuais**: controle fino sobre quando uma mensagem é considerada processada

### Negativas / Trade-offs
- Sem replay nativo (mensagens consumidas são removidas)
- Escalabilidade horizontal mais complexa que Kafka
- Single node é ponto único de falha (mitigado com quorum queues em cluster futuro)

## Referências

- https://www.rabbitmq.com/docs
- https://www.cloudamqp.com/blog/when-to-use-rabbitmq-or-apache-kafka.html
