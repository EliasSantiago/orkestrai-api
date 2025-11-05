#!/bin/bash

# Script para executar o ADK em modo interativo
# IMPORTANTE: Agentes agora vêm do banco de dados, não da pasta /agents

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
echo "ADK Interactive Mode"
echo "=========================================="
echo ""
echo "⚠️  IMPORTANTE: Agentes agora vêm do banco de dados!"
echo ""
echo "Para usar agentes:"
echo "  1. Inicie o servidor ADK: ./start_adk_web.sh"
echo "  2. Acesse http://localhost:8000 no navegador"
echo ""
echo "Para criar agentes:"
echo "  1. Inicie a API: ./start_api.sh"
echo "  2. Acesse http://localhost:8001/docs"
echo "  3. Crie agentes via POST /api/agents"
echo ""
echo "Este modo interativo não está mais disponível."
echo "Use a interface web do ADK (./start_adk_web.sh) em vez disso."
echo "=========================================="
exit 1

