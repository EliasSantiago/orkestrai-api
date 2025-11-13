#!/bin/bash

# Script para expor a API via ngrok

echo "=========================================="
echo "🌐 Expondo API via Ngrok"
echo "=========================================="
echo ""

# Verificar se ngrok está instalado
if ! command -v ngrok &> /dev/null; then
    echo "❌ Ngrok não está instalado!"
    echo ""
    echo "Instale o ngrok:"
    echo "  sudo snap install ngrok"
    echo ""
    echo "Ou baixe em: https://ngrok.com/download"
    exit 1
fi

# Verificar se API está rodando
if ! curl -s http://localhost:8001/health > /dev/null 2>&1; then
    echo "❌ API não está rodando em localhost:8001"
    echo ""
    echo "Inicie a API primeiro:"
    echo "  ./scripts/start_backend.sh"
    echo ""
    exit 1
fi

echo "✓ API está rodando"
echo ""
echo "Iniciando ngrok..."
echo ""
echo "=========================================="
echo "📝 Instruções:"
echo "=========================================="
echo ""
echo "1. Copie a URL gerada (ex: https://abc123.ngrok.io)"
echo "2. No LobeChat, configure:"
echo "   Base URL: https://abc123.ngrok.io/v1"
echo "   API Key: your-api-key-here"
echo ""
echo "3. Pressione Ctrl+C para parar o ngrok"
echo ""
echo "=========================================="
echo ""

# Iniciar ngrok
ngrok http 8001

