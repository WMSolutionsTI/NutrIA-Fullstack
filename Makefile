# =============================================================================
# NutrIA-Pro — Makefile de Comandos Utilitários
# =============================================================================
# O Makefile é um arquivo especial que permite criar "atalhos" para comandos
# longos e repetitivos. Em vez de digitar:
#   docker compose -f infra/docker-compose.yml up -d
# Você digita apenas:
#   make dev
#
# Como usar: make <comando>
# Exemplo:   make dev
# =============================================================================

# .PHONY diz ao Make que esses nomes são comandos, não arquivos.
.PHONY: help dev down build logs logs-api logs-worker test lint migrate seed \
        shell-api shell-db prod-deploy prod-down prod-logs setup

# Caminhos
COMPOSE_DEV  = docker compose -f infra/docker-compose.yml
COMPOSE_PROD = docker compose -f infra/docker-compose.prod.yml

# -----------------------------------------------------------------------------
# PADRÃO: ao digitar só "make" sem nenhum comando, mostra a ajuda
# -----------------------------------------------------------------------------
.DEFAULT_GOAL := help

## help: Exibe esta mensagem de ajuda com todos os comandos disponíveis
help:
	@echo ""
	@echo "╔══════════════════════════════════════════════════════════╗"
	@echo "║              NutrIA-Pro — Comandos Disponíveis            ║"
	@echo "╚══════════════════════════════════════════════════════════╝"
	@echo ""
	@echo "  🛠️  SETUP"
	@echo "     make setup         Configura o ambiente de desenvolvimento do zero"
	@echo ""
	@echo "  🚀 DESENVOLVIMENTO"
	@echo "     make dev           Sobe todos os serviços em modo desenvolvimento"
	@echo "     make down          Para todos os serviços"
	@echo "     make build         Reconstrói todas as imagens Docker"
	@echo ""
	@echo "  🚢 PRODUÇÃO (VPS)"
	@echo "     make prod-deploy   Deploy do backend no VPS"
	@echo "     make prod-down     Para os serviços de produção"
	@echo "     make prod-logs     Exibe logs de produção em tempo real"
	@echo ""
	@echo "  📋 LOGS"
	@echo "     make logs          Exibe logs de todos os containers em tempo real"
	@echo "     make logs-api      Exibe logs apenas da API"
	@echo "     make logs-worker   Exibe logs apenas dos workers"
	@echo ""
	@echo "  🧪 QUALIDADE"
	@echo "     make test          Executa a suíte completa de testes"
	@echo "     make lint          Executa todos os linters"
	@echo ""
	@echo "  🗃️  BANCO DE DADOS"
	@echo "     make migrate       Aplica as migrations pendentes"
	@echo "     make seed          Popula dados iniciais"
	@echo ""
	@echo "  🐚 SHELLS (acesso direto aos containers)"
	@echo "     make shell-api     Abre um terminal dentro do container da API"
	@echo "     make shell-db      Abre o psql no container do PostgreSQL"
	@echo ""

# =============================================================================
# 🛠️ SETUP
# =============================================================================

## setup: Configura o ambiente de desenvolvimento do zero
setup:
	@echo "🛠️  Configurando ambiente de desenvolvimento..."
	./scripts/dev-setup.sh

# =============================================================================
# 🚀 AMBIENTE DE DESENVOLVIMENTO
# =============================================================================

## dev: Sobe todos os serviços em modo desenvolvimento
dev:
	@echo "🚀 Subindo o ambiente de desenvolvimento..."
	$(COMPOSE_DEV) up -d
	@echo ""
	@echo "✅ Ambiente no ar! Acesse os serviços:"
	@echo "   • API (Swagger):   http://localhost:8000/docs"
	@echo "   • Frontend:        http://localhost:3000"
	@echo "   • Chatwoot:        http://localhost:3001"
	@echo "   • RabbitMQ:        http://localhost:15672"
	@echo "   • MinIO:           http://localhost:9001"
	@echo "   • n8n:             http://localhost:5678"

## down: Para todos os serviços
down:
	@echo "🛑 Parando todos os serviços..."
	$(COMPOSE_DEV) down
	@echo "✅ Serviços parados."

## build: Reconstrói todas as imagens Docker (útil após mudar dependências)
build:
	@echo "🔨 Reconstruindo todas as imagens Docker..."
	$(COMPOSE_DEV) build --no-cache
	@echo "✅ Build concluído."

# =============================================================================
# 🚢 PRODUÇÃO
# =============================================================================

## prod-deploy: Deploy do backend no VPS (via scripts/deploy-backend.sh)
prod-deploy:
	@echo "🚢 Iniciando deploy de produção..."
	./scripts/deploy-backend.sh $(TAG)

## prod-down: Para os serviços de produção no VPS
prod-down:
	$(COMPOSE_PROD) --env-file infra/.env.prod down

## prod-logs: Exibe logs de produção em tempo real
prod-logs:
	$(COMPOSE_PROD) --env-file infra/.env.prod logs -f

# =============================================================================
# 📋 LOGS
# =============================================================================

## logs: Exibe logs de todos os containers em tempo real (Ctrl+C para sair)
logs:
	$(COMPOSE_DEV) logs -f

## logs-api: Exibe logs apenas da API
logs-api:
	$(COMPOSE_DEV) logs -f api

## logs-worker: Exibe logs apenas dos workers
logs-worker:
	$(COMPOSE_DEV) logs -f worker

# =============================================================================
# 🧪 QUALIDADE DE CÓDIGO
# =============================================================================

## test: Executa a suíte completa de testes com relatório de cobertura
test:
	@echo "🧪 Rodando todos os testes..."
	$(COMPOSE_DEV) exec api pytest tests/ -v --cov=app --cov-report=term-missing
	@echo "✅ Testes concluídos."

## lint: Executa todos os linters (verifica qualidade e formatação do código)
lint:
	@echo "🔍 Rodando linters..."
	$(COMPOSE_DEV) exec api ruff check app/ tests/
	$(COMPOSE_DEV) exec api ruff format --check app/ tests/
	$(COMPOSE_DEV) exec api mypy app/
	@echo "✅ Lint concluído."

# =============================================================================
# 🗃️ BANCO DE DADOS
# =============================================================================

## migrate: Aplica todas as migrations pendentes no banco de dados
migrate:
	@echo "🗃️  Rodando migrations..."
	$(COMPOSE_DEV) exec api alembic upgrade head
	@echo "✅ Migrations aplicadas."

## seed: Popula o banco com dados iniciais (planos, configurações padrão)
seed:
	@echo "🌱 Populando dados iniciais..."
	$(COMPOSE_DEV) exec api python scripts/seed.py
	@echo "✅ Seed concluído."

# =============================================================================
# 🐚 ACESSO DIRETO AOS CONTAINERS
# =============================================================================

## shell-api: Abre um terminal interativo dentro do container da API
shell-api:
	@echo "🐚 Abrindo shell no container da API..."
	$(COMPOSE_DEV) exec api bash

## shell-db: Abre o cliente psql diretamente no container do PostgreSQL
shell-db:
	@echo "🐘 Abrindo psql no container do PostgreSQL..."
	$(COMPOSE_DEV) exec postgres psql -U nutriapro_app -d nutriapro
