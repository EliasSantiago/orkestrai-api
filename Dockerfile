# Multi-stage build para otimizar o tamanho da imagem

# Stage 1: Builder
FROM python:3.11-slim as builder

WORKDIR /app

# Instalar dependências do sistema necessárias para build
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

WORKDIR /app

# Instalar apenas dependências runtime necessárias
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar dependências Python do builder para local do appuser
COPY --from=builder /root/.local /home/appuser/.local

# Adicionar PATH para binários do usuário
ENV PATH=/home/appuser/.local/bin:$PATH

# Copiar código da aplicação
COPY . .

# Criar usuário não-root primeiro
RUN useradd -m -u 1000 appuser

# Copiar entrypoint e dar permissão (fazer como root)
COPY docker-entrypoint.sh /app/docker-entrypoint.sh
RUN chmod +x /app/docker-entrypoint.sh

# Ajustar permissões
RUN chown -R appuser:appuser /app /home/appuser/.local

# Mudar para usuário não-root
USER appuser

# Expor porta da API
EXPOSE 8001

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8001/docs || exit 1

# Configurar entrypoint e comando
ENTRYPOINT ["/app/docker-entrypoint.sh"]
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8001", "--workers", "4"]

