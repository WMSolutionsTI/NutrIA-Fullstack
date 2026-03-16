#!/usr/bin/env bash
# =============================================================================
# NutrIA-Pro — Script de Deploy do Backend para VPS Contabo
# =============================================================================
# Uso: ./scripts/deploy-backend.sh [TAG]
#
# TAG: versão das imagens Docker (padrão: latest)
#
# Pré-requisitos:
#   - SSH configurado para o VPS
#   - VPS_HOST, VPS_USER, VPS_PORT no ambiente
#   - .env.prod configurado no diretório infra/ do VPS
#
# Exemplo:
#   VPS_HOST=vps.contabo.com VPS_USER=root ./scripts/deploy-backend.sh sha-abc123
# =============================================================================

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

info()    { echo -e "${BLUE}ℹ️  $*${NC}"; }
success() { echo -e "${GREEN}✅ $*${NC}"; }
warn()    { echo -e "${YELLOW}⚠️  $*${NC}"; }
error()   { echo -e "${RED}❌ $*${NC}"; exit 1; }

# Tag da imagem (argumento opcional, padrão: latest)
TAG="${1:-latest}"

# Configurações do VPS (via variáveis de ambiente ou defaults)
VPS_HOST="${VPS_HOST:?'Defina VPS_HOST com o IP/hostname do VPS'}"
VPS_USER="${VPS_USER:-root}"
VPS_PORT="${VPS_PORT:-22}"
VPS_DIR="${VPS_DIR:-/opt/nutriapro}"

REGISTRY="${REGISTRY:-ghcr.io/wmsolutionsti}"

echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║           NutrIA-Pro — Deploy Backend VPS                 ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""
info "VPS: ${VPS_USER}@${VPS_HOST}:${VPS_PORT}"
info "Tag: ${TAG}"
echo ""

# =============================================================================
# Verificar conectividade com o VPS
# =============================================================================
info "Verificando conectividade com o VPS..."
if ! ssh -p "$VPS_PORT" -o ConnectTimeout=10 -o BatchMode=yes "${VPS_USER}@${VPS_HOST}" "echo ok" >/dev/null 2>&1; then
  error "Não foi possível conectar ao VPS. Verifique SSH e as variáveis de ambiente."
fi
success "Conexão SSH estabelecida."

# =============================================================================
# Deploy via SSH
# =============================================================================
info "Iniciando deploy..."

ssh -p "$VPS_PORT" "${VPS_USER}@${VPS_HOST}" bash -s -- "$VPS_DIR" "$TAG" "$REGISTRY" << 'REMOTE_SCRIPT'
  set -euo pipefail

  VPS_DIR="$1"
  TAG="$2"
  REGISTRY="$3"

  echo "📂 Navegando para $VPS_DIR..."
  cd "$VPS_DIR"

  echo "🔄 Atualizando código..."
  git pull origin main

  echo "📥 Pulling imagens com tag $TAG..."
  export TAG="$TAG"
  export REGISTRY="$REGISTRY"
  docker compose -f infra/docker-compose.prod.yml pull api worker

  echo "🚀 Atualizando serviços (zero downtime)..."
  docker compose -f infra/docker-compose.prod.yml up -d --no-deps --remove-orphans api worker

  echo "⏳ Aguardando API ficar saudável..."
  MAX_WAIT=60
  ELAPSED=0
  while [ $ELAPSED -lt $MAX_WAIT ]; do
    HEALTH=$(docker inspect --format='{{.State.Health.Status}}' nutriapro-api 2>/dev/null || echo "unknown")
    if [ "$HEALTH" = "healthy" ]; then
      break
    fi
    sleep 5
    ELAPSED=$((ELAPSED + 5))
  done

  if [ "$HEALTH" != "healthy" ]; then
    echo "❌ API não ficou saudável em ${MAX_WAIT}s. Logs:"
    docker compose -f infra/docker-compose.prod.yml logs --tail=50 api
    exit 1
  fi

  echo "🗃️ Aplicando migrations..."
  docker compose -f infra/docker-compose.prod.yml exec -T api alembic upgrade head

  echo "🧹 Limpando imagens antigas..."
  docker image prune -f

  echo "✅ Deploy concluído com sucesso!"
REMOTE_SCRIPT

success "Deploy concluído!"
echo ""
info "Verificando saúde da API em produção..."
sleep 5

API_URL="https://api.nutriapro.com/health"
if curl --silent --fail --retry 3 --retry-delay 5 "$API_URL" | grep -q '"status"'; then
  success "API respondendo em $API_URL"
else
  warn "Não foi possível verificar a saúde da API em $API_URL"
fi

echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║           ✅ Backend deployado com sucesso!              ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""
