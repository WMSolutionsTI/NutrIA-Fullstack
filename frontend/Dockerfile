# =============================================================================
# NutrIA-Pro — Frontend Dockerfile (Desenvolvimento Local)
# =============================================================================
# Este Dockerfile é usado apenas para desenvolvimento local via docker-compose.
# Em produção, o frontend é deployado diretamente na Vercel via Git push.
# =============================================================================

FROM node:20-alpine

WORKDIR /app

# Instala dependências primeiro (melhor cache de layers)
COPY package*.json ./
RUN npm ci

# Copia o restante do código
COPY . .

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD wget --spider -q http://localhost:3000 || exit 1

CMD ["npm", "run", "dev"]
