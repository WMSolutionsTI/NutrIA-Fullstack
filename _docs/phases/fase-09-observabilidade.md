# Fase 09 — Observabilidade

> Stack de observabilidade: Prometheus, Grafana, Loki, alertas para falhas de workers/n8n, rastreamento de mensagens, dashboards de SLA de atendimento.

## Descrição

Esta fase implementa a stack completa de observabilidade para monitoramento em tempo real do NutrIA-Pro em produção, com foco especial em SLA de atendimento do agente de IA e saúde dos workers.

## Stack de Observabilidade

| Ferramenta | Função |
|-----------|--------|
| Prometheus | Coleta de métricas (workers, API, RabbitMQ) |
| Grafana | Dashboards e visualização |
| Loki | Agregação de logs |
| Alertmanager | Alertas via Slack/WhatsApp |
| OpenTelemetry | Rastreamento distribuído |

## Métricas Chave

- **SLA de Atendimento:** tempo entre mensagem recebida e resposta da IA
- **Taxa de Escalação:** % de conversas que requerem intervenção humana
- **Saúde dos Workers:** profundidade de fila, taxa de erro, throughput
- **Uptime do n8n:** execuções com sucesso/falha por workflow
- **Uso por Tenant:** mensagens, armazenamento, agendamentos

## Alertas Críticos

- Worker DLQ com profundidade > 100 mensagens
- Tempo de resposta da IA > 30 segundos
- n8n com workflow falhando repetidamente
- API com latência P99 > 2 segundos

## Referência

Ver `projects/fase-09-observabilidade.yaml` para issues detalhadas.
