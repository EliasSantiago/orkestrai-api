#!/bin/bash

# Script para obter JWT token para usar no LobeChat

echo "=========================================="
echo "🔑 Obter JWT Token para LobeChat"
echo "=========================================="
echo ""

# Solicitar credenciais
read -p "Email: " EMAIL
read -sp "Senha: " PASSWORD
echo ""
echo ""

# Fazer login
echo "Fazendo login..."
RESPONSE=$(curl -s -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"$EMAIL\",
    \"password\": \"$PASSWORD\"
  }")

# Verificar se houve erro
if echo "$RESPONSE" | grep -q "detail"; then
    echo "❌ Erro ao fazer login:"
    echo "$RESPONSE" | jq '.'
    exit 1
fi

# Extrair token
TOKEN=$(echo $RESPONSE | jq -r '.access_token')

if [ "$TOKEN" == "null" ] || [ -z "$TOKEN" ]; then
    echo "❌ Não foi possível obter o token"
    echo "$RESPONSE"
    exit 1
fi

echo "✅ Login realizado com sucesso!"
echo ""
echo "=========================================="
echo "📋 Token JWT:"
echo "=========================================="
echo ""
echo "$TOKEN"
echo ""
echo "=========================================="
echo "🐳 Configure no docker-compose.yml:"
echo "=========================================="
echo ""
echo "environment:"
echo "  OPENAI_API_KEY: \"$TOKEN\""
echo "  OPENAI_PROXY_URL: \"http://host.docker.internal:8001/v1\""
echo ""
echo "=========================================="
echo "🧪 Testar token:"
echo "=========================================="
echo ""
echo "curl -X GET http://localhost:8001/v1/models \\"
echo "  -H \"Authorization: Bearer $TOKEN\""
echo ""
echo "=========================================="
echo ""
echo "⚠️  IMPORTANTE: Este token expira em 30 dias."
echo "    Renove periodicamente executando este script novamente."
echo ""

