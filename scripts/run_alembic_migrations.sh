#!/bin/bash
# Script para executar migrations Alembic
# Este script é executado durante o deploy para aplicar todas as migrations pendentes

set -e

echo "🔄 Executando Migrations Alembic"
echo "=================================="
echo ""

# Cores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Verificar se está rodando via Docker ou local
if [ -f "/.dockerenv" ]; then
    echo "📦 Executando dentro do container Docker"
    export PYTHONPATH=/app:${PYTHONPATH:-}
else
    echo "💻 Executando localmente"
    # Carregar .env se existir
    if [ -f .env ]; then
        export $(cat .env | grep -v '^#' | xargs)
    fi
    export PYTHONPATH=.:${PYTHONPATH:-}
fi

# Aguardar PostgreSQL estar pronto
echo "⏳ Aguardando PostgreSQL..."
MAX_TRIES=30
TRIES=0
LAST_ERROR=""

while [ $TRIES -lt $MAX_TRIES ]; do
    # Tentar conectar ao banco
    ERROR_OUTPUT=$(python3 -c "
import sys
sys.path.insert(0, '/app' if '/.dockerenv' in open('/.dockerenv').read() else '.')
try:
    from src.database import test_connection
    if test_connection():
        sys.exit(0)
    else:
        sys.exit(1)
except Exception as e:
    print(f'Error: {e}', file=sys.stderr)
    sys.exit(1)
" 2>&1)
    EXIT_CODE=$?
    
    if [ $EXIT_CODE -eq 0 ]; then
        echo -e "${GREEN}✓ PostgreSQL pronto!${NC}"
        break
    else
        LAST_ERROR="$ERROR_OUTPUT"
        TRIES=$((TRIES + 1))
        echo "  Tentativa $TRIES/$MAX_TRIES..."
        if [ $TRIES -lt $MAX_TRIES ]; then
            sleep 2
        fi
    fi
done

if [ $TRIES -eq $MAX_TRIES ]; then
    echo -e "${RED}✗ Timeout: PostgreSQL não respondeu após ${MAX_TRIES} tentativas${NC}"
    echo -e "${RED}Último erro:${NC}"
    echo "$LAST_ERROR"
    exit 1
fi

echo ""
echo "📊 Verificando status das migrations..."
echo "----------------------------------------"

# Mostrar status atual
if [ -f "/.dockerenv" ]; then
    cd /app
else
    cd "$(dirname "$0")/.."
fi

# Verificar versão atual
CURRENT_REV=$(alembic current 2>&1 | tail -1 | grep -oP '^\w+' || echo "none")
if [ "$CURRENT_REV" = "none" ]; then
    CURRENT_REV=$(alembic current 2>&1 | grep "Current revision" | awk '{print $3}' || echo "none")
fi
echo "  Versão atual: ${CURRENT_REV:-none}"

# Mostrar migrations pendentes
echo ""
echo "📋 Migrations disponíveis:"
alembic heads 2>&1 | tail -5 || echo "  Verificando..."

echo ""
echo "🚀 Aplicando migrations..."
echo "-------------------------"

# Aplicar todas as migrations pendentes
if alembic upgrade head; then
    echo ""
    echo -e "${GREEN}✅ Todas as migrations aplicadas com sucesso!${NC}"
    
    # Mostrar versão atual após migrations
    echo ""
    echo "📊 Status final:"
    alembic current
else
    echo ""
    echo -e "${RED}✗ Erro ao aplicar migrations${NC}"
    exit 1
fi

echo ""
echo "=================================="
echo -e "${GREEN}✅ Migrations concluídas!${NC}"

