# Fase 15 — Alta Disponibilidade e Performance do Banco de Dados

> PostgreSQL Primary/Replica com streaming replication, PgBouncer para connection pooling, roteamento automático de reads/writes no SQLAlchemy, estratégias anti-travamento e zero-downtime.

## Descrição

Esta fase implementa a estratégia completa de banco de dados para alta disponibilidade, performance e anti-travamento — garantindo que o NutrIA-Pro suporte muitos acessos simultâneos sem degradação ou timeouts.

## Arquitetura

```
                    ┌─────────────────────────────────┐
                    │          PgBouncer               │
                    │   (connection pooling router)    │
                    └────────────┬────────────────┬────┘
                                 │                │
                    ┌────────────▼────┐   ┌───────▼──────────┐
                    │  PostgreSQL     │   │  PostgreSQL       │
                    │  PRIMARY        │   │  REPLICA          │
                    │  (writes only)  │   │  (reads only)     │
                    │                 │──▶│  streaming        │
                    │  INSERT/UPDATE  │   │  replication      │
                    │  DELETE         │   │                   │
                    │  COMMIT         │   │  SELECT, reports  │
                    │                 │   │  anamnese, CRM    │
                    └─────────────────┘   └───────────────────┘
```

## Implementação no SQLAlchemy

```python
# Duas engines configuradas
engine_write = create_async_engine(settings.DATABASE_URL_PRIMARY)
engine_read  = create_async_engine(settings.DATABASE_URL_REPLICA)

# Repositório base roteia automaticamente
class BaseRepository:
    async def get(self, id) -> Model:
        async with AsyncSession(engine_read) as session:  # leitura → replica
            ...

    async def create(self, data) -> Model:
        async with AsyncSession(engine_write) as session:  # escrita → primary
            ...

    async def update(self, id, data) -> Model:
        async with AsyncSession(engine_write) as session:  # escrita → primary
            ...
```

## Estratégias Anti-Travamento

### 1. Connection Pooling com PgBouncer
- Modo: **transaction pooling** (conexão liberada após cada transação)
- Pool size: 20 conexões por serviço (API + workers)
- Max client connections: 1000
- Evita o problema de "too many connections" do PostgreSQL

### 2. Queries Otimizadas
- Todos os SELECTs críticos indexados (tenant_id + foreign keys)
- `EXPLAIN ANALYZE` obrigatório em queries novas antes de deploy
- Paginação cursor-based (não OFFSET) para listas grandes
- Evitar N+1 queries com `selectinload` / `joinedload` no SQLAlchemy

### 3. Cache de Dados Quentes no Redis
- Configurações de tenant: TTL 5 min (`tenant:{id}:config`)
- Prontuário ativo durante consulta: TTL 2h (`medical_record:{id}`)
- Plano alimentar aprovado: TTL 24h (`meal_plan:{id}`)
- Contatos recentes do Chatwoot: TTL 1h

### 4. Locking Distribuído
- Usar Redis `SET NX EX` para locks distribuídos
- Evitar race conditions em workers simultâneos (ex: dois workers processando a mesma mensagem)
- Lock específico por operação:
  - `lock:anamnesis:{client_id}` — evita duas sessões de anamnese simultâneas
  - `lock:mealplan:generate:{appointment_id}` — evita geração dupla de plano

### 5. Backpressure nos Workers
- `prefetch_count` configurável por fila
- Workers de IA (anamnese, plano) com prefetch baixo (1-2) — operações pesadas
- Workers de notificação com prefetch alto (10-50) — operações leves

### 6. Monitoramento de Saúde do Banco
- Alertas para replica lag > 500ms
- Alertas para conexões ativas próximas do limite
- Dashboard Grafana com:
  - Queries lentas (> 1s)
  - Lock waits
  - Cache hit rate do PgBouncer
  - Replica lag em tempo real

## Tasks de Implementação

- [ ] Configurar PostgreSQL Primary com `wal_level = replica`
- [ ] Configurar PostgreSQL Replica com streaming replication
- [ ] Instalar e configurar PgBouncer em transaction mode
- [ ] Criar duas variáveis de ambiente: `DATABASE_URL_PRIMARY` e `DATABASE_URL_REPLICA`
- [ ] Implementar `engine_write` e `engine_read` no SQLAlchemy
- [ ] Refatorar `BaseRepository` para roteamento automático
- [ ] Adicionar índices em todas as foreign keys e `tenant_id`
- [ ] Implementar lock distribuído via Redis para workers críticos
- [ ] Configurar alertas de replica lag no Grafana
- [ ] Stress test: 1000 conexões simultâneas via PgBouncer

## Referência

Nova fase — criar `projects/fase-15-banco-dados-ha.yaml` com issues detalhadas.
