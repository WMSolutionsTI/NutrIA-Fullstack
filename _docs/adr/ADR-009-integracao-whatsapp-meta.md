# ADR-009 - Estratégia de Integração WhatsApp/Meta por Nutricionista

## Status
Proposto

## Contexto
O NutrIA-Pro usa Chatwoot como hub de comunicação. Cada nutricionista possui uma conta no ecossistema e pode ter múltiplas inboxes por plano. Para WhatsApp/Meta, há duas opções operacionais:

1. Conta Meta centralizada no admin.
2. Conta Meta própria por nutricionista.

## Decisão recomendada
Adotar **modelo híbrido com padrão por conta própria da nutricionista**:

- Padrão: inbox WhatsApp via ativos da própria nutricionista (WABA/Meta Business dela).
- Exceção controlada: canal centralizado do admin apenas para onboarding assistido, contingência e operação temporária.

## Racional
- Isolamento de tenant: reduz risco de mistura de dados e impacto cruzado.
- Compliance: facilita comprovação de titularidade dos dados/canal.
- Escalabilidade operacional: evita gargalo no time admin conforme crescimento.
- Portabilidade comercial: nutricionista mantém continuidade do canal em eventual churn.

## Trade-offs
- Conta própria por nutricionista:
- Prós: isolamento forte, autonomia, menor risco regulatório.
- Contras: onboarding inicial mais complexo.

- Conta centralizada admin:
- Prós: onboarding rápido no curto prazo.
- Contras: alto risco de acoplamento, limites compartilhados, suporte mais caro.

## Diretrizes técnicas
- Sempre armazenar no banco: `tenant_id`, `nutricionista_id`, `inbox_id`, `chatwoot_account_id`, tipo de integração e status.
- Toda solicitação de nova inbox deve abrir `admin_request` do tipo `nova_integracao_inbox`.
- Provisionamento:
- assinatura confirmada -> cria conta Chatwoot + credencial temporária + envio de instruções.
- inbox solicitada -> pendência admin até teste de integração.
- Ativação da secretária IA somente após status `active` da inbox.

## Plano de adoção
1. Fase 1: habilitar fluxo híbrido (conta própria + fallback centralizado).
2. Fase 2: tornar conta própria obrigatória para novos clientes.
3. Fase 3: migrar clientes legados centralizados para conta própria com playbook assistido.
