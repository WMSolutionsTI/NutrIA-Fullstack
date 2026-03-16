# Fase 04 — Mensageria e Integração Chatwoot

> Integração completa com Chatwoot como hub central de mensagens: webhook receiver, roteamento de conversas, gerenciamento de contatos, **flag de AI agent ativo/inativo por contato**, canal WhatsApp via Evolution API.

## Descrição

Esta fase implementa o pipeline completo de mensageria, tornando o Chatwoot o hub central de todas as comunicações com clientes. A feature central é a **flag `ai_agent_enabled` por contato**, que controla se o agente de IA está ativo ou se a conversa foi transferida para atendimento humano.

## Pipeline de Mensageria

```
WhatsApp → Evolution API → Chatwoot → Webhook → Backend
  → Verificar ai_agent_enabled
    → [true]  → RabbitMQ → Worker → n8n Secretária v3
    → [false] → Mantém em Chatwoot para atendimento humano
```

## Feature Central: Flag ai_agent_enabled

- Campo `ai_agent_enabled` (boolean, default: `true`) por contato/conversa
- Endpoint `PATCH /api/v1/conversations/{id}/ai-agent` para toggle
- Quando `false`: mensagens não são processadas pela IA, ficam no Chatwoot
- Quando reativado: mensagem padrão enviada ao cliente + log registrado

## Objetivos

- Implementar receptor de webhook Chatwoot com verificação HMAC-SHA256
- Implementar `ChatwootAPIClient` assíncrono com retry
- Criar modelos de CRM: `clients`, `conversations`, `messages`
- Implementar flag `ai_agent_enabled` por contato
- Implementar endpoint de toggle do agente de IA
- Pipeline completo: webhook → fila → worker → n8n

## Referência

Ver `projects/fase-04-mensageria-chatwoot.yaml` para issues detalhadas.
