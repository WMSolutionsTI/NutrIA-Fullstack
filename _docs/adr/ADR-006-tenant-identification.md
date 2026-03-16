# ADR-006: Inbox ID do Chatwoot como identificador de tenant

**Data:** 2026-03-09
**Status:** Aceito

---

## Contexto

Em um sistema multi-tenant, cada mensagem recebida via webhook precisa ser roteada para o tenant correto. Precisamos de um identificador único, confiável e presente em todas as mensagens recebidas.

## Decisão

Usar o **Inbox ID do Chatwoot** como identificador primário de tenant no roteamento de webhooks.

## Raciocínio

Cada nutricionista/clínica possui uma **Inbox dedicada** no Chatwoot (um número de WhatsApp = uma Inbox). O webhook do Chatwoot sempre inclui o `inbox_id` no payload, tornando o roteamento trivial:

```python
tenant = await db.get_tenant_by_inbox_id(webhook.inbox_id)
```

## Alternativas Consideradas

| Alternativa | Por que descartada |
|---|---|
| Subdomínio (tenant.nutria-pro.com) | Não presente em webhooks de mensagens; requer DNS por tenant |
| Header HTTP customizado | Requer configuração adicional em cada integração |
| Número de telefone | Pode mudar; não é estável como identificador |
| UUID interno | Não está no webhook do Chatwoot nativo |

## Consequências

### Positivas
- Identificação zero-config: o `inbox_id` já está em todo webhook
- Mapeamento 1:1 limpo: Inbox → Tenant → Configurações
- Simples de implementar e debugar

### Negativas / Trade-offs
- Um tenant com múltiplos canais terá múltiplos inbox_ids (gerenciável com tabela de mapeamento)
- Dependência do modelo de dados do Chatwoot

## Referências

- https://www.chatwoot.com/docs/product/channels/api/
