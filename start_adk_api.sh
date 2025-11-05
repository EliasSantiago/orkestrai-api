#!/bin/bash

# Script para iniciar o servidor API do ADK
# IMPORTANTE: Agentes agora vêm do banco de dados

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
echo "⚠️  IMPORTANTE: Sistema Atualizado"
echo "=========================================="
echo ""
echo "Os agentes agora vêm do banco de dados PostgreSQL!"
echo ""
echo "Para usar agentes:"
echo "  ./start_adk_web.sh  (Interface Web ADK - http://localhost:8000)"
echo ""
echo "Para gerenciar agentes (criar/editar):"
echo "  ./start_api.sh  (API REST - http://localhost:8001/docs)"
echo ""
echo "Este script (start_adk_api.sh) não é mais necessário."
echo "Use ./start_adk_web.sh para a interface web do ADK."
echo "=========================================="
exit 1

