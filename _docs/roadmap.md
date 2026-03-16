# 🗺️ NutrIA-Pro Platform — Complete Development Roadmap

> **Version:** 1.0.0
> **Date:** 2026-03-07
> **Classification:** Internal Engineering — Senior Team Execution Plan
> **Status:** Active

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Guiding Principles](#guiding-principles)
3. [Phase 0 — Foundation & Project Initialization](#phase-0--foundation--project-initialization)
4. [Phase 1 — Infrastructure & Environment Setup](#phase-1--infrastructure--environment-setup)
5. [Phase 2 — Core Backend API Development](#phase-2--core-backend-api-development)
6. [Phase 3 — Multi-Tenant SaaS Architecture](#phase-3--multi-tenant-saas-architecture)
7. [Phase 4 — Messaging Architecture & Chatwoot Integration](#phase-4--messaging-architecture--chatwoot-integration)
8. [Phase 5 — Worker System & Queue Architecture](#phase-5--worker-system--queue-architecture)
9. [Phase 6 — Automation Engine (n8n Integration)](#phase-6--automation-engine-n8n-integration)
10. [Phase 7 — SaaS Business Features](#phase-7--saas-business-features)
11. [Phase 8 — Frontend Dashboards (Next.js)](#phase-8--frontend-dashboards-nextjs)
12. [Phase 9 — Observability, Monitoring & Alerting](#phase-9--observability-monitoring--alerting)
13. [Phase 10 — Security Hardening](#phase-10--security-hardening)
14. [Phase 11 — DevOps, CI/CD & Deployment Strategy](#phase-11--devops-cicd--deployment-strategy)
15. [Phase 12 — Production Launch Preparation](#phase-12--production-launch-preparation)
16. [Phase 13 — Early Scale Readiness](#phase-13--early-scale-readiness)
17. [Milestone Summary Table](#milestone-summary-table)
18. [Risk Register](#risk-register)

---

## Project Overview

**Product Name:** NutrIA-Pro (working title)
**Target Market:** Nutritionists and nutrition clinics
**Business Model:** Multi-tenant SaaS, subscription-based
**Core Value Proposition:** A fully automated communication, scheduling, and client management platform for nutrition professionals — powered by a centralized messaging hub (Chatwoot), an intelligent queue-based worker system, and a no-code automation engine (n8n).

### What This System Does

- Nutritionists subscribe and get their own isolated environment (tenant)
- Each tenant receives a dedicated Chatwoot Inbox (the core tenant identifier)
- Clients communicate through any channel (WhatsApp, Telegram, Instagram, Email, Website, etc.)
- All messages are routed through Chatwoot → Webhook → RabbitMQ → Workers
- Workers process messages, trigger automations, update CRM records, schedule appointments, enforce billing rules, and send responses
- The platform manages the full lifecycle: lead capture → consultation → payment → follow-up → reactivation

---

## Guiding Principles

These principles govern all technical decisions throughout the roadmap:

| Principle | Description |
|---|---|
| **Tenant Isolation First** | Every data model, query, and API endpoint must enforce tenant boundaries |
| **Queue-First Architecture** | No operation that can be async should be synchronous |
| **Horizontal Scale by Default** | Worker replicas must be addable without architectural changes |
| **Idempotency Everywhere** | All queue consumers must be safe to re-execute without side effects |
| **Observability from Day One** | Logging, metrics, and health checks must be built alongside features, not after |
| **Security is Not Optional** | Auth, secret management, rate limiting, and webhook verification are first-class concerns |
| **Configuration Over Code** | Tenant behavior and automation rules must be driven by database configuration, not code changes |
| **Fail Gracefully** | Dead-letter queues, retry logic, and circuit breakers protect against cascade failures |

---

## Phase 0 — Foundation & Project Initialization

**Goal:** Establish project structure, team conventions, tooling, and the foundational decisions that will govern the entire build.

**Estimated Duration:** 1 week
**Milestone:** M0 — Project Initialized

---

### 0.1 — Project Repository Structure

- [ ] **0.1.1** Create a monorepo structure with clearly separated service directories
  - `services/api/` — FastAPI backend
  - `services/workers/` — RabbitMQ consumer workers
  - `services/frontend/` — Next.js dashboard
  - `infra/` — Docker Compose files, Nginx configs, Cloudflare configs
  - `scripts/` — Utility scripts (migrations, seed data, tenant provisioning)
  - `docs/` — Architecture docs, ADRs, API specs (generated later)
  - `.github/` — CI/CD workflows

- [ ] **0.1.2** Initialize Git repository with `main` and `develop` branches
  - `main` — production-ready code only
  - `develop` — integration branch
  - Feature branches follow pattern: `feat/<service>/<description>`
  - Hotfix branches follow pattern: `hotfix/<description>`

- [ ] **0.1.3** Set up branch protection rules
  - Require PR reviews before merging to `main` and `develop`
  - Require passing CI checks before merge
  - No direct push to `main`

- [ ] **0.1.4** Create `.gitignore`, `.editorconfig`, and root `README.md`

---

### 0.2 — Coding Standards & Conventions

- [ ] **0.2.1** Define Python code style standards
  - Use `ruff` for linting
  - Use `black` for formatting
  - Use `mypy` for static type checking
  - Enforce via pre-commit hooks

- [ ] **0.2.2** Define TypeScript/JavaScript code style standards (Frontend)
  - Use `eslint` with strict rules
  - Use `prettier` for formatting
  - Enforce via pre-commit hooks

- [ ] **0.2.3** Create `CONTRIBUTING.md` with:
  - Commit message format (Conventional Commits: `feat:`, `fix:`, `chore:`, etc.)
  - Branch naming conventions
  - PR template with checklist
  - Code review standards

- [ ] **0.2.4** Set up pre-commit hooks using `pre-commit` framework
  - Linting
  - Formatting
  - Type checks
  - Secret scanning (no accidental credential commits)

---

### 0.3 — Environment Variable Strategy

- [ ] **0.3.1** Define a single source of truth for environment configuration
  - Use `.env.example` files for each service (committed to repo)
  - Actual `.env` files are never committed
  - Document every variable with its purpose and example value

- [ ] **0.3.2** Define environment tiers:
  - `local` — developer machine with Docker Compose
  - `staging` — isolated server environment mirroring production
  - `production` — live Contabo VPS

- [ ] **0.3.3** Establish secret management policy
  - Secrets stored in environment variables injected at runtime
  - For production: evaluate Docker Swarm secrets or Vault (documented as future enhancement)
  - All secrets rotated on employee departure

---

### 0.4 — Architecture Decision Records (ADRs)

- [ ] **0.4.1** Create `docs/adr/` directory
- [ ] **0.4.2** Write initial ADRs for foundational decisions:
  - ADR-001: Why FastAPI over Django/Flask
  - ADR-002: Why RabbitMQ over Kafka (initial scale) with migration path documented
  - ADR-003: Why single VPS initially with horizontal expansion path
  - ADR-004: Why Chatwoot as communication hub
  - ADR-005: Why n8n for automation workflows
  - ADR-006: Multi-tenancy model (Inbox ID as tenant identifier)
  - ADR-007: Why PostgreSQL with row-level tenant isolation vs. separate schemas
  - ADR-008: MinIO as S3-compatible object storage

---

### 0.5 — Project Tooling

- [ ] **0.5.1** Set up task runner (`Makefile`) with commands for:
  - `make dev` — start local development environment
  - `make test` — run full test suite
  - `make migrate` — run database migrations
  - `make lint` — run all linters
  - `make build` — build all Docker images
  - `make logs` — tail all container logs

- [ ] **0.5.2** Set up a shared Notion/Confluence/Linear workspace (external to repo) for:
  - Sprint planning
  - Bug tracking
  - Feature requests
  - Deployment runbooks

---

## Phase 1 — Infrastructure & Environment Setup

**Goal:** Stand up a fully working local development environment and a production-ready VPS environment. Every service should be reachable, containerized, and externally accessible via Cloudflare Tunnel.

**Estimated Duration:** 1.5 weeks
**Milestone:** M1 — Infrastructure Running

---

### 1.1 — Docker Compose — Local Development

- [ ] **1.1.1** Write `docker-compose.yml` for local development including all services:
  - `api` — FastAPI application
  - `worker` — RabbitMQ consumer worker (scalable)
  - `rabbitmq` — Message broker with management plugin enabled
  - `postgres` — PostgreSQL database
  - `redis` — For caching, rate limiting, and session management
  - `minio` — Object storage
  - `n8n` — Automation workflow engine
  - `chatwoot-web` — Chatwoot Rails web server
  - `chatwoot-worker` — Chatwoot Sidekiq background jobs
  - `chatwoot-postgres` — Dedicated PostgreSQL for Chatwoot (isolated)
  - `chatwoot-redis` — Dedicated Redis for Chatwoot (isolated)
  - `frontend` — Next.js development server
  - `nginx` — Reverse proxy / local routing

- [ ] **1.1.2** Define Docker networks:
  - `saas-internal` — All internal service communication
  - `chatwoot-internal` — Chatwoot-specific services only (isolated)
  - External traffic only enters through `nginx`

- [ ] **1.1.3** Configure volume mounts for:
  - PostgreSQL data persistence
  - MinIO data persistence
  - n8n workflow data persistence
  - RabbitMQ data persistence

- [ ] **1.1.4** Configure service health checks for all containers
  - PostgreSQL: `pg_isready`
  - RabbitMQ: management API check
  - Redis: `redis-cli ping`
  - API: `/health` endpoint
  - Chatwoot: HTTP check on port 3000

- [ ] **1.1.5** Ensure service startup order with `depends_on` and health check conditions

- [ ] **1.1.6** Create `docker-compose.override.yml` for developer-specific local overrides (hot reload, debug ports, volume mounts for source code)

---

### 1.2 — Docker Compose — Production Configuration

- [ ] **1.2.1** Create separate `docker-compose.prod.yml` for production
  - No volume source mounts (build into image instead)
  - Resource limits defined per container (`mem_limit`, `cpus`)
  - Restart policies: `restart: unless-stopped`
  - Production-grade environment variable injection

- [ ] **1.2.2** Define resource allocation strategy for single Contabo VPS
  - Document estimated RAM allocation per service
  - Document estimated CPU allocation per service
  - Set hard limits to prevent a single service from consuming all resources
  - Plan for a VPS with minimum 16GB RAM, 6+ vCPUs (adjust per chosen plan)

- [ ] **1.2.3** Write production startup runbook:
  - Step-by-step guide to deploy all services on a fresh VPS
  - Order of operations for first-time deployment
  - Verification checklist

---

### 1.3 — Contabo VPS Initial Setup

- [ ] **1.3.1** Provision Contabo VPS (Ubuntu 22.04 LTS recommended)

- [ ] **1.3.2** Server hardening:
  - Create non-root deploy user with sudo privileges
  - Disable root SSH login
  - Configure SSH key-only authentication (disable password auth)
  - Configure UFW firewall:
    - Allow: SSH (22), HTTP (80), HTTPS (443)
    - Deny: all other inbound ports (services communicate internally through Docker networks)
  - Install `fail2ban` for brute-force protection
  - Enable automatic security updates

- [ ] **1.3.3** Install required software:
  - Docker Engine (latest stable)
  - Docker Compose v2
  - Git
  - `make`
  - `htop`, `curl`, `wget`, `unzip` (admin utilities)

- [ ] **1.3.4** Configure swap space (minimum 4GB) as safety net for memory spikes

- [ ] **1.3.5** Configure system limits:
  - Increase `ulimit` for open file descriptors (essential for high-concurrency services)
  - Tune kernel parameters for network performance (`sysctl`)

---

### 1.4 — Cloudflare Tunnel Setup (Cloudflared)

- [ ] **1.4.1** Create Cloudflare account and add project domain

- [ ] **1.4.2** Install `cloudflared` daemon as a Docker container in the compose stack

- [ ] **1.4.3** Configure Cloudflare Tunnel to expose:
  - `api.yourdomain.com` → FastAPI service (internal port 8000)
  - `app.yourdomain.com` → Next.js frontend (internal port 3000)
  - `chat.yourdomain.com` → Chatwoot (internal port 3000)
  - `n8n.yourdomain.com` → n8n (internal port 5678) — restricted access
  - `minio.yourdomain.com` → MinIO console (internal port 9001) — restricted access
  - `rabbit.yourdomain.com` → RabbitMQ management (internal port 15672) — restricted access

- [ ] **1.4.4** Enable Cloudflare Access (Zero Trust) for admin-only internal tools (n8n, MinIO console, RabbitMQ management)
  - Require email authentication via Cloudflare Access before accessing these routes

- [ ] **1.4.5** Enable Cloudflare DDoS protection and rate limiting at DNS level

- [ ] **1.4.6** Verify all routes are reachable with correct TLS termination

---

### 1.5 — PostgreSQL Setup

- [ ] **1.5.1** Configure PostgreSQL with secure superuser credentials

- [ ] **1.5.2** Create separate databases:
  - `nutria-pro` — main application database
  - `chatwoot` — Chatwoot's dedicated database

- [ ] **1.5.3** Create application-specific DB user with least-privilege access:
  - `nutria-pro_app` user: SELECT, INSERT, UPDATE, DELETE on `nutria-pro` database
  - No DDL permissions for application user (migrations run with admin credentials)

- [ ] **1.5.4** Configure `postgresql.conf` for performance:
  - `max_connections`: Tune based on VPS RAM (typically 100–200)
  - `shared_buffers`: 25% of available RAM
  - `work_mem`: 4–16MB depending on query complexity
  - `maintenance_work_mem`: 256MB
  - `effective_cache_size`: 75% of available RAM
  - `wal_level` = replica (prepare for future replication)

- [ ] **1.5.5** Set up automated daily backup using `pg_dump`:
  - Backup to local disk and sync to MinIO bucket (cold storage)
  - Retain 30 days of backups
  - Test restore procedure documented

---

### 1.6 — RabbitMQ Setup

- [ ] **1.6.1** Configure RabbitMQ with:
  - Management plugin enabled
  - Default admin user replaced with secure credentials
  - Virtual host: `/nutria-pro`

- [ ] **1.6.2** Define initial exchange and queue topology (to be implemented in Phase 5):
  - Document all planned exchanges, queues, and routing keys
  - Dead-letter exchange strategy documented

- [ ] **1.6.3** Configure RabbitMQ persistence:
  - `durable: true` on all production queues and exchanges
  - Message persistence (`delivery_mode: 2`) for all critical messages

- [ ] **1.6.4** Configure RabbitMQ resource limits:
  - Memory high watermark: 60% of allocated container memory
  - Disk free limit: 1GB minimum before blocking publishes

---

### 1.7 — MinIO Setup

- [ ] **1.7.1** Deploy MinIO in standalone mode (single node, single drive — sufficient for initial scale)

- [ ] **1.7.2** Create initial buckets:
  - `tenant-files` — diet plans, PDFs, documents uploaded by nutritionists
  - `message-attachments` — files received from client messages
  - `system-exports` — generated reports and exports
  - `db-backups` — PostgreSQL dump files

- [ ] **1.7.3** Configure bucket policies:
  - `tenant-files`: Private (pre-signed URL access only)
  - `message-attachments`: Private (pre-signed URL access only)
  - `system-exports`: Private
  - `db-backups`: Private

- [ ] **1.7.4** Create MinIO access key/secret for application use (least-privilege policy)

---

### 1.8 — Redis Setup

- [ ] **1.8.1** Deploy Redis 7.x with password authentication enabled

- [ ] **1.8.2** Define Redis usage namespaces:
  - `cache:*` — API response caching
  - `session:*` — Frontend user sessions
  - `ratelimit:*` — API rate limiting counters
  - `lock:*` — Distributed locks for idempotent processing
  - `tenant:config:*` — Tenant configuration cache

- [ ] **1.8.3** Configure Redis persistence:
  - Enable AOF (Append-Only File) for durability
  - RDB snapshots every 15 minutes as additional safety net

- [ ] **1.8.4** Configure `maxmemory` and `maxmemory-policy: allkeys-lru` to prevent unbounded growth

---

### 1.9 — Chatwoot Setup

- [ ] **1.9.1** Deploy Chatwoot using official Docker setup

- [ ] **1.9.2** Run Chatwoot database migrations and seed data

- [ ] **1.9.3** Create Chatwoot superadmin account

- [ ] **1.9.4** Configure Chatwoot SMTP settings for email channel support

- [ ] **1.9.5** Enable and document Chatwoot Webhook configuration:
  - Webhook URL: `https://api.yourdomain.com/webhooks/chatwoot`
  - Subscribe to events: `message_created`, `conversation_created`, `conversation_updated`, `contact_updated`

- [ ] **1.9.6** Test Chatwoot is accessible at `https://chat.yourdomain.com`

- [ ] **1.9.7** Document Chatwoot API token management strategy:
  - System API token for backend service-to-Chatwoot communication
  - Secure storage in environment variables (never hardcoded)

---

## Phase 2 — Core Backend API Development

**Goal:** Build the foundational FastAPI application with proper structure, database connectivity, authentication, and base models. This is the backbone that all other features build upon.

**Estimated Duration:** 2 weeks
**Milestone:** M2 — Core API Operational

---

### 2.1 — FastAPI Project Structure

- [ ] **2.1.1** Scaffold FastAPI application with the following structure:
  ```
  services/api/
  ├── app/
  │   ├── main.py                  # Application entry point
  │   ├── config.py                # Settings (pydantic-settings)
  │   ├── dependencies.py          # Shared FastAPI dependencies
  │   ├── database.py              # SQLAlchemy engine and session
  │   ├── models/                  # SQLAlchemy ORM models
  │   ├── schemas/                 # Pydantic request/response schemas
  │   ├── routers/                 # FastAPI routers (one per domain)
  │   ├── services/                # Business logic layer
  │   ├── repositories/            # Data access layer
  │   ├── workers/                 # RabbitMQ publisher utilities
  │   ├── integrations/            # External service clients (Chatwoot, MinIO, etc.)
  │   ├── middleware/              # Custom middleware (logging, tenant, rate limit)
  │   └── utils/                   # Shared utilities
  ├── tests/
  │   ├── unit/
  │   ├── integration/
  │   └── conftest.py
  ├── alembic/                     # Database migrations
  ├── Dockerfile
  ├── requirements.txt
  └── .env.example
  ```

- [ ] **2.1.2** Configure `pydantic-settings` for typed, validated configuration loading from environment variables

- [ ] **2.1.3** Set up structured application logging:
  - Use `structlog` or `python-json-logger` for JSON-formatted logs
  - Include `request_id`, `tenant_id`, and `user_id` in all log entries
  - Log levels configurable via environment variable

---

### 2.2 — Database Layer (SQLAlchemy + Alembic)

- [ ] **2.2.1** Configure SQLAlchemy async engine with asyncpg driver:
  - Connection pool size: configurable via environment variable
  - Pool timeout: 30 seconds
  - Pool recycle: 1800 seconds
  - Overflow: configurable

- [ ] **2.2.2** Create base SQLAlchemy model class with common fields:
  - `id` (UUID, primary key, auto-generated)
  - `created_at` (timestamp with timezone, server default: now)
  - `updated_at` (timestamp with timezone, auto-updated)
  - `tenant_id` (UUID, foreign key — included on all tenant-scoped models)

- [ ] **2.2.3** Initialize Alembic for database migrations:
  - Configure `env.py` to import all models automatically
  - Async migration support using `asyncio` mode
  - Document migration workflow:
    - Create: `alembic revision --autogenerate -m "description"`
    - Apply: `alembic upgrade head`
    - Rollback: `alembic downgrade -1`

- [ ] **2.2.4** Create repository pattern base class:
  - `get_by_id(id, tenant_id)` — always scoped by tenant
  - `list(tenant_id, filters, pagination)` — always scoped by tenant
  - `create(data, tenant_id)`
  - `update(id, data, tenant_id)`
  - `soft_delete(id, tenant_id)` — prefer soft delete over hard delete

- [ ] **2.2.5** Implement database session dependency for FastAPI:
  - Async context manager pattern
  - Automatic rollback on exception
  - Automatic commit on success

---

### 2.3 — Authentication & Authorization System

- [ ] **2.3.1** Implement JWT-based authentication:
  - Access tokens: short-lived (15 minutes)
  - Refresh tokens: long-lived (30 days), stored in database for revocation
  - Algorithm: RS256 (asymmetric) — private key signs, public key verifies
  - Token payload includes: `user_id`, `tenant_id`, `role`, `plan_tier`, `exp`

- [ ] **2.3.2** Implement auth endpoints:
  - `POST /auth/login` — email + password, returns access + refresh tokens
  - `POST /auth/refresh` — refresh token rotation (invalidate old, issue new)
  - `POST /auth/logout` — revoke refresh token
  - `POST /auth/forgot-password` — send reset email
  - `POST /auth/reset-password` — validate token and reset
  - `POST /auth/verify-email` — email verification flow

- [ ] **2.3.3** Implement password security:
  - Argon2 hashing (via `argon2-cffi`)
  - Minimum password requirements enforced at schema level
  - Brute-force protection via rate limiting on auth endpoints

- [ ] **2.3.4** Implement Role-Based Access Control (RBAC):
  - Roles: `platform_admin`, `nutritionist_owner`, `nutritionist_staff`, `readonly`
  - Permission decorators/dependencies for route protection
  - Role checks always combined with tenant scope checks

- [ ] **2.3.5** Create FastAPI dependency `get_current_tenant_user()`:
  - Validates JWT
  - Loads user from database
  - Returns both user and tenant context
  - Used on every protected endpoint

---

### 2.4 — Tenant Context Middleware

- [ ] **2.4.1** Implement `TenantContextMiddleware`:
  - Extracts `tenant_id` from JWT token on every request
  - Stores in Python `contextvars.ContextVar` for thread-safe access
  - Makes tenant_id available globally within the request lifecycle without passing it explicitly through every function call

- [ ] **2.4.2** Implement automatic tenant scoping in the repository base class:
  - Every query automatically appends `WHERE tenant_id = :current_tenant_id`
  - Prevents accidental cross-tenant data access even if developer forgets to filter manually

- [ ] **2.4.3** Add tenant validation on startup of every request:
  - Check tenant status (active, suspended, trial_expired)
  - Return 403 with descriptive error for inactive tenants
  - Cache tenant status in Redis with short TTL (60 seconds) to avoid DB hit on every request

---

### 2.5 — API Health, Versioning & Observability Endpoints

- [ ] **2.5.1** Implement `GET /health` — liveness check (returns 200 if process is alive)

- [ ] **2.5.2** Implement `GET /health/ready` — readiness check:
  - Checks PostgreSQL connectivity
  - Checks Redis connectivity
  - Checks RabbitMQ connectivity
  - Returns 503 if any critical dependency is unavailable

- [ ] **2.5.3** Implement API versioning strategy:
  - All routes prefixed with `/v1/`
  - Future versions (`/v2/`) can coexist without breaking existing clients
  - Deprecation headers added when routes are scheduled for removal

- [ ] **2.5.4** Implement request ID middleware:
  - Generate unique `X-Request-ID` for every request
  - Return it in response headers
  - Include in all log entries for correlation

- [ ] **2.5.5** Configure OpenAPI/Swagger documentation:
  - Available at `/docs` (disable in production or restrict via Cloudflare Access)
  - All endpoints, schemas, and error responses fully documented

---

### 2.6 — Error Handling

- [ ] **2.6.1** Define a standard error response schema:
  ```json
  {
    "error": {
      "code": "TENANT_SUSPENDED",
      "message": "Your account has been suspended.",
      "details": {},
      "request_id": "uuid"
    }
  }
  ```

- [ ] **2.6.2** Implement global exception handlers:
  - `ValidationError` → 422 with field-level details
  - `AuthenticationError` → 401
  - `AuthorizationError` → 403
  - `NotFoundError` → 404
  - `TenantSuspendedError` → 403
  - `PlanLimitExceededError` → 429
  - Unhandled exceptions → 500 with sanitized message (no stack traces exposed)

- [ ] **2.6.3** Ensure all exceptions are logged with full context including `request_id`, `tenant_id`, `user_id`

---

### 2.7 — Testing Foundation

- [ ] **2.7.1** Set up `pytest` with async support (`pytest-asyncio`)

- [ ] **2.7.2** Create `conftest.py` with fixtures:
  - Test database (isolated, wiped between test runs)
  - Test tenant factory
  - Test user factory with JWT generation
  - Mock RabbitMQ publisher
  - Mock Chatwoot API client

- [ ] **2.7.3** Set up code coverage reporting (`pytest-cov`)
  - Minimum coverage threshold: 80%
  - Coverage reports generated in CI

- [ ] **2.7.4** Write initial unit tests for:
  - Auth service (login, token validation, refresh)
  - Tenant scoping (verify cross-tenant queries are blocked)
  - Repository base class

---

## Phase 3 — Multi-Tenant SaaS Architecture

**Goal:** Build the complete tenant lifecycle system — from onboarding a new nutritionist to suspending an inactive tenant — including subscription plans, feature gating, usage tracking, and tenant isolation enforcement.

**Estimated Duration:** 2 weeks
**Milestone:** M3 — Multi-Tenant Core Complete

---

### 3.1 — Tenant Data Model

- [ ] **3.1.1** Design and implement the `tenants` table with fields:
  - `id` (UUID)
  - `name` (business name of the nutritionist/clinic)
  - `slug` (URL-safe unique identifier)
  - `email` (owner email)
  - `status` (`trial`, `active`, `suspended`, `cancelled`, `past_due`)
  - `plan_id` (foreign key to `subscription_plans`)
  - `trial_ends_at` (nullable timestamp)
  - `chatwoot_account_id` (Chatwoot's internal account ID for this tenant)
  - `chatwoot_inbox_id` (the primary inbox used to identify this tenant in webhooks)
  - `chatwoot_api_token` (encrypted, per-tenant token for API calls)
  - `timezone` (e.g., `America/Sao_Paulo`)
  - `locale` (e.g., `pt-BR`)
  - `created_at`, `updated_at`

- [ ] **3.1.2** Design and implement `tenant_users` table:
  - `id`, `tenant_id`, `user_id`, `role`, `created_at`
  - Supports multiple staff members per nutritionist account

- [ ] **3.1.3** Design and implement `tenant_settings` table:
  - Key-value store for tenant-specific configuration
  - Examples: working hours, auto-reply settings, appointment duration defaults
  - Cached in Redis with configurable TTL

---

### 3.2 — Subscription Plans

- [ ] **3.2.1** Design and implement `subscription_plans` table:
  - `id`, `name`, `slug`, `description`
  - `price_monthly`, `price_annual`
  - `is_active` (hide deprecated plans)
  - `created_at`

- [ ] **3.2.2** Design and implement `plan_features` table:
  - `plan_id`, `feature_key`, `feature_value`
  - Feature keys define limits and capabilities, for example:
    - `max_active_clients` → `100`
    - `max_inboxes` → `1`
    - `max_monthly_messages` ��� `5000`
    - `automation_enabled` → `true`
    - `campaign_enabled` → `false`
    - `pdf_generation_enabled` → `true`
    - `priority_support` → `false`

- [ ] **3.2.3** Create default plans:
  - `starter` — limited clients, no campaigns, basic automations
  - `professional` — expanded limits, campaigns enabled
  - `clinic` — unlimited clients, all features, multi-staff support

- [ ] **3.2.4** Implement `PlanFeatureService`:
  - `check_feature(tenant_id, feature_key)` → bool or limit value
  - Results cached in Redis (invalidated on plan change)
  - Used across all services to gate access

---

### 3.3 — Tenant Onboarding Flow

- [ ] **3.3.1** Design and implement the full onboarding sequence as a transactional workflow:
  1. Tenant registers (email, name, password)
  2. Email verification sent
  3. Email verified — tenant status set to `trial`
  4. Chatwoot account created via Chatwoot API (programmatically)
  5. Chatwoot inbox created for this tenant via Chatwoot API
  6. `chatwoot_inbox_id` stored in `tenants` table
  7. Default tenant settings seeded
  8. Welcome automation workflow triggered in n8n
  9. Onboarding checklist created for the tenant dashboard

- [ ] **3.3.2** Implement `TenantProvisioningService`:
  - Encapsulates all steps as an atomic operation
  - If any step fails, compensating actions are taken (rollback)
  - Idempotent — safe to retry if partially completed
  - Logs each step for operational visibility

- [ ] **3.3.3** Implement `POST /tenants/register` endpoint:
  - Validates email uniqueness
  - Creates tenant + user atomically in a DB transaction
  - Triggers async provisioning job via RabbitMQ (Chatwoot setup is async — does not block registration response)

- [ ] **3.3.4** Implement async tenant provisioning worker:
  - Consumes `tenant.provisioning.requested` event from queue
  - Calls Chatwoot API to create account + inbox
  - Updates tenant record with Chatwoot IDs
  - Sends welcome email upon completion

---

### 3.4 — Tenant Lifecycle Management

- [ ] **3.4.1** Implement tenant suspension flow:
  - Triggered by: payment failure, manual admin action, abuse detection
  - Sets tenant status to `suspended`
  - Invalidates tenant config cache in Redis
  - Sends suspension notification email to tenant owner
  - Suspended tenants receive 403 on all API calls

- [ ] **3.4.2** Implement tenant reactivation flow:
  - Triggered by: successful payment, manual admin action
  - Sets tenant status to `active`
  - Clears cache, sends reactivation email

- [ ] **3.4.3** Implement trial expiration flow:
  - Daily background job checks all tenants with `status = trial` and `trial_ends_at < now()`
  - Sends warning emails at: 7 days before, 3 days before, 1 day before expiry
  - On expiry: sets status to `trial_expired`
  - Tenant can upgrade to paid plan to reactivate

- [ ] **3.4.4** Implement tenant cancellation flow:
  - Soft cancellation: data retained for 30 days
  - Hard deletion: scheduled job purges data after retention period
  - Chatwoot inbox deactivated (not deleted) on cancellation

---

### 3.5 — Usage Tracking

- [ ] **3.5.1** Design and implement `usage_records` table:
  - `tenant_id`, `metric_key`, `value`, `period` (month as `YYYY-MM`), `updated_at`
  - Metrics tracked:
    - `messages_sent`
    - `messages_received`
    - `active_clients`
    - `appointments_scheduled`
    - `campaigns_sent`
    - `files_stored_mb`

- [ ] **3.5.2** Implement `UsageTrackingService`:
  - `increment(tenant_id, metric_key, amount=1)`
  - Uses Redis atomic `INCR` for real-time counting
  - Flushes to PostgreSQL every 5 minutes (background task)
  - `check_limit(tenant_id, metric_key)` → returns `(current_value, plan_limit, within_limit)`

- [ ] **3.5.3** Implement usage enforcement middleware:
  - Check limits before processing each message
  - Return `429 Too Many Requests` with `Retry-After` header when limits exceeded
  - Log limit breach events for admin visibility

---

### 3.6 — Admin Panel API

- [ ] **3.6.1** Implement `/admin/tenants` — list all tenants with status and plan info

- [ ] **3.6.2** Implement `/admin/tenants/{id}` — view full tenant details

- [ ] **3.6.3** Implement `/admin/tenants/{id}/suspend` — manually suspend tenant

- [ ] **3.6.4** Implement `/admin/tenants/{id}/activate` — manually activate tenant

- [ ] **3.6.5** Implement `/admin/tenants/{id}/change-plan` — change subscription plan

- [ ] **3.6.6** Implement `/admin/usage` — platform-wide usage metrics dashboard

- [ ] **3.6.7** Secure all `/admin/*` routes with `platform_admin` role check

---

## Phase 4 — Messaging Architecture & Chatwoot Integration

**Goal:** Build the complete pipeline from Chatwoot webhook arrival to message processing, including inbox-to-tenant resolution, webhook security, and the Chatwoot API integration client.

**Estimated Duration:** 2 weeks
**Milestone:** M4 — Messaging Pipeline Operational

---

### 4.1 — Chatwoot Webhook Receiver

- [ ] **4.1.1** Implement `POST /webhooks/chatwoot` endpoint:
  - Publicly accessible (no JWT required — it's an inbound webhook from Chatwoot)
  - HMAC-SHA256 signature verification using shared webhook secret
  - Reject requests with invalid or missing signatures → 401
  - Accept and immediately return `200 OK` (webhook receiver must respond fast)
  - Parse and validate incoming payload
  - Publish event to RabbitMQ asynchronously (do not process inline)

- [ ] **4.1.2** Implement webhook signature verification:
  - Chatwoot sends `X-Chatwoot-Signature` header
  - Compute HMAC-SHA256 of raw request body using shared secret
  - Compare using `hmac.compare_digest` (constant-time comparison, prevents timing attacks)

- [ ] **4.1.3** Implement inbox-to-tenant resolution:
  - Extract `inbox_id` from webhook payload
  - Look up `tenants` table where `chatwoot_inbox_id = inbox_id`
  - Cache mapping in Redis: `inbox:tenant:{inbox_id}` → `tenant_id` (TTL: 5 minutes)
  - If inbox not found: log warning, return 200 (avoid Chatwoot retries for unknown inboxes)
  - If tenant found but suspended: log, skip processing, return 200

- [ ] **4.1.4** Define Chatwoot webhook event types to handle:
  - `message_created` — new message from client or agent
  - `conversation_created` — new conversation started
  - `conversation_updated` — status change, assignment change
  - `contact_created` — new contact
  - `contact_updated` — contact profile update
  - Route each event type to its respective RabbitMQ exchange

- [ ] **4.1.5** Implement webhook idempotency:
  - Extract Chatwoot event ID from payload
  - Check Redis for recently processed event IDs: `webhook:processed:{event_id}`
  - If found: skip (duplicate delivery), return 200
  - If not found: mark as processed with TTL of 24 hours, then proceed

---

### 4.2 — Chatwoot API Integration Client

- [ ] **4.2.1** Build `ChatwootAPIClient` as an async HTTP client (using `httpx`):
  - Base URL configured from environment
  - Per-tenant API token management (fetched from `tenants` table)
  - Automatic retry with exponential backoff on 5xx errors (max 3 retries)
  - Request/response logging with `tenant_id` context

- [ ] **4.2.2** Implement Chatwoot API methods used by the platform:
  - `create_account(name, email)` → creates a new Chatwoot account for tenant
  - `create_inbox(account_id, name, channel_type)` → creates tenant inbox
  - `send_message(account_id, conversation_id, content, attachments)` → sends a message
  - `get_conversation(account_id, conversation_id)` → fetch full conversation
  - `get_contact(account_id, contact_id)` → fetch contact profile
  - `update_conversation_status(account_id, conversation_id, status)` → open/resolved/pending
  - `add_conversation_label(account_id, conversation_id, label)` → tag conversations
  - `assign_conversation(account_id, conversation_id, agent_id)` → assign to agent
  - `create_contact(account_id, name, phone, email)` → create/sync contact

- [ ] **4.2.3** Implement Chatwoot API error handling:
  - 401 Unauthorized: alert — API token may have been revoked
  - 404 Not Found: log warning — conversation/contact may have been deleted
  - 429 Rate Limited: back off and retry with proper delay
  - 500+ Server Error: retry with exponential backoff, alert if persistent

---

### 4.3 — Message Model & Client CRM

- [ ] **4.3.1** Design and implement `clients` table (tenant-scoped):
  - `id`, `tenant_id`, `chatwoot_contact_id`, `name`, `phone`, `email`
  - `status` (`active`, `inactive`, `prospect`)
  - `last_interaction_at`, `created_at`, `updated_at`
  - Indexes: `(tenant_id, chatwoot_contact_id)`, `(tenant_id, phone)`, `(tenant_id, email)`

- [ ] **4.3.2** Design and implement `conversations` table (tenant-scoped):
  - `id`, `tenant_id`, `client_id`, `chatwoot_conversation_id`
  - `channel` (whatsapp, telegram, instagram, email, etc.)
  - `status` (`open`, `resolved`, `pending`, `snoozed`)
  - `last_message_at`, `created_at`, `updated_at`

- [ ] **4.3.3** Design and implement `messages` table (tenant-scoped):
  - `id`, `tenant_id`, `conversation_id`, `chatwoot_message_id`
  - `direction` (`inbound`, `outbound`)
  - `content_type` (`text`, `image`, `document`, `audio`, `video`, `location`)
  - `content` (text content)
  - `attachment_url` (MinIO pre-signed or external URL)
  - `sent_at`, `created_at`

- [ ] **4.3.4** Implement `ClientSyncService`:
  - When a message arrives for an unknown contact: auto-create client record
  - When contact data updates in Chatwoot: sync to local `clients` table
  - Merge logic for duplicate contacts (same phone number)

---

### 4.4 — Inbound Message Processing Pipeline

- [ ] **4.4.1** Define the complete inbound message processing flow:
  1. Webhook arrives at `/webhooks/chatwoot`
  2. Signature verified
  3. Inbox ID extracted → tenant resolved
  4. Event published to RabbitMQ exchange `chatwoot.events`
  5. Routing key: `chatwoot.message.created`, `chatwoot.conversation.created`, etc.
  6. Worker consumes from bound queue
  7. Worker resolves/creates client record
  8. Worker stores message in database
  9. Worker evaluates automation rules for this tenant
  10. Worker triggers n8n webhook if automation rule matches
  11. Worker updates `last_interaction_at` on client and conversation

- [ ] **4.4.2** Implement automation rule evaluation engine:
  - `AutomationRuleEngine` evaluates rules against each incoming message
  - Rules stored in `automation_rules` table (configurable per tenant)
  - Rule conditions: keyword match, conversation status, client tag, channel type, time of day
  - Rule actions: trigger n8n workflow, send reply, assign agent, add label, schedule follow-up

---

## Phase 5 — Worker System & Queue Architecture

**Goal:** Build a robust, horizontally scalable worker system using RabbitMQ. Workers must be idempotent, support retry logic, handle dead-letter queues, and process high message volumes reliably.

**Estimated Duration:** 2 weeks
**Milestone:** M5 — Worker System Operational

---

### 5.1 — Queue Architecture Design

- [ ] **5.1.1** Define the complete exchange and queue topology:

  **Exchanges:**
  | Exchange Name | Type | Purpose |
  |---|---|---|
  | `chatwoot.events` | Topic | All inbound Chatwoot webhook events |
  | `automation.triggers` | Topic | Trigger automation workflows |
  | `notifications.outbound` | Direct | Send messages back through Chatwoot |
  | `scheduler.tasks` | Topic | Scheduled/delayed tasks (reminders, follow-ups) |
  | `billing.events` | Direct | Billing-related events (payment success/failure) |
  | `deadletter` | Direct | Dead-letter exchange for failed messages |

  **Queues:**
  | Queue Name | Bound Exchange | Routing Key | Workers |
  |---|---|---|---|
  | `message.processor` | `chatwoot.events` | `chatwoot.message.created` | 3–10 |
  | `conversation.processor` | `chatwoot.events` | `chatwoot.conversation.*` | 2–5 |
  | `automation.executor` | `automation.triggers` | `#` | 3–10 |
  | `notification.sender` | `notifications.outbound` | `#` | 3–10 |
  | `scheduler.executor` | `scheduler.tasks` | `#` | 2–5 |
  | `billing.processor` | `billing.events` | `#` | 1–2 |
  | `deadletter.queue` | `deadletter` | `#` | 1 (monitoring) |

- [ ] **5.1.2** Configure all queues with:
  - `durable: true` — survive RabbitMQ restarts
  - `x-dead-letter-exchange: deadletter` — failed messages route to DLX
  - `x-dead-letter-routing-key: {queue_name}.dead` — identifiable in DLQ
  - `x-message-ttl: 86400000` — messages expire after 24 hours if not processed (configurable)

- [ ] **5.1.3** Configure prefetch count per worker:
  - Start with `prefetch_count = 10` per worker
  - Tune based on observed throughput and latency under load
  - Document tuning methodology

---

### 5.2 — Worker Service Architecture

- [ ] **5.2.1** Scaffold worker service with structure:
  ```
  services/workers/
  ├── app/
  │   ├── main.py              # Worker entry point — registers all consumers
  │   ├── config.py            # Settings
  │   ├── connection.py        # RabbitMQ async connection management
  │   ├── base_consumer.py     # Abstract base consumer class
  │   ├── consumers/           # One consumer class per queue
  │   ├── handlers/            # Business logic for each event type
  │   ├── services/            # Shared services (DB, Redis, Chatwoot client)
  │   └── utils/               # Retry logic, idempotency helpers
  ├── tests/
  ├── Dockerfile
  └── requirements.txt
  ```

- [ ] **5.2.2** Implement `BaseConsumer` abstract class:
  - Connect to RabbitMQ on startup
  - Declare exchange, queue, and binding (idempotent declarations)
  - Implement consume loop with error handling
  - Call `handle(message)` method (implemented by subclass)
  - On success: `ack` the message
  - On business logic error (expected failure): `nack` without requeue → routes to DLQ
  - On transient error (DB timeout, network issue): `nack` with requeue + delay → retry

- [ ] **5.2.3** Implement retry strategy:
  - Transient errors: retry up to 3 times with exponential backoff (2s, 4s, 8s)
  - Use per-message retry counter stored in message headers
  - After max retries: `nack` without requeue → DLQ
  - Log each retry with full context

- [ ] **5.2.4** Implement idempotency pattern for all consumers:
  - Each message includes a unique `message_id` (UUID generated at publish time)
  - Consumer checks Redis before processing: `worker:processed:{message_id}`
  - If found: ack immediately (already processed), skip
  - If not found: process, then set Redis key with TTL of 48 hours

- [ ] **5.2.5** Implement graceful shutdown:
  - Handle `SIGTERM` signal
  - Stop accepting new messages
  - Finish processing current in-flight message
  - Close connections cleanly
  - Essential for zero-downtime container restarts

---

### 5.3 — Message Processor Worker

- [ ] **5.3.1** Implement `MessageProcessorConsumer`:
  - Consumes from `message.processor` queue
  - Validates message payload (Pydantic schema)
  - Resolves tenant from `inbox_id`
  - Checks tenant status and usage limits
  - Upserts client record
  - Stores message record in database
  - Updates conversation `last_message_at`
  - Emits `automation.triggers` event if applicable
  - Increments `messages_received` usage counter

- [ ] **5.3.2** Implement attachment handling:
  - If message contains attachment URLs from Chatwoot
  - Download attachment asynchronously
  - Upload to MinIO under `message-attachments/{tenant_id}/{conversation_id}/{filename}`
  - Update message record with MinIO path

---

### 5.4 — Notification Sender Worker

- [ ] **5.4.1** Implement `NotificationSenderConsumer`:
  - Consumes from `notification.sender` queue
  - Calls Chatwoot API to send outbound message
  - Handles Chatwoot rate limiting (429) with retry
  - Records outbound message in `messages` table
  - Increments `messages_sent` usage counter
  - On failure: routes to DLQ with error details

---

### 5.5 — Scheduler Worker

- [ ] **5.5.1** Design scheduled task system:
  - `scheduled_tasks` table: `id`, `tenant_id`, `task_type`, `payload`, `scheduled_at`, `executed_at`, `status`
  - Task types: `send_reminder`, `follow_up_message`, `appointment_reminder`, `reactivation_campaign`

- [ ] **5.5.2** Implement scheduler polling mechanism:
  - Background FastAPI async task (runs every 60 seconds)
  - Queries `scheduled_tasks WHERE status = 'pending' AND scheduled_at <= now()`
  - Publishes due tasks to `scheduler.tasks` exchange
  - Updates task status to `queued` to prevent double-publishing

- [ ] **5.5.3** Implement `SchedulerExecutorConsumer`:
  - Consumes from `scheduler.executor` queue
  - Dispatches task to appropriate handler based on `task_type`
  - Updates task status to `executed` or `failed`

---

### 5.6 — Dead Letter Queue Handling

- [ ] **5.6.1** Implement DLQ monitor consumer:
  - Consumes from `deadletter.queue`
  - Logs full message details: queue origin, error reason, tenant_id, payload
  - Stores DLQ record in `dead_letter_events` table for admin review
  - Sends alert to monitoring system (Slack/email) for high DLQ volume

- [ ] **5.6.2** Implement DLQ replay API:
  - `POST /admin/dlq/{id}/replay` — re-publish a specific dead-lettered message back to its original queue
  - Manual replay with audit log entry

- [ ] **5.6.3** Implement DLQ dashboard (basic):
  - `GET /admin/dlq` — list recent dead-lettered messages with filter by tenant and queue

---

### 5.7 — Worker Horizontal Scaling

- [ ] **5.7.1** Document scaling strategy:
  - Each worker type is a separate Docker service
  - Scale with: `docker compose up --scale worker-message=5`
  - No configuration changes required — RabbitMQ distributes messages across replicas automatically
  - Prefetch count controls per-replica concurrency

- [ ] **5.7.2** Define scaling triggers (when to add replicas):
  - Queue depth > 500 messages sustained for > 2 minutes → scale up message workers
  - Queue depth < 50 messages for > 10 minutes → scale down
  - Document manual scaling runbook

- [ ] **5.7.3** Prepare future-ready configuration for container orchestration:
  - Document migration path to Docker Swarm or Kubernetes if single-VPS becomes insufficient
  - Worker Dockerfiles must be stateless and environment-variable driven

---

## Phase 6 — Automation Engine (n8n Integration)

**Goal:** Integrate n8n as the automation backbone. Build the workflow templates, the trigger/callback architecture, and the integration between the worker system and n8n workflows.

**Estimated Duration:** 1.5 weeks
**Milestone:** M6 — Automation Engine Integrated

---

### 6.1 — n8n Configuration & Security

- [ ] **6.1.1** Deploy n8n with:
  - PostgreSQL as workflow storage backend (not SQLite)
  - `EXECUTIONS_DATA_SAVE_ON_SUCCESS: all`
  - `EXECUTIONS_DATA_SAVE_ON_ERROR: all`
  - Webhook base URL configured to `https://n8n.yourdomain.com`

- [ ] **6.1.2** Secure n8n:
  - Basic auth enabled for n8n UI
  - Cloudflare Access layer in front of n8n subdomain (admin-only access)
  - n8n API key configured for programmatic workflow management

- [ ] **6.1.3** Configure n8n timezone to match platform timezone (or UTC)

---

### 6.2 — Automation Trigger Architecture

- [ ] **6.2.1** Design the trigger architecture:
  - Workers call n8n webhook URLs to trigger workflows
  - Each automation rule stores the `n8n_webhook_url` to call
  - Workers POST to n8n with standardized payload:
    ```json
    {
      "tenant_id": "uuid",
      "trigger_event": "message_received",
      "client_id": "uuid",
      "conversation_id": "uuid",
      "message_content": "...",
      "channel": "whatsapp",
      "metadata": {}
    }
    ```

- [ ] **6.2.2** Design callback architecture (n8n → Platform API):
  - n8n workflows call back to the platform API for actions:
    - `POST /internal/messages/send` — send message via Chatwoot
    - `POST /internal/appointments/schedule` — create appointment
    - `POST /internal/clients/{id}/tag` — add tag to client
    - `POST /internal/tasks/schedule` — schedule a future task
  - Internal endpoints protected by API key (not JWT) — dedicated internal token per n8n instance

- [ ] **6.2.3** Implement `POST /internal/*` route group:
  - Authenticated with `X-Internal-API-Key` header
  - Separate middleware — does not require user JWT
  - Rate limited separately from external API

---

### 6.3 — Core Automation Workflow Templates

Build the following n8n workflow templates that tenants can enable:

- [ ] **6.3.1** **Welcome Message Workflow**
  - Trigger: `conversation_created` from a new client
  - Action: Send personalized welcome message via Chatwoot
  - Delay: immediate or configurable delay (e.g., 2 minutes)

- [ ] **6.3.2** **Appointment Confirmation Workflow**
  - Trigger: appointment created event
  - Action: Send confirmation message with appointment details
  - Action: Send calendar invite (if email channel)

- [ ] **6.3.3** **Appointment Reminder Workflow**
  - Trigger: scheduled task (24 hours and 2 hours before appointment)
  - Action: Send reminder message
  - Action: Await client confirmation reply

- [ ] **6.3.4** **Post-Consultation Follow-up Workflow**
  - Trigger: consultation marked as completed
  - Action: Send follow-up message after configurable delay
  - Action: Send diet plan PDF attachment (from MinIO)

- [ ] **6.3.5** **Inactive Client Reactivation Workflow**
  - Trigger: scheduled daily check — client with no interaction > N days
  - Action: Send reactivation message
  - Action: If no response in 7 days, add `inactive` tag

- [ ] **6.3.6** **Payment Request Workflow**
  - Trigger: manual or scheduled
  - Action: Send payment link via message
  - Action: Follow up if not paid within 48 hours

- [ ] **6.3.7** **Out-of-Hours Auto-Reply Workflow**
  - Trigger: `message_created` outside of tenant working hours
  - Action: Send configurable out-of-hours message

---

### 6.4 — Tenant Workflow Management

- [ ] **6.4.1** Design `automation_workflows` table:
  - `id`, `tenant_id`, `name`, `n8n_workflow_id`, `trigger_event`, `is_enabled`, `config_json`

- [ ] **6.4.2** Implement workflow enable/disable API:
  - `PUT /workflows/{id}/toggle` — enable or disable a workflow for a tenant

- [ ] **6.4.3** Implement workflow configuration API:
  - `PUT /workflows/{id}/config` — update workflow parameters (e.g., delay duration, message text)

- [ ] **6.4.4** Implement workflow execution log:
  - `workflow_execution_logs` table: `id`, `tenant_id`, `workflow_id`, `triggered_at`, `status`, `error_message`
  - Visible in tenant dashboard for transparency

---

## Phase 7 — SaaS Business Features

**Goal:** Build all business-layer features: appointment management, client CRM, payment integration, campaign system, and file management.

**Estimated Duration:** 3 weeks
**Milestone:** M7 — Business Features Complete

---

### 7.1 — Appointment Management

- [ ] **7.1.1** Design `appointments` table:
  - `id`, `tenant_id`, `client_id`, `appointment_type_id`
  - `scheduled_at`, `duration_minutes`, `status` (`scheduled`, `confirmed`, `completed`, `cancelled`, `no_show`)
  - `notes`, `created_at`, `updated_at`

- [ ] **7.1.2** Design `appointment_types` table (tenant-configurable):
  - `id`, `tenant_id`, `name`, `duration_minutes`, `price`, `description`

- [ ] **7.1.3** Implement appointment CRUD API:
  - `GET /appointments` — list with filters (date range, client, status)
  - `POST /appointments` — schedule new appointment
  - `PUT /appointments/{id}` — update appointment
  - `POST /appointments/{id}/confirm` — mark as confirmed
  - `POST /appointments/{id}/complete` — mark as completed
  - `POST /appointments/{id}/cancel` — cancel with reason
  - `GET /appointments/calendar` — calendar view data (weekly/monthly)

- [ ] **7.1.4** Implement appointment reminder scheduling:
  - On appointment creation: auto-schedule reminder tasks in `scheduled_tasks`
  - 24-hour reminder
  - 2-hour reminder
  - Post-appointment follow-up (24 hours after `scheduled_at`)

- [ ] **7.1.5** Implement availability checking:
  - `GET /appointments/availability` — returns open slots based on tenant working hours and existing bookings

---

### 7.2 — Client CRM

- [ ] **7.2.1** Implement full client management API:
  - `GET /clients` — paginated list with search and filters
  - `POST /clients` — manually create client
  - `GET /clients/{id}` — full client profile
  - `PUT /clients/{id}` — update client profile
  - `GET /clients/{id}/conversations` — conversation history
  - `GET /clients/{id}/appointments` — appointment history
  - `GET /clients/{id}/notes` — clinical notes
  - `POST /clients/{id}/notes` — add clinical note
  - `GET /clients/{id}/files` — files shared with client
  - `POST /clients/{id}/tags` — add tag
  - `DELETE /clients/{id}/tags/{tag}` — remove tag

- [ ] **7.2.2** Implement client tagging system:
  - `client_tags` table: `client_id`, `tenant_id`, `tag`
  - Tags used for: automation targeting, segmentation, campaign audience

- [ ] **7.2.3** Implement client notes (clinical notes):
  - `client_notes` table: `id`, `tenant_id`, `client_id`, `author_user_id`, `content`, `created_at`
  - Notes are immutable (no update/delete — medical record integrity)
  - Append-only pattern

- [ ] **7.2.4** Implement client import:
  - `POST /clients/import` — CSV upload
  - Background worker processes CSV, creates/upserts clients
  - Returns import job status with success/error counts

---

### 7.3 — File Management

- [ ] **7.3.1** Implement file upload API:
  - `POST /files/upload` — multipart upload
  - Validates file type (PDF, images, documents only)
  - Validates file size (max configurable per plan)
  - Stores in MinIO: `tenant-files/{tenant_id}/{category}/{uuid}-{filename}`
  - Creates `tenant_files` record in database

- [ ] **7.3.2** Implement pre-signed URL generation:
  - `GET /files/{id}/download` — generate time-limited pre-signed MinIO URL (15 minutes TTL)
  - Validates tenant ownership before generating URL

- [ ] **7.3.3** Implement file send via Chatwoot:
  - `POST /files/{id}/send` — send file as attachment to a conversation
  - Worker downloads from MinIO, uploads to Chatwoot, sends message

- [ ] **7.3.4** Implement storage usage tracking:
  - Track `files_stored_mb` in usage records
  - Enforce plan storage limits on upload

---

### 7.4 — Campaign System

- [ ] **7.4.1** Design `campaigns` table:
  - `id`, `tenant_id`, `name`, `status` (`draft`, `scheduled`, `running`, `completed`, `cancelled`)
  - `audience_filter` (JSON — tag-based, activity-based filters)
  - `message_template`, `channel`, `scheduled_at`, `created_at`

- [ ] **7.4.2** Design `campaign_recipients` table:
  - `id`, `campaign_id`, `client_id`, `status` (`pending`, `sent`, `failed`, `opted_out`), `sent_at`

- [ ] **7.4.3** Implement campaign management API:
  - `POST /campaigns` — create campaign
  - `PUT /campaigns/{id}` — update draft campaign
  - `POST /campaigns/{id}/preview-audience` — estimate audience size without sending
  - `POST /campaigns/{id}/launch` — approve and schedule campaign
  - `POST /campaigns/{id}/cancel` — cancel pending/running campaign
  - `GET /campaigns/{id}/stats` — delivery stats

- [ ] **7.4.4** Implement campaign execution worker:
  - Consumes from `scheduler.tasks` queue when campaign is due
  - Fetches audience based on filter criteria
  - Publishes individual send tasks to `notification.sender` queue (rate-controlled)
  - Updates `campaign_recipients` status as messages are sent
  - Respects per-tenant daily message limits

- [ ] **7.4.5** Implement opt-out handling:
  - Clients who reply "STOP" or equivalent are marked as opted-out
  - Opted-out clients excluded from future campaigns

---

### 7.5 — Payment Integration

- [ ] **7.5.1** Evaluate and integrate payment gateway:
  - Primary target: Stripe (global) + MercadoPago (Brazil — given target market)
  - Abstract behind `PaymentGatewayService` interface to allow swapping providers

- [ ] **7.5.2** Implement subscription billing (platform billing — tenant pays platform):
  - `POST /billing/subscribe` — initiate subscription checkout
  - Webhook receiver for payment gateway events:
    - `invoice.payment_succeeded` → activate tenant, extend subscription
    - `invoice.payment_failed` → send warning, start grace period
    - `invoice.payment_failed` (3rd attempt) → suspend tenant
    - `customer.subscription.cancelled` → initiate cancellation flow
  - `GET /billing/invoices` — list tenant's invoices
  - `GET /billing/portal` — redirect to billing portal (Stripe Customer Portal)

- [ ] **7.5.3** Implement payment link generation (nutritionist sends to their clients):
  - `POST /payments/links` — generate a payment link for a specific amount
  - Supported gateways: MercadoPago Checkout, PIX (Brazil)
  - Payment link sent via Chatwoot message
  - Webhook for payment confirmation → update appointment status, send receipt

---

## Phase 8 — Frontend Dashboards (Next.js)

**Goal:** Build the nutritionist-facing dashboard and the platform admin panel using Next.js. The UI must be fast, intuitive, and professional.

**Estimated Duration:** 3 weeks
**Milestone:** M8 — Frontend Operational

---

### 8.1 — Frontend Project Setup

- [ ] **8.1.1** Initialize Next.js 14+ project with App Router

- [ ] **8.1.2** Configure TypeScript with strict mode

- [ ] **8.1.3** Set up TailwindCSS for styling

- [ ] **8.1.4** Install and configure UI component library (shadcn/ui recommended — headless, customizable)

- [ ] **8.1.5** Configure API client layer:
  - Use `axios` or `ky` with interceptors for:
    - Automatic JWT injection
    - Token refresh on 401
    - Request ID header attachment
    - Global error handling

- [ ] **8.1.6** Configure state management:
  - Server state: React Query (TanStack Query) for data fetching, caching, and synchronization
  - Client state: Zustand for lightweight global UI state

- [ ] **8.1.7** Set up i18n for multi-language support (start with Portuguese/English)

---

### 8.2 — Authentication Flows

- [ ] **8.2.1** Implement login page with email/password form

- [ ] **8.2.2** Implement registration/onboarding flow:
  - Step 1: Account details (name, email, password)
  - Step 2: Business details (clinic name, timezone)
  - Step 3: Plan selection
  - Step 4: Email verification
  - Step 5: Onboarding checklist (connect channels, configure first automation)

- [ ] **8.2.3** Implement forgot password / reset password flow

- [ ] **8.2.4** Implement session management:
  - Access token in memory (not localStorage)
  - Refresh token in `HttpOnly` cookie
  - Silent token refresh using React Query background refetch

---

### 8.3 — Nutritionist Dashboard Screens

- [ ] **8.3.1** **Dashboard Home** (`/dashboard`)
  - Today's appointments
  - Unread messages count
  - Recent client activity
  - Key metrics (messages this month, active clients)

- [ ] **8.3.2** **Conversations** (`/conversations`)
  - List of active conversations with search and filter
  - Quick preview of last message
  - Status indicators (open, pending, resolved)
  - Link to open conversation in Chatwoot (deep link)

- [ ] **8.3.3** **Clients** (`/clients`)
  - Paginated client list with search
  - Filter by tag, status, last interaction date
  - Quick actions: send message, schedule appointment, view profile

- [ ] **8.3.4** **Client Profile** (`/clients/{id}`)
  - Contact information
  - Conversation history
  - Appointment history
  - Clinical notes (add note inline)
  - Files
  - Tags management
  - Activity timeline

- [ ] **8.3.5** **Appointments / Calendar** (`/appointments`)
  - Monthly and weekly calendar views
  - Schedule new appointment (modal)
  - Click appointment: view details, confirm, complete, cancel
  - Appointment type configuration

- [ ] **8.3.6** **Files** (`/files`)
  - Upload files
  - Organize by category (diet plans, materials, contracts)
  - Send to client button

- [ ] **8.3.7** **Automations** (`/automations`)
  - List of available workflow templates
  - Toggle enable/disable per workflow
  - Configure parameters (message texts, delays, triggers)
  - Execution logs

- [ ] **8.3.8** **Campaigns** (`/campaigns`)
  - Create and manage campaigns
  - Audience preview
  - Schedule and launch
  - Delivery statistics

- [ ] **8.3.9** **Settings** (`/settings`)
  - Business profile (name, timezone, working hours)
  - Notification preferences
  - Team management (invite staff)
  - Billing and subscription
  - API tokens (for advanced users)
  - Channel connections (link to Chatwoot inbox setup)

---

### 8.4 — Admin Panel Screens

- [ ] **8.4.1** **Admin Dashboard** (`/admin`)
  - Platform-wide metrics
  - Active tenants, MRR, churn indicators

- [ ] **8.4.2** **Tenant Management** (`/admin/tenants`)
  - List all tenants with status, plan, and usage
  - View/edit tenant details
  - Suspend/activate/change plan

- [ ] **8.4.3** **DLQ Monitor** (`/admin/dlq`)
  - List dead-lettered messages
  - Replay failed messages

- [ ] **8.4.4** **Usage Monitor** (`/admin/usage`)
  - Per-tenant usage breakdown
  - Alert on approaching limits

---

### 8.5 — Frontend Performance

- [ ] **8.5.1** Implement route-based code splitting (automatic with Next.js App Router)

- [ ] **8.5.2** Implement optimistic UI updates for mutations (mark message as read, update status) to improve perceived performance

- [ ] **8.5.3** Implement pagination and virtual scrolling for large lists (clients, messages)

- [ ] **8.5.4** Configure Next.js caching strategies:
  - Static pages (marketing): `force-cache`
  - Dashboard pages (dynamic, per-user): `no-store`

- [ ] **8.5.5** Set up Core Web Vitals monitoring

---

## Phase 9 — Observability, Monitoring & Alerting

**Goal:** Implement professional-grade observability so the team can understand system behavior, detect anomalies, and respond to incidents quickly.

**Estimated Duration:** 1 week
**Milestone:** M9 — Observability Operational

---

### 9.1 — Logging Strategy

- [ ] **9.1.1** Standardize structured JSON logging across all services:
  - API: `structlog` with JSON renderer
  - Workers: same pattern
  - All logs include: `timestamp`, `level`, `service`, `request_id`, `tenant_id`, `event`

- [ ] **9.1.2** Define log levels and their usage:
  - `DEBUG` — local development only
  - `INFO` — normal operation events
  - `WARNING` — unexpected but handled situations
  - `ERROR` — failures that need attention
  - `CRITICAL` — system-level failures (database down, queue down)

- [ ] **9.1.3** Centralize logs:
  - Deploy Loki (log aggregation) + Promtail (log shipper) + Grafana (visualization)
  - Configure Promtail to ship Docker container logs to Loki
  - Create Grafana dashboards for log exploration

---

### 9.2 — Metrics

- [ ] **9.2.1** Deploy Prometheus for metrics collection

- [ ] **9.2.2** Instrument FastAPI with `prometheus-fastapi-instrumentator`:
  - HTTP request rate, latency (p50, p95, p99), error rate per endpoint
  - Active connections

- [ ] **9.2.3** Implement custom business metrics (published as Prometheus gauges/counters):
  - `messages_processed_total` (labels: tenant_id, channel)
  - `queue_depth` per queue (published by RabbitMQ exporter)
  - `worker_processing_time_seconds` (histogram)
  - `dlq_messages_total`
  - `active_tenants_total` by status
  - `automation_executions_total` by status

- [ ] **9.2.4** Deploy RabbitMQ Prometheus exporter

- [ ] **9.2.5** Deploy PostgreSQL exporter (`postgres_exporter`)

- [ ] **9.2.6** Deploy Node exporter for VPS hardware metrics (CPU, RAM, disk, network)

- [ ] **9.2.7** Deploy Grafana and create dashboards:
  - **System Overview:** CPU, RAM, disk, network for VPS
  - **API Performance:** Request rate, latency, error rate
  - **Queue Health:** Queue depths, consumer counts, DLQ volume
  - **Worker Performance:** Processing time, throughput, error rate
  - **Business Metrics:** Messages/hour, active tenants, automations executed
  - **Tenant Usage:** Per-tenant message volume

---

### 9.3 — Alerting

- [ ] **9.3.1** Configure Prometheus Alertmanager with alert rules:
  - API error rate > 5% for > 2 minutes → CRITICAL
  - Queue depth > 1000 messages for > 5 minutes → WARNING
  - DLQ depth > 50 messages → WARNING
  - Worker consumer count = 0 for any queue → CRITICAL
  - PostgreSQL connection count > 90% of max → WARNING
  - VPS disk usage > 80% → WARNING
  - API p99 latency > 2000ms for > 5 minutes → WARNING
  - Tenant suspension rate spikes → INFO

- [ ] **9.3.2** Configure alert notification channels:
  - Primary: Slack webhook (ops channel)
  - Secondary: Email (on-call engineer)
  - Critical: PagerDuty or equivalent (for after-hours)

---

### 9.4 — Health Checks & Uptime Monitoring

- [ ] **9.4.1** Configure external uptime monitoring (UptimeRobot or Betterstack):
  - Monitor `https://api.yourdomain.com/health/ready` every 1 minute
  - Monitor `https://app.yourdomain.com` every 1 minute
  - Monitor `https://chat.yourdomain.com` every 5 minutes
  - Alert via email/Slack on downtime

- [ ] **9.4.2** Create internal health dashboard in Grafana showing all service health check statuses

---

## Phase 10 — Security Hardening

**Goal:** Ensure the platform is secured against common attack vectors, data leakage, and unauthorized access before launch.

**Estimated Duration:** 1 week
**Milestone:** M10 — Security Audit Passed

---

### 10.1 — API Security

- [ ] **10.1.1** Implement rate limiting:
  - Use Redis-based sliding window rate limiter
  - Auth endpoints: 10 requests/minute per IP
  - Public API endpoints: 100 requests/minute per tenant
  - Webhook endpoint: 1000 requests/minute (high volume expected)
  - Return `429 Too Many Requests` with `Retry-After` header

- [ ] **10.1.2** Implement request size limits:
  - Max request body: 10MB (configurable)
  - Max file upload: 50MB (configurable per plan)

- [ ] **10.1.3** Implement security headers via Nginx/Cloudflare:
  - `Strict-Transport-Security: max-age=31536000; includeSubDomains`
  - `X-Content-Type-Options: nosniff`
  - `X-Frame-Options: DENY`
  - `Content-Security-Policy` (strict for dashboard)
  - `Referrer-Policy: strict-origin-when-cross-origin`

- [ ] **10.1.4** Configure CORS:
  - Only allow requests from `https://app.yourdomain.com`
  - No wildcard origins in production

---

### 10.2 — Authentication Security

- [ ] **10.2.1** Implement account lockout after 5 consecutive failed login attempts (10-minute lockout, stored in Redis)

- [ ] **10.2.2** Implement JWT token rotation on every use of refresh token

- [ ] **10.2.3** Log all authentication events: login, logout, failed attempt, password reset (with IP and user-agent)

- [ ] **10.2.4** Implement optional TOTP-based Two-Factor Authentication (2FA) for nutritionist accounts

---

### 10.3 — Tenant Isolation Security

- [ ] **10.3.1** Conduct security review of all database queries:
  - Every query must include `tenant_id` in WHERE clause
  - Use automated query analysis in test suite to verify no cross-tenant queries possible

- [ ] **10.3.2** Implement integration tests specifically for tenant isolation:
  - Attempt to access tenant B's data using tenant A's credentials → verify 404 (not 403, to avoid revealing resource existence)

- [ ] **10.3.3** Ensure MinIO object paths always include `tenant_id` as first path segment:
  - File path: `{bucket}/{tenant_id}/{...rest}`
  - Pre-signed URL generation always validates requester's `tenant_id` matches path

---

### 10.4 — Secret Management

- [ ] **10.4.1** Audit all environment variables — no secrets in code or Docker images

- [ ] **10.4.2** Document secret rotation procedures for all critical secrets:
  - JWT signing keys
  - Database passwords
  - RabbitMQ credentials
  - MinIO access keys
  - Chatwoot API tokens
  - Payment gateway API keys

- [ ] **10.4.3** Implement encrypted storage for per-tenant secrets (e.g., Chatwoot API tokens in `tenants` table):
  - Encrypt at rest using AES-256-GCM
  - Encryption key stored in environment variable (not in DB)

- [ ] **10.4.4** Enable PostgreSQL SSL/TLS for all connections

---

### 10.5 — Webhook Security

- [ ] **10.5.1** Verify HMAC signatures for all inbound webhooks (Chatwoot, payment gateway)

- [ ] **10.5.2** Validate webhook payload schemas (reject malformed payloads before processing)

- [ ] **10.5.3** Implement webhook replay protection (as designed in Phase 4.1.5)

- [ ] **10.5.4** Separate webhook processing from business logic (webhook receiver never calls external services inline — always via queue)

---

### 10.6 — Dependency Security

- [ ] **10.6.1** Set up automated dependency vulnerability scanning:
  - Python: `safety` or `pip-audit` in CI
  - Node.js: `npm audit` in CI
  - Docker images: `trivy` image scanning in CI

- [ ] **10.6.2** Pin all dependency versions (no ranges in production `requirements.txt`)

- [ ] **10.6.3** Configure Dependabot (or Renovate) for automated security patch PRs

---

## Phase 11 — DevOps, CI/CD & Deployment Strategy

**Goal:** Build a professional deployment pipeline that enables fast, safe, and repeatable deployments with minimal downtime.

**Estimated Duration:** 1 week
**Milestone:** M11 — CI/CD Pipeline Live

---

### 11.1 — Container Registry

- [ ] **11.1.1** Set up GitHub Container Registry (ghcr.io) or Docker Hub as container registry

- [ ] **11.1.2** Define image naming convention:
  - `ghcr.io/org/nutria-pro-api:{tag}`
  - `ghcr.io/org/nutria-pro-worker:{tag}`
  - `ghcr.io/org/nutria-pro-frontend:{tag}`
  - Tags: `latest` (staging), `v{semver}` (production releases), `sha-{git_sha}` (all builds)

- [ ] **11.1.3** Configure image retention policy (keep last 10 versions, purge older)

---

### 11.2 — CI Pipeline (GitHub Actions)

- [ ] **11.2.1** Implement CI workflow triggered on every PR and push to `develop`/`main`:

  **Job: lint-and-type-check**
  - Run `ruff` linter
  - Run `mypy` type checker
  - Run `eslint` on frontend

  **Job: unit-tests**
  - Start PostgreSQL and Redis as service containers
  - Run `pytest` unit tests with coverage report
  - Fail if coverage < 80%

  **Job: integration-tests**
  - Start full Docker Compose stack
  - Run integration tests against real services
  - Tear down stack after tests

  **Job: security-scan**
  - Run `pip-audit` on Python dependencies
  - Run `npm audit` on frontend dependencies
  - Run `trivy` on built Docker images

  **Job: build-images**
  - Build Docker images for API, workers, frontend
  - Push to registry with `sha-{git_sha}` tag
  - Only on push to `develop` or `main`

---

### 11.3 — CD Pipeline (Deployment)

- [ ] **11.3.1** Implement deployment to staging on every push to `develop`:
  - SSH to staging VPS
  - Pull latest images
  - Run `docker compose -f docker-compose.prod.yml up -d`
  - Run database migrations
  - Run smoke tests
  - Notify Slack on success/failure

- [ ] **11.3.2** Implement deployment to production on tag push (`v*.*.*`) or manual trigger:
  - Require manual approval in GitHub Actions (environment protection rules)
  - Pull specific version images
  - Run migrations
  - Perform health check after deploy
  - Automatic rollback if health check fails (re-deploy previous image)

- [ ] **11.3.3** Implement zero-downtime deployment strategy:
  - Scale up new containers before stopping old ones
  - Use `docker compose up -d --no-deps --build {service}` for rolling updates
  - Ensure workers handle graceful shutdown (Phase 5.2.5)

---

### 11.4 — Database Migration Strategy

- [ ] **11.4.1** Migration execution policy:
  - Migrations always run before new application code is deployed
  - All migrations must be backward compatible (additive, not destructive)
  - Never drop columns or tables in the same migration that removes code references — use two-phase approach

- [ ] **11.4.2** Two-phase migration pattern for breaking changes:
  - Phase 1 (deploy A): Add new column, write to both old and new
  - Phase 2 (deploy B): Remove old column after all code is updated

- [ ] **11.4.3** Require migration review for:
  - Any migration touching tables with millions of rows
  - Index creation (use `CREATE INDEX CONCURRENTLY`)
  - Column type changes

---

### 11.5 — Staging Environment

- [ ] **11.5.1** Provision dedicated staging server (can be smaller Contabo VPS or equivalent)

- [ ] **11.5.2** Staging mirrors production configuration exactly:
  - Same Docker Compose structure
  - Same environment variable structure (different values)
  - Separate Cloudflare Tunnel (`staging.yourdomain.com`)
  - Separate Chatwoot instance or dedicated staging account

- [ ] **11.5.3** Staging database seeded with anonymized test data

- [ ] **11.5.4** Staging used for:
  - Pre-production validation
  - QA testing
  - Load testing (before large traffic spikes)
  - Webhook testing

---

### 11.6 — Backup Strategy

- [ ] **11.6.1** PostgreSQL backup:
  - Daily `pg_dump` via cron job in a dedicated backup container
  - Encrypted backup files using GPG
  - Uploaded to MinIO `db-backups` bucket with date prefix
  - Retention: 30 daily backups, 12 monthly backups
  - Tested restore procedure: monthly restore drill to staging

- [ ] **11.6.2** MinIO data backup:
  - Configure MinIO replication to a secondary storage (Backblaze B2 or Wasabi recommended for cost)
  - Replication runs nightly

- [ ] **11.6.3** n8n workflow backup:
  - Export all workflows via n8n API nightly
  - Store JSON exports in `system-exports` MinIO bucket

- [ ] **11.6.4** RabbitMQ definitions backup:
  - Export definitions (exchanges, queues, bindings) via management API nightly
  - Store in MinIO

---

## Phase 12 — Production Launch Preparation

**Goal:** Prepare the platform for real tenants — final testing, performance validation, operational readiness, and launch checklist.

**Estimated Duration:** 1 week
**Milestone:** M12 — Launch Ready

---

### 12.1 — Load Testing

- [ ] **12.1.1** Define load testing scenarios:
  - 100 concurrent tenants, each receiving 10 messages/minute
  - Burst scenario: 500 messages in 60 seconds
  - Campaign scenario: 1 campaign sending to 1000 recipients simultaneously

- [ ] **12.1.2** Implement load tests using `Locust` or `k6`

- [ ] **12.1.3** Run load tests against staging environment

- [ ] **12.1.4** Identify and resolve performance bottlenecks:
  - Slow database queries (use `EXPLAIN ANALYZE`)
  - Queue backlogs (adjust worker replicas or prefetch counts)
  - API latency (cache hot paths, optimize serialization)

- [ ] **12.1.5** Document maximum tested throughput and recommended scaling thresholds

---

### 12.2 — Database Performance Review

- [ ] **12.2.1** Review all database indexes:
  - Verify indexes on all foreign keys
  - Verify indexes on frequently filtered columns (`tenant_id`, `status`, `scheduled_at`, `last_interaction_at`)
  - Verify composite indexes for common query patterns
  - Remove unused indexes (overhead without benefit)

- [ ] **12.2.2** Run `EXPLAIN ANALYZE` on the 20 most frequent database queries from the API

- [ ] **12.2.3** Configure connection pooling with PgBouncer (optional at launch, required at scale)

---

### 12.3 — Security Review

- [ ] **12.3.1** Conduct internal security review (OWASP Top 10 checklist):
  - Injection (SQL injection, command injection)
  - Broken Authentication
  - Sensitive Data Exposure
  - XML External Entity (not applicable)
  - Broken Access Control → tenant isolation audit
  - Security Misconfiguration
  - Cross-Site Scripting (frontend)
  - Insecure Deserialization
  - Known Vulnerable Components
  - Insufficient Logging & Monitoring

- [ ] **12.3.2** Validate all environment variables are set correctly in production

- [ ] **12.3.3** Confirm no debug endpoints, development credentials, or test data exist in production

---

### 12.4 — Operational Readiness

- [ ] **12.4.1** Write and review operations runbooks:
  - Runbook: Deploy new version
  - Runbook: Roll back failed deployment
  - Runbook: Restart crashed service
  - Runbook: Scale up workers
  - Runbook: Replay DLQ messages
  - Runbook: Emergency tenant suspension
  - Runbook: Database restore from backup
  - Runbook: RabbitMQ queue purge (for stuck messages)

- [ ] **12.4.2** Conduct on-call training with engineering team:
  - Walk through each runbook
  - Practice rollback procedure in staging

- [ ] **12.4.3** Set up incident management process:
  - Severity levels: P0 (platform down), P1 (major feature broken), P2 (degraded), P3 (minor)
  - Response time SLOs per severity
  - Post-incident review process

---

### 12.5 — Launch Checklist

- [ ] **12.5.1** All environment variables set and verified in production
- [ ] **12.5.2** Database migrations applied to production database
- [ ] **12.5.3** Cloudflare Tunnel verified for all domains
- [ ] **12.5.4** SSL certificates verified (Cloudflare managed)
- [ ] **12.5.5** Chatwoot instance healthy and inboxes configured
- [ ] **12.5.6** n8n workflows deployed and tested
- [ ] **12.5.7** RabbitMQ exchanges, queues, and bindings declared
- [ ] **12.5.8** All monitoring dashboards operational
- [ ] **12.5.9** All alerts configured and tested (send a test alert)
- [ ] **12.5.10** Uptime monitoring configured
- [ ] **12.5.11** Backup jobs running and verified
- [ ] **12.5.12** Admin user created for platform operations
- [ ] **12.5.13** Subscription plans seeded in database
- [ ] **12.5.14** Email sending (SMTP/transactional) verified
- [ ] **12.5.15** Payment gateway webhooks registered and verified
- [ ] **12.5.16** Rate limits tested
- [ ] **12.5.17** Load test results reviewed and acceptable
- [ ] **12.5.18** Rollback procedure tested in staging

---

## Phase 13 — Early Scale Readiness

**Goal:** Prepare the platform for growth beyond the initial VPS — define the path from single server to multi-node infrastructure without requiring architectural changes.

**Estimated Duration:** Ongoing — begins after first 100 tenants
**Milestone:** M13 — Scale-Ready Architecture

---

### 13.1 — Horizontal Worker Scaling

- [ ] **13.1.1** Document worker scaling playbook:
  - Trigger: sustained queue depth > threshold (see Phase 5.7.2)
  - Action: `docker compose -f docker-compose.prod.yml up -d --scale worker-message=N`
  - Workers are stateless — no data migration needed
  - Monitor queue drain rate after scaling to verify improvement

- [ ] **13.1.2** Implement auto-scaling monitoring script:
  - Monitor RabbitMQ queue depths every 30 seconds
  - Alert to Slack with current depths and recommendation to scale
  - (Manual scaling initially — automated scaling is a future enhancement)

---

### 13.2 — Database Scaling Path

- [ ] **13.2.1** Document PostgreSQL read replica setup:
  - When needed: API read queries > 80% of max connections
  - How: Add streaming replica, route read queries to replica
  - No application code changes required if using read/write query routing via PgBouncer

- [ ] **13.2.2** Implement database read/write routing:
  - Write operations → primary
  - Read operations (GET endpoints, report queries) → replica (when available)
  - Configure via environment variable: `DATABASE_READ_URL` (separate from `DATABASE_URL`)

- [ ] **13.2.3** Document table partitioning strategy for `messages` and `workflow_execution_logs`:
  - Partition by `tenant_id` hash or by `created_at` range when table exceeds 10M rows
  - This is a future optimization — document now, implement when needed

---

### 13.3 — Multi-Node Infrastructure Path

- [ ] **13.3.1** Document migration path from single VPS to multi-node:
  - **Trigger:** CPU > 80% or RAM > 85% sustained for 1 week
  - **Step 1:** Add a second Contabo VPS for workers only (stateless, easy to add)
  - **Step 2:** Move PostgreSQL to a managed database service or dedicated server
  - **Step 3:** Move RabbitMQ to a managed service (CloudAMQP) or dedicated server
  - **Step 4:** Move object storage to managed S3-compatible service (Backblaze B2)
  - **Step 5:** Evaluate migration to Docker Swarm or Kubernetes for full orchestration

- [ ] **13.3.2** Ensure all services are configured by environment variables only:
  - No hardcoded hostnames or IPs
  - All inter-service URLs configurable
  - This ensures services can be moved to different servers without code changes

---

### 13.4 — Caching Strategy Maturation

- [ ] **13.4.1** Implement response caching for high-read, low-update API endpoints:
  - `GET /plans` — cache 1 hour
  - `GET /clients/{id}` — cache 30 seconds (invalidated on update)
  - `GET /appointments/availability` — cache 60 seconds

- [ ] **13.4.2** Implement cache invalidation strategy:
  - Tag-based invalidation: when a resource updates, invalidate all cached responses tagged with its ID
  - Use Redis key patterns for easy bulk invalidation

- [ ] **13.4.3** Monitor cache hit rate in Grafana dashboard:
  - Target: > 60% hit rate for cacheable endpoints
  - Tune TTLs based on observed data

---

### 13.5 — RabbitMQ Scaling Path

- [ ] **13.5.1** Document RabbitMQ cluster setup procedure:
  - When needed: single RabbitMQ node becomes bottleneck
  - How: Add RabbitMQ nodes and form a cluster
  - Enable quorum queues (replace classic queues) for cluster safety

- [ ] **13.5.2** Evaluate transition to CloudAMQP managed service at scale:
  - Eliminates RabbitMQ operational overhead
  - No message loss guarantees
  - Cost justified when saving engineering time on RabbitMQ maintenance

---

### 13.6 — Tenant-Aware Rate Limiting at Scale

- [ ] **13.6.1** Review rate limiting implementation as tenant count grows:
  - Ensure Redis-based rate limiter scales with tenant count
  - Consider sliding window vs. token bucket algorithm trade-offs
  - Document when a distributed rate limiter service becomes necessary

---

## Milestone Summary Table

| # | Milestone | Phase | Description | Est. Duration |
|---|---|---|---|---|
| M0 | Project Initialized | 0 | Repository, conventions, ADRs in place | 1 week |
| M1 | Infrastructure Running | 1 | All services containerized, VPS live, Cloudflare Tunnel active | 1.5 weeks |
| M2 | Core API Operational | 2 | FastAPI app with auth, DB, error handling, tests | 2 weeks |
| M3 | Multi-Tenant Core | 3 | Tenant lifecycle, plans, usage, onboarding | 2 weeks |
| M4 | Messaging Pipeline | 4 | Chatwoot webhook → queue → tenant resolved | 2 weeks |
| M5 | Worker System | 5 | Full queue/worker system with retry and DLQ | 2 weeks |
| M6 | Automation Engine | 6 | n8n integrated, core workflows built | 1.5 weeks |
| M7 | Business Features | 7 | Appointments, CRM, files, campaigns, payments | 3 weeks |
| M8 | Frontend Live | 8 | Next.js dashboards for tenants and admin | 3 weeks |
| M9 | Observability Live | 9 | Logging, metrics, dashboards, alerting | 1 week |
| M10 | Security Hardened | 10 | Full security audit and hardening | 1 week |
| M11 | CI/CD Pipeline | 11 | Automated build, test, deploy pipeline | 1 week |
| M12 | Launch Ready | 12 | Load tested, runbooks written, checklist complete | 1 week |
| M13 | Scale Ready | 13 | Horizontal scaling path documented and tested | Ongoing |

**Estimated Total to Production Launch: ~22–24 weeks (5–6 months) with a 2–3 engineer team**

---

## Risk Register

| ID | Risk | Probability | Impact | Mitigation |
|---|---|---|---|---|
| R01 | Chatwoot webhook delivery failures | Medium | High | Idempotent webhook processing; webhook replay via Chatwoot admin |
| R02 | RabbitMQ message loss on restart | Low | Critical | Durable queues + persistent messages + regular definition backups |
| R03 | Tenant data cross-contamination | Low | Critical | Automated tenant isolation tests in CI; repository base class enforces scoping |
| R04 | VPS resource exhaustion | Medium | High | Resource limits per container; scaling runbook ready; monitoring alerts before saturation |
| R05 | n8n workflow execution failures | Medium | Medium | Execution logs in DB; DLQ for failed triggers; manual replay capability |
| R06 | Payment gateway webhook failures | Low | High | Webhook retry handling; idempotent payment processing; reconciliation job |
| R07 | Chatwoot API rate limiting | Low | Medium | Exponential backoff; queue-based outbound message rate control |
| R08 | Database migration failures in production | Low | Critical | Always run migrations before code deploy; backward-compatible migration policy; tested rollback |
| R09 | Secret exposure via environment variables | Low | Critical | Secret scanning in CI; `.env` never committed; rotation procedure documented |
| R10 | Single VPS becoming a single point of failure | Medium | High | Documented multi-node migration path; regular backups; monitoring + fast response runbooks |
| R11 | Worker message processing storms | Medium | Medium | Prefetch count limits; per-tenant rate limiting; DLQ prevents poison pill loops |
| R12 | High DLQ volume goes unnoticed | Low | Medium | DLQ monitoring alerts in Alertmanager; admin dashboard visibility |

---

*This roadmap is a living document. It should be reviewed at the end of each milestone and updated to reflect lessons learned, changing requirements, and new technical discoveries. No architecture is perfect before it meets reality — the goal is to build a solid foundation that can evolve without requiring complete rewrites.*

---

**Document Owner:** Engineering Team
**Last Updated:** 2026-03-07
**Next Review:** End of Phase 0 (M0 completion)
