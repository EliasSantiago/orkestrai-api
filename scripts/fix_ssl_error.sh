#!/bin/bash

# ==============================================
# Script de Correção Rápida - Erro SSL
# ==============================================
#
# Este script corrige o erro:
# "SSL: CERTIFICATE_VERIFY_FAILED"
#
# O que ele faz:
# 1. Verifica se o arquivo .env existe
# 2. Adiciona/atualiza a variável VERIFY_SSL=false
# 3. Mostra instruções de como reiniciar o servidor
#

set -e

echo "=========================================="
echo "🔧 Correção de Erro SSL"
echo "=========================================="
echo ""

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Caminho para o arquivo .env
ENV_FILE=".env"

# Verificar se .env existe
if [ ! -f "$ENV_FILE" ]; then
    echo -e "${RED}❌ Erro: Arquivo .env não encontrado!${NC}"
    echo ""
    echo "Crie um arquivo .env na raiz do projeto com o seguinte conteúdo:"
    echo ""
    echo "# LiteLLM Configuration"
    echo "LITELLM_ENABLED=true"
    echo "VERIFY_SSL=false"
    echo ""
    echo "# API Keys"
    echo "GOOGLE_API_KEY=your_key_here"
    echo "OPENAI_API_KEY=your_key_here"
    echo ""
    exit 1
fi

echo "✓ Arquivo .env encontrado"
echo ""

# Fazer backup do .env
BACKUP_FILE=".env.backup.$(date +%Y%m%d_%H%M%S)"
cp "$ENV_FILE" "$BACKUP_FILE"
echo -e "${GREEN}✓ Backup criado: $BACKUP_FILE${NC}"
echo ""

# Verificar se VERIFY_SSL já existe
if grep -q "^VERIFY_SSL=" "$ENV_FILE"; then
    # Atualizar valor existente
    echo "Atualizando VERIFY_SSL existente..."
    
    # Usar sed diferente no macOS vs Linux
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' 's/^VERIFY_SSL=.*/VERIFY_SSL=false/' "$ENV_FILE"
    else
        sed -i 's/^VERIFY_SSL=.*/VERIFY_SSL=false/' "$ENV_FILE"
    fi
    
    echo -e "${GREEN}✓ VERIFY_SSL atualizado para 'false'${NC}"
else
    # Adicionar nova variável
    echo "Adicionando VERIFY_SSL ao .env..."
    
    # Adicionar com comentário
    cat >> "$ENV_FILE" << 'EOF'

# SSL/TLS Configuration (added by fix_ssl_error.sh)
# WARNING: Only disable SSL verification in development environments!
VERIFY_SSL=false
EOF
    
    echo -e "${GREEN}✓ VERIFY_SSL=false adicionado ao .env${NC}"
fi

echo ""
echo "=========================================="
echo -e "${GREEN}✅ Correção aplicada com sucesso!${NC}"
echo "=========================================="
echo ""
echo -e "${YELLOW}⚠️  IMPORTANTE:${NC}"
echo "   SSL verification está agora DESABILITADO."
echo "   Isto é seguro para desenvolvimento, mas NÃO use em produção!"
echo ""
echo "=========================================="
echo "📝 Próximos passos:"
echo "=========================================="
echo ""
echo "1. Reinicie o servidor:"
echo "   ./scripts/start_backend.sh"
echo ""
echo "2. Verifique os logs. Você deve ver:"
echo "   '⚠️  SSL verification is DISABLED'"
echo ""
echo "3. Teste seu chat novamente"
echo ""
echo "=========================================="
echo "📚 Documentação:"
echo "=========================================="
echo ""
echo "- Guia completo: docs/arquitetura/litellm/SSL_FIX_GUIDE.md"
echo "- Troubleshooting: docs/arquitetura/litellm/TROUBLESHOOTING.md"
echo ""
echo "=========================================="
echo ""

