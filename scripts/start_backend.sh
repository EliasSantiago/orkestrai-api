#!/bin/bash

# Script para iniciar o backend (API FastAPI)
# Inicia serviços Docker, verifica banco de dados e inicia a API

# Navegar para o diretório raiz do projeto
cd "$(dirname "$0")/.."

# Verificar se o ambiente virtual existe
if [ ! -d ".venv" ]; then
    echo "✗ Ambiente virtual não encontrado!"
    echo "Execute primeiro: ./scripts/setup.sh"
    exit 1
fi

# Ativar ambiente virtual
source .venv/bin/activate

echo "=========================================="
echo "Iniciando Backend (API FastAPI)"
echo "=========================================="
echo ""

# Verificar e iniciar serviços Docker se necessário
if command -v docker &> /dev/null; then
    if command -v docker-compose &> /dev/null; then
        COMPOSE_CMD="docker-compose"
    elif docker compose version &> /dev/null; then
        COMPOSE_CMD="docker compose"
    else
        COMPOSE_CMD=""
    fi
    
    if [ -n "$COMPOSE_CMD" ] && [ -f "docker-compose.yml" ]; then
        echo "Verificando serviços Docker (PostgreSQL e Redis)..."
        # Verificar se os containers estão rodando
        RUNNING_CONTAINERS=$($COMPOSE_CMD ps -q 2>/dev/null | wc -l)
        if [ "$RUNNING_CONTAINERS" -eq 0 ]; then
            echo "Iniciando serviços Docker..."
            $COMPOSE_CMD up -d
            echo "Aguardando serviços iniciarem..."
            sleep 3
        else
            echo "✓ Serviços Docker já estão rodando"
        fi
    fi
fi

# Verificar conexão com banco de dados
echo ""
echo "Verificando banco de dados..."
python -c "from src.database import test_connection; exit(0 if test_connection() else 1)" 2>&1
DB_CONNECTION_STATUS=$?
if [ $DB_CONNECTION_STATUS -ne 0 ]; then
    echo "⚠ Aviso: Não foi possível conectar ao banco de dados"
    echo "  Tentando inicializar o banco de dados..."
    python src/init_db.py 2>&1
    INIT_STATUS=$?
    if [ $INIT_STATUS -ne 0 ]; then
        echo ""
        echo "✗ Erro ao inicializar banco de dados"
        echo ""
        echo "Possíveis causas:"
        echo "  1. PostgreSQL não está rodando"
        echo "  2. Configuração de conexão incorreta no .env"
        echo "  3. Erro de permissões no banco de dados"
        echo ""
        echo "Soluções:"
        echo "  - Verifique se os containers estão rodando:"
        echo "    docker ps"
        echo "  - Inicie os serviços se necessário:"
        echo "    docker-compose up -d"
        echo "  - Verifique a configuração DATABASE_URL no .env"
        echo ""
        exit 1
    fi
    echo "✓ Banco de dados inicializado"
else
    echo "✓ Conexão com banco de dados OK"
fi

echo ""
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

