#!/bin/bash

# Script para iniciar a interface web do ADK com agentes do banco de dados

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
echo "Iniciando Interface Web do ADK"
echo "Carregando agentes do banco de dados"
echo "=========================================="
echo ""
echo "A interface web estará disponível em:"
echo "  - Web UI: http://localhost:8000"
echo ""
echo "Pressione Ctrl+C para parar o servidor"
echo "=========================================="
echo ""

# Verificar conexão com banco de dados
echo "Verificando banco de dados..."
python -c "from src.database import test_connection; exit(0 if test_connection() else 1)" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠ Aviso: Não foi possível conectar ao banco de dados"
    echo "  Certifique-se de que o PostgreSQL está rodando:"
    echo "    docker-compose up -d"
    echo ""
    read -p "Deseja continuar mesmo assim? (s/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Ss]$ ]]; then
        exit 1
    fi
fi

# Iniciar o servidor ADK customizado que carrega agentes do banco
python -m src.adk_server

