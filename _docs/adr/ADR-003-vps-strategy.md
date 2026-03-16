# ADR-003: Estratégia de VPS único com expansão horizontal planejada

**Data:** 2026-03-09
**Status:** Aceito

---

## Contexto

O NutrIA-Pro precisa de uma estratégia de infraestrutura que seja economicamente viável no lançamento (poucos tenants) mas que possa escalar conforme a base de clientes cresce, sem reescritas de arquitetura.

## Decisão

Iniciar com **VPS único** (Contabo, 8 vCPU / 32GB RAM) rodando todos os serviços via Docker Compose, com **path de expansão horizontal documentado e testado**.

## Alternativas Consideradas

| Alternativa | Por que descartada |
|---|---|
| Kubernetes desde o início | Complexidade operacional excessiva para fase inicial; custo alto |
| AWS ECS/EKS | Vendor lock-in; custo proibitivo no início |
| Heroku/Railway | Limitações de customização; custo escalona rapidamente; sem controle de rede |
| Docker Swarm | Meio-termo razoável, mas planejamos migrar para K8s quando necessário |

## Path de Expansão

```
Fase 1 (0-50 tenants):   1 VPS — todos os serviços
Fase 2 (50-200 tenants): 2 VPS — workers em servidor separado
Fase 3 (200+ tenants):   PostgreSQL dedicado + RabbitMQ cluster
Fase 4 (500+ tenants):   Docker Swarm ou Kubernetes
```

## Consequências

### Positivas
- Custo inicial muito baixo (~€15-30/mês)
- Operação simples com Docker Compose
- Deploy rápido e previsível
- Controle total da infraestrutura

### Negativas / Trade-offs
- Ponto único de falha no início (mitigado com backups e monitoramento)
- Escalonamento vertical tem limite físico
- Requer migração cuidadosa ao crescer

## Referências

- Roadmap Fase 13: Arquitetura Pronta para Escala
