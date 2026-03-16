# Fase 13 — Escala

> Prontidão para escala: auto-scaling de workers, PostgreSQL primary/replica com PgBouncer, Redis Cluster, CDN, particionamento de tabelas, stress tests, arquitetura para 10k+ nutricionistas.

## Descrição

Esta fase prepara o NutrIA-Pro para operar em escala, suportando 10.000+ nutricionistas com milhões de mensagens e consultas processadas mensalmente, sem degradação de performance ou confiabilidade.

## Metas de Escala

| Métrica | Alvo |
|---------|------|
| Nutricionistas ativos | 10.000+ |
| Mensagens/dia | 1.000.000+ |
| Anamneses simultâneas | 5.000+ |
| PDFs gerados/dia | 10.000+ |
| Latência P99 da API | < 500ms |
| Uptime | > 99.9% |
| Tempo de resposta da IA | < 15s (P95) |
| Geração de plano alimentar | < 60s (P95) |

## Estratégias de Escala

### Workers
- Auto-scaling baseado em profundidade de fila (KEDA no Kubernetes)
- Escalonamento horizontal: múltiplas réplicas stateless
- Separação de workers por criticidade:
  - **Tier 1 (crítico):** `message.processor`, `notification.sender`
  - **Tier 2 (negócio):** `anamnesis.conductor`, `mealplan.generator`
  - **Tier 3 (background):** `followup.daily.agent`, `mealplan.pdf.renderer`

### Banco de Dados — Estratégia Anti-Travamento
- **PostgreSQL Primary** — exclusivo para writes (INSERT/UPDATE/DELETE)
- **PostgreSQL Replica(s)** — exclusivo para reads (SELECT, relatórios, anamnese, prontuário)
- **PgBouncer** — connection pooling em transaction mode (reduz conexões abertas)
- **SQLAlchemy** — duas engines configuradas: `engine_write` e `engine_read`
- **Repositório base** — roteia automaticamente: métodos de escrita → primary, leitura → replica
- Particionamento de tabelas de mensagens e follow-up por tenant e data
- `VACUUM` e `ANALYZE` automáticos com monitoramento de bloat
- Sharding horizontal quando necessário (> 100M rows por tabela)

### Cache
- Redis Cluster para alta disponibilidade
- Cache de configurações de tenant (TTL 5 min) — evita queries repetitivas
- Cache de prontuários ativos durante consulta (TTL 2h)
- Cache de planos alimentares aprovados (TTL 24h)

### Armazenamento
- MinIO em modo distribuído para PDFs de planos alimentares
- CDN para assets estáticos do frontend
- Lifecycle policy no MinIO: arquivar PDFs antigos para cold storage

### Infraestrutura
- Migração de Docker Compose para Kubernetes (Helm charts)
- Horizontal Pod Autoscaler para API e workers
- Load balancing com health checks refinados
- Separação de nodes por workload (API, workers IA, workers background)

## Testes de Carga

- Simular 10k nutricionistas com 50 clientes cada (500k pacientes)
- Load test: 10k anamneses simultâneas
- Stress test: geração de 1k planos alimentares em paralelo
- Verificar replica lag sob carga máxima (target: < 100ms)

## Referência

Ver `projects/fase-13-escala.yaml` para issues detalhadas.
