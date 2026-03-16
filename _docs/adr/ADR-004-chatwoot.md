# ADR-004: Chatwoot como hub centralizado de comunicação

**Data:** 2026-03-09
**Status:** Aceito

---

## Contexto

O NutrIA-Pro precisa centralizar toda a comunicação com clientes (WhatsApp, e-mail, chat) em um único lugar, com suporte a atendimento humano quando necessário e API robusta para automação.

## Decisão

Usar **Chatwoot** (self-hosted) como hub de comunicação central.

## Alternativas Consideradas

| Alternativa | Por que descartada |
|---|---|
| Zendesk | Custo elevado por agente; sem self-hosted; vendor lock-in |
| Intercom | Idem Zendesk; sem integração nativa com WhatsApp via Evolution API |
| Twilio Flex | Custo muito alto; complexidade de configuração |
| Solução proprietária | Alto custo de desenvolvimento; fora do escopo inicial |

## Consequências

### Positivas
- **Self-hosted**: dados dos pacientes ficam sob controle do cliente (LGPD)
- **API REST completa**: integração nativa com workers e n8n
- **Multi-canal**: WhatsApp, e-mail, chat web em uma interface
- **Gratuito**: código aberto (MIT), sem custo por agente
- **Inbox ID**: identificador único por tenant para roteamento multi-tenant

### Negativas / Trade-offs
- Responsabilidade pela manutenção e updates da instância
- Consumo de recursos no VPS (~512MB RAM)
- Customizações profundas requerem fork do código

## Referências

- https://www.chatwoot.com/docs/
- https://github.com/chatwoot/chatwoot
