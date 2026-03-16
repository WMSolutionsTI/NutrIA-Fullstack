# Fase 03 — Multi-tenancy

> Implementação da arquitetura multi-tenant: isolamento por schema PostgreSQL, middleware de tenant resolution, planos de assinatura, limites por tier.

## Descrição

Esta fase implementa o isolamento completo de dados entre tenants (nutricionistas) usando schemas PostgreSQL, e estabelece o sistema de planos de assinatura com limites por tier.

## Estratégia de Isolamento

- **Schema-per-tenant** no PostgreSQL: cada nutricionista tem um schema isolado (`tenant_{id}`)
- **Tenant resolution** via JWT claim (`tenant_id`) e/ou subdomínio
- **Middleware** injeta `tenant_id` em cada requisição autenticada
- Nenhuma query escapa do contexto do tenant

## Planos de Assinatura

| Tier | Clientes | Mensagens/mês | Armazenamento |
|------|---------|--------------|---------------|
| Starter | 50 | 1.000 | 1 GB |
| Professional | 200 | 5.000 | 10 GB |
| Enterprise | Ilimitado | Ilimitado | 100 GB |

## Objetivos

- Implementar criação automática de schema ao registrar tenant
- Criar middleware `TenantMiddleware` que extrai e valida `tenant_id`
- Implementar `UsageTrackingService` para monitorar limites por plano
- Criar modelo de dados para planos, assinaturas e uso
- Implementar guard de limites (bloquear quando excedido)

## Referência

Ver `projects/fase-03-multitenancy.yaml` para issues detalhadas.
