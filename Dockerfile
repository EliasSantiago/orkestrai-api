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

# Instalar PyTorch CPU-only primeiro (para evitar downloads de CUDA)
RUN pip install --no-cache-dir --user \
    torch torchaudio --index-url https://download.pytorch.org/whl/cpu

# Copiar requirements e instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Instalar Whisper após PyTorch (para garantir que use a versão CPU)
RUN pip install --no-cache-dir --user "openai-whisper>=20231117"

# Stage 2: Runtime
FROM python:3.11-slim

WORKDIR /app

# Instalar dependências runtime necessárias
# Inclui: PostgreSQL, Tesseract OCR (com idiomas), FFmpeg, curl
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    tesseract-ocr \
    tesseract-ocr-por \
    tesseract-ocr-eng \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Criar usuário não-root antes de copiar arquivos
RUN useradd -m -u 1000 appuser

# Copiar dependências Python do builder para local do appuser
COPY --from=builder /root/.local /home/appuser/.local

# Adicionar PATH para binários do usuário
ENV PATH=/home/appuser/.local/bin:$PATH

# Copiar código da aplicação
COPY . .

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

