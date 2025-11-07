#!/bin/bash

# Script para iniciar a interface web do ADK
# Inicia serviços Docker, verifica banco de dados e inicia o servidor web

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
echo "Iniciando Interface Web do ADK"
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
python -c "from src.database import test_connection; exit(0 if test_connection() else 1)" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠ Aviso: Não foi possível conectar ao banco de dados"
    echo "  Tentando inicializar o banco de dados..."
    python src/init_db.py 2>/dev/null
    if [ $? -ne 0 ]; then
        echo "✗ Erro ao inicializar banco de dados"
        echo "  Certifique-se de que o PostgreSQL está rodando:"
        echo "    docker-compose up -d"
        echo ""
        read -p "Deseja continuar mesmo assim? (s/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Ss]$ ]]; then
            exit 1
        fi
    else
        echo "✓ Banco de dados inicializado"
    fi
else
    echo "✓ Conexão com banco de dados OK"
fi

echo ""
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

# Iniciar o servidor ADK customizado que carrega agentes do banco
python -m src.adk_server

