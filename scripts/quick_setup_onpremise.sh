#!/bin/bash

# Quick Setup Script for On-Premise Agents
# Usage: ./scripts/quick_setup_onpremise.sh

set -e

echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║  🚀 SETUP RÁPIDO: AGENTES ON-PREMISE                              ║"
echo "╚════════════════════════════════════════════════════════════════════╝"

# Check if jq is installed
if ! command -v jq &> /dev/null; then
    echo "❌ Erro: 'jq' não está instalado"
    echo "   Instale com: sudo apt-get install jq"
    exit 1
fi

# Configuration
API_BASE_URL="http://localhost:8001"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Login
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  📝 PASSO 1: LOGIN"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
read -p "📧 Email: " email
read -sp "🔒 Senha: " password
echo ""
echo ""

echo "🔐 Autenticando..."
token_response=$(curl -s -X POST "$API_BASE_URL/api/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$email\",\"password\":\"$password\"}")

access_token=$(echo "$token_response" | jq -r '.access_token')

if [ "$access_token" == "null" ] || [ -z "$access_token" ]; then
    echo -e "${RED}❌ Erro no login${NC}"
    echo "$token_response" | jq .
    exit 1
fi

echo -e "${GREEN}✅ Login bem-sucedido!${NC}"

# Step 2: Choose model
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🤖 PASSO 2: CONFIGURAR AGENTE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Modelos sugeridos:"
echo "  • gpt-oss:20b"
echo "  • llama-2:7b"
echo "  • onpremise-custom:latest"
echo "  • local-model:version"
echo ""
read -p "🎯 Nome do modelo on-premise: " model_name

if [ -z "$model_name" ]; then
    echo -e "${RED}❌ Nome do modelo não pode ser vazio${NC}"
    exit 1
fi

echo ""
read -p "📝 Nome do agente (ou Enter para usar padrão): " agent_name

if [ -z "$agent_name" ]; then
    agent_name="Assistente $model_name"
fi

# Step 3: Choose tools
echo ""
echo "Ferramentas disponíveis:"
echo "  1. Nenhuma"
echo "  2. calculator"
echo "  3. time"
echo "  4. calculator + time"
echo "  5. web_search"
echo "  6. calculator + time + web_search"
echo ""
read -p "🛠️  Escolha as ferramentas (1-6): " tools_choice

case "$tools_choice" in
    1)
        tools_json="[]"
        ;;
    2)
        tools_json='["calculator"]'
        ;;
    3)
        tools_json='["time"]'
        ;;
    4)
        tools_json='["calculator", "time"]'
        ;;
    5)
        tools_json='["web_search"]'
        ;;
    6)
        tools_json='["calculator", "time", "web_search"]'
        ;;
    *)
        tools_json="[]"
        ;;
esac

# Step 4: Create agent
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🔨 PASSO 3: CRIAR AGENTE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Criando agente..."

agent_response=$(curl -s -X POST "$API_BASE_URL/api/agents" \
  -H "Authorization: Bearer $access_token" \
  -H "Content-Type: application/json" \
  -d "{
    \"name\": \"$agent_name\",
    \"description\": \"Agente usando modelo on-premise $model_name\",
    \"model\": \"$model_name\",
    \"instruction\": \"Você é um assistente útil que responde em português do Brasil. Seja claro, objetivo e sempre educado.\",
    \"tools\": $tools_json
  }")

agent_id=$(echo "$agent_response" | jq -r '.id')

if [ "$agent_id" == "null" ] || [ -z "$agent_id" ]; then
    echo -e "${RED}❌ Erro ao criar agente${NC}"
    echo "$agent_response" | jq .
    exit 1
fi

echo -e "${GREEN}✅ Agente criado com sucesso!${NC}"
echo ""
echo "Detalhes do agente:"
echo "$agent_response" | jq '{id, name, model, tools}'

# Step 5: Test agent
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  💬 PASSO 4: TESTAR AGENTE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
read -p "Deseja testar o agente agora? (s/N): " test_choice

if [[ "$test_choice" =~ ^[Ss]$ ]]; then
    echo ""
    read -p "💬 Digite sua mensagem: " user_message
    
    if [ -z "$user_message" ]; then
        user_message="Olá! Você está funcionando? Responda brevemente."
    fi
    
    echo ""
    echo "Enviando mensagem..."
    echo ""
    
    curl -X POST "$API_BASE_URL/api/agents/$agent_id/chat" \
      -H "Authorization: Bearer $access_token" \
      -H "Content-Type: application/json" \
      -d "{
        \"message\": \"$user_message\",
        \"session_id\": \"quick-setup-test\"
      }"
    
    echo ""
fi

# Summary
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ✅ SETUP COMPLETO!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${GREEN}Seu agente está pronto para uso!${NC}"
echo ""
echo "📋 Informações do agente:"
echo "  • ID: $agent_id"
echo "  • Nome: $agent_name"
echo "  • Modelo: $model_name"
echo "  • Ferramentas: $tools_json"
echo ""
echo "💡 Próximos passos:"
echo "  1. Teste via API:"
echo "     curl -X POST http://localhost:8001/api/agents/$agent_id/chat \\"
echo "       -H 'Authorization: Bearer $access_token' \\"
echo "       -H 'Content-Type: application/json' \\"
echo "       -d '{\"message\":\"Sua mensagem\",\"session_id\":\"test\"}'"
echo ""
echo "  2. Teste via interface web:"
echo "     Acesse: http://localhost:8000"
echo ""
echo "  3. Liste seus agentes:"
echo "     curl -X GET http://localhost:8001/api/agents \\"
echo "       -H 'Authorization: Bearer $access_token'"
echo ""
echo "📚 Documentação: docs/ONPREMISE_CREATE_AGENTS_EXAMPLES.md"
echo ""

