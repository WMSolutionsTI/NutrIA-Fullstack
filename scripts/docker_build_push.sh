#!/usr/bin/env bash
set -euo pipefail

IMAGE_NAME="yourdockerhubusername/nutria-backend"
IMAGE_TAG="$(git rev-parse --short HEAD)"

echo "Building Docker image ${IMAGE_NAME}:${IMAGE_TAG}..."
cd backend_python

docker build -t ${IMAGE_NAME}:${IMAGE_TAG} .

echo "Pushing Docker image to Docker Hub..."
docker push ${IMAGE_NAME}:${IMAGE_TAG}

echo "Optionally tag 'latest' and push"
docker tag ${IMAGE_NAME}:${IMAGE_TAG} ${IMAGE_NAME}:latest

docker push ${IMAGE_NAME}:latest

echo "Docker image published:
 - ${IMAGE_NAME}:${IMAGE_TAG}
 - ${IMAGE_NAME}:latest"
