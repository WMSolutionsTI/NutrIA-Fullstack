# ADR-001: FastAPI como framework da API backend

**Data:** 2026-03-09
**Status:** Aceito

---

## Contexto

O NutrIA-Pro precisa de uma API REST de alta performance para suportar múltiplos tenants simultâneos, com operações de I/O intensivas (banco de dados, mensageria, integrações externas). A escolha do framework impacta performance, produtividade de desenvolvimento e manutenibilidade a longo prazo.

## Decisão

Usar **FastAPI** como framework principal da API backend.

## Alternativas Consideradas

| Alternativa | Por que descartada |
|---|---|
| Django REST Framework | Síncrono por padrão, overhead do ORM do Django, mais pesado para APIs puras |
| Flask | Minimalista demais, requer muitas bibliotecas externas, sem suporte nativo async |
| Node.js (Express/Fastify) | Time com mais expertise em Python; consistência com workers |
| Go (Gin/Fiber) | Curva de aprendizado alta para o time atual |

## Consequências

### Positivas
- **Performance**: suporte nativo a async/await com Python 3.12+
- **Documentação automática**: Swagger UI e ReDoc gerados automaticamente via OpenAPI
- **Validação**: Pydantic v2 integrado nativamente para validação e serialização
- **Tipagem**: type hints Python como cidadãos de primeira classe
- **Ecossistema**: SQLAlchemy async, Alembic, pytest-asyncio bem integrados

### Negativas / Trade-offs
- Menos "baterias inclusas" que Django (sem admin, sem auth nativo)
- Requer mais decisões manuais de arquitetura (estrutura de pastas, auth, etc.)
- ORM assíncrono (SQLAlchemy async) tem curva de aprendizado mais íngreme

## Referências

- https://fastapi.tiangolo.com/
- https://docs.pydantic.dev/latest/
