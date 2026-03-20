#!/usr/bin/env bash
set -euo pipefail

# Exemplo de deploy via Docker Swarm na VPS
# Assuma que Docker e Docker Swarm já estejam instalados

STACK_NAME="nutria"
IMAGE_NAME="yourdockerhubusername/nutria-backend"
IMAGE_TAG="$(git rev-parse --short HEAD)"

# se não estiver em swarm
if ! docker info --format '{{.Swarm.LocalNodeState}}' | grep -q "active"; then
    echo "Inicializando Swarm..."
    docker swarm init
fi

# rede overlay
if ! docker network ls --filter name=nutria_overlay --format '{{.Name}}' | grep -q "nutria_overlay"; then
    docker network create --driver overlay nutria_overlay
fi

# Cria stack (crie arquivo docker-stack.yml no root)
docker stack deploy -c docker-stack.yml ${STACK_NAME}

docker service ls
