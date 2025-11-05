#!/bin/bash

# Script para iniciar a API FastAPI

cd "$(dirname "$0")"

# Verificar se o ambiente virtual existe
if [ ! -d ".venv" ]; then
    echo "✗ Ambiente virtual não encontrado!"
    echo "Execute primeiro: ./setup.sh"
    exit 1
fi

# Ativar ambiente virtual
source .venv/bin/activate

echo "=========================================="
echo "Iniciando API FastAPI"
echo "=========================================="
echo ""
echo "A API estará disponível em:"
echo "  - API: http://localhost:8001"
echo "  - Docs: http://localhost:8001/docs"
echo ""
echo "Pressione Ctrl+C para parar o servidor"
echo "=========================================="
echo ""

# Iniciar o servidor FastAPI
uvicorn src.api.main:app --host=0.0.0.0 --port=8001 --reload

