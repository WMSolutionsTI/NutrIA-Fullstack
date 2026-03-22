# =============================================================================
# NutrIA-Pro — API Dockerfile
# =============================================================================
# Build multi-stage para imagem de produção otimizada.
#
# Stages:
#   builder  → instala dependências Python
#   runtime  → imagem final mínima para produção
# =============================================================================

# ---------------------------------------------------------------------------
# Stage 1: Builder — instala dependências
# ---------------------------------------------------------------------------
FROM python:3.12-slim AS builder

WORKDIR /app

# Instala dependências de sistema necessárias para compilação
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copia e instala dependências Python (camada separada para cache eficiente)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# ---------------------------------------------------------------------------
# Stage 2: Runtime — imagem final otimizada
# ---------------------------------------------------------------------------
FROM python:3.12-slim AS runtime

WORKDIR /app

# Instala apenas o necessário para runtime (curl para healthcheck)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    tesseract-ocr \
    tesseract-ocr-por \
    && rm -rf /var/lib/apt/lists/*

# Copia dependências instaladas do builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copia código da aplicação
COPY . .

# Usuário não-root para segurança
RUN useradd --no-create-home --shell /bin/false appuser
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Produção: sem --reload
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
