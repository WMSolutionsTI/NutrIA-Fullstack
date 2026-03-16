# ADR-007: Multi-tenancy com row-level isolation no PostgreSQL

**Data:** 2026-03-09
**Status:** Aceito

---

## Contexto

O NutrIA-Pro é uma plataforma SaaS multi-tenant. Precisamos garantir isolamento completo dos dados entre nutricionistas, sem vazar dados de um tenant para outro, enquanto mantemos uma operação simples (único banco de dados).

## Decisão

Usar **row-level isolation** com coluna `tenant_id` em todas as tabelas, com enforcement na camada da aplicação e índices compostos para performance.

## Estratégias de Multi-tenancy Avaliadas

| Estratégia | Isolamento | Complexidade | Custo |
|---|---|---|---|
| **Row-level (escolhida)** | Médio | Baixo | Baixo |
| Schema por tenant | Alto | Médio | Médio |
| Database por tenant | Máximo | Alto | Alto |

## Implementação

```python
# Toda query DEVE incluir tenant_id
SELECT * FROM clients WHERE tenant_id = $1 AND id = $2

# Todos os modelos herdam de TenantModel
class TenantModel(Base):
    tenant_id: UUID = Column(ForeignKey("tenants.id"), nullable=False, index=True)
```

## Consequências

### Positivas
- Operação simples: único banco de dados
- Migrations únicas para todos os tenants
- Menor custo de infraestrutura

### Negativas / Trade-offs
- Risco de vazamento de dados se `tenant_id` for esquecido em alguma query
- Mitigado com: testes de isolamento, middleware de validação, code review obrigatório
- Backups incluem dados de todos os tenants (isolamento de restore é manual)

## Medidas de Segurança

1. Todos os modelos herdam de `TenantModel` (enforcement em nível de classe)
2. Middleware valida `tenant_id` em toda request autenticada
3. Testes de isolamento obrigatórios em toda feature que acessa dados
4. PR template inclui checklist: "tenant_id presente em todos os novos modelos?"

## Referências

- https://www.postgresql.org/docs/current/ddl-rowsecurity.html
