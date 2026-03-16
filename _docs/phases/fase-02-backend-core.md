# Fase 02 — Backend Core

> Desenvolvimento da API core em FastAPI: autenticação JWT, CRUD base, modelos de dados com suporte a prontuário clínico, migrations Alembic, repositório com roteamento read/write automático.

## Descrição

Esta fase constrói o esqueleto do backend FastAPI com autenticação, autorização, estrutura de serviços e todas as fundações necessárias para as fases subsequentes — incluindo a base do prontuário eletrônico do paciente e o roteamento de banco de dados read/write.

## Stack de Backend

- **Framework:** FastAPI (Python 3.12+)
- **ORM:** SQLAlchemy 2.0 (async)
- **Migrations:** Alembic
- **Validação:** Pydantic v2
- **Autenticação:** JWT (access + refresh tokens)
- **Testes:** pytest + pytest-asyncio

## Objetivos

- Scaffoldar projeto FastAPI com estrutura de pastas padronizada
- **Configurar SQLAlchemy async com duas engines: `db_write` (primary) e `db_read` (replica)**
- **Criar classe base de repositório que roteia automaticamente: writes → `db_write`, reads → `db_read`**
- Criar migrations base com Alembic
- Implementar autenticação JWT (login, refresh, logout)
- Implementar CRUD base para nutritionists/tenants
- **Criar modelos base de prontuário: `MedicalRecord`, `AnamnesisSession`, `AnamnesisAnswer`**
- **Criar modelo `MealPlan` com status de aprovação e versionamento**
- Configurar middleware: logging, CORS, request ID
- Implementar health check endpoints (inclui status da replica de leitura)
- Configurar pytest com banco de dados de teste isolado

## Modelos de Dados Principais

| Modelo | Descrição |
|--------|-----------|
| `Tenant` | Nutricionista/clínica — tenant isolado |
| `Client` | Paciente do nutricionista |
| `MedicalRecord` | Prontuário do paciente (dados clínicos contínuos) |
| `AnamnesisSession` | Sessão de entrevista pré-consulta conduzida pela IA |
| `AnamnesisAnswer` | Respostas individuais da anamnese (texto ou transcrição de voz) |
| `Appointment` | Consulta agendada |
| `MealPlan` | Plano alimentar gerado pela IA (com status: draft/pending_approval/approved) |
| `MealPlanVersion` | Histórico de versões do plano alimentar |
| `FollowUpLog` | Registro diário de acompanhamento pós-consulta |

## Endpoints Core

- `POST /auth/login` — autenticação com JWT
- `POST /auth/refresh` — renovação de token
- `GET /health` e `GET /health/ready` — health checks (inclui replica lag)
- `GET/POST/PUT/DELETE /nutritionists` — CRUD de nutricionistas
- `GET/POST /clients/{id}/medical-record` — prontuário do paciente
- `GET/POST /clients/{id}/anamnesis` — sessões de anamnese
- `GET/PUT /meal-plans/{id}` — visualização e edição do plano alimentar
- `POST /meal-plans/{id}/approve` — aprovação do plano alimentar

## Referência

Ver `projects/fase-02-backend-core.yaml` para issues detalhadas.
