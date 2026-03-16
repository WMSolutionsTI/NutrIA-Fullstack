#!/usr/bin/env bash
# =============================================================================
# NutrIA-Pro — Script de Setup para Desenvolvimento Local
# =============================================================================
# Uso: ./scripts/dev-setup.sh
#
# Este script configura o ambiente de desenvolvimento completo:
#   1. Verifica pré-requisitos (Docker, Node.js, Python)
#   2. Copia arquivos .env.example → .env
#   3. Instala dependências do frontend
#   4. Sobe todos os containers via docker-compose
# =============================================================================

set -euo pipefail

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'  # No Color

info()    { echo -e "${BLUE}ℹ️  $*${NC}"; }
success() { echo -e "${GREEN}✅ $*${NC}"; }
warn()    { echo -e "${YELLOW}⚠️  $*${NC}"; }
error()   { echo -e "${RED}❌ $*${NC}"; exit 1; }

# Diretório raiz do repositório
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║          NutrIA-Pro — Setup de Desenvolvimento            ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# =============================================================================
# 1. Verificar pré-requisitos
# =============================================================================
info "Verificando pré-requisitos..."

command -v docker    >/dev/null 2>&1 || error "Docker não encontrado. Instale em: https://docs.docker.com/get-docker/"
command -v node      >/dev/null 2>&1 || error "Node.js não encontrado. Instale em: https://nodejs.org/"
command -v python3   >/dev/null 2>&1 || warn "Python 3 não encontrado (opcional para desenvolvimento local)."
command -v git       >/dev/null 2>&1 || error "Git não encontrado."

DOCKER_VERSION=$(docker --version | awk '{print $3}' | tr -d ',')
NODE_VERSION=$(node --version)

success "Docker $DOCKER_VERSION encontrado."
success "Node.js $NODE_VERSION encontrado."

# Docker Compose (plugin v2)
if ! docker compose version >/dev/null 2>&1; then
  error "Docker Compose plugin não encontrado. Atualize o Docker Desktop ou instale: https://docs.docker.com/compose/install/"
fi
success "Docker Compose $(docker compose version --short) encontrado."

# =============================================================================
# 2. Configurar arquivos .env
# =============================================================================
info "Configurando arquivos de ambiente..."

setup_env() {
  local example="$1"
  local target="$2"
  if [ ! -f "$target" ]; then
    cp "$example" "$target"
    success "Criado: $target"
  else
    warn "Já existe: $target (não sobrescrito)"
  fi
}

setup_env "$REPO_ROOT/backend/api/.env.example"     "$REPO_ROOT/backend/api/.env"
setup_env "$REPO_ROOT/backend/workers/.env.example" "$REPO_ROOT/backend/workers/.env"
setup_env "$REPO_ROOT/frontend/.env.example"         "$REPO_ROOT/frontend/.env.local"
setup_env "$REPO_ROOT/infra/.env.prod.example"       "$REPO_ROOT/infra/.env.prod"

# =============================================================================
# 3. Instalar dependências do frontend
# =============================================================================
info "Instalando dependências do frontend..."
cd "$REPO_ROOT/frontend"
npm ci
success "Dependências do frontend instaladas."
cd "$REPO_ROOT"

# =============================================================================
# 4. Instalar pre-commit hooks
# =============================================================================
if command -v pre-commit >/dev/null 2>&1; then
  info "Instalando pre-commit hooks..."
  pre-commit install
  success "Pre-commit hooks instalados."
fi

# =============================================================================
# 5. Subir ambiente Docker
# =============================================================================
info "Subindo ambiente Docker..."
cd "$REPO_ROOT/infra"
docker compose pull --quiet
docker compose up -d
cd "$REPO_ROOT"

# =============================================================================
# 6. Aguardar serviços ficarem saudáveis
# =============================================================================
info "Aguardando serviços ficarem saudáveis (pode levar 1-2 minutos)..."
sleep 15

MAX_WAIT=120
ELAPSED=0
while [ $ELAPSED -lt $MAX_WAIT ]; do
  if docker compose -f infra/docker-compose.yml ps --filter "health=healthy" | grep -q "nutriapro-api"; then
    break
  fi
  sleep 5
  ELAPSED=$((ELAPSED + 5))
done

echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║              ✅ Ambiente no ar!                           ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""
echo "  Serviços disponíveis:"
echo "  • API (Swagger):  http://localhost:8000/docs"
echo "  • Frontend:       http://localhost:3000"
echo "  • Chatwoot:       http://localhost:3001"
echo "  • RabbitMQ UI:    http://localhost:15672  (admin / nutriapro_dev_password)"
echo "  • MinIO Console:  http://localhost:9001   (minioadmin / minioadmin_dev_password)"
echo "  • n8n:            http://localhost:5678"
echo ""
echo "  Comandos úteis:"
echo "  • make logs       → ver logs em tempo real"
echo "  • make migrate    → aplicar migrations"
echo "  • make test       → rodar testes"
echo "  • make down       → parar tudo"
echo ""
