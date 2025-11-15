#!/bin/bash

# Script para gerar senhas seguras para o arquivo .env

echo "🔐 Gerando senhas seguras para produção..."
echo ""

# Função para gerar senha segura
generate_password() {
    # Gera uma senha de 32 caracteres com mix de caracteres
    openssl rand -base64 24 | tr -d "=+/" | cut -c1-32
}

POSTGRES_PASSWORD=$(generate_password)
REDIS_PASSWORD=$(generate_password)

echo "📝 Senhas geradas:"
echo ""
echo "POSTGRES_PASSWORD=$POSTGRES_PASSWORD"
echo "REDIS_PASSWORD=$REDIS_PASSWORD"
echo ""
echo "⚠️  IMPORTANTE: Copie essas senhas para seu arquivo .env"
echo "   Execute: cp .env.example .env"
echo "   Depois edite o .env e substitua as senhas acima"
echo ""
echo "💡 Dica: Você pode executar este script e redirecionar para o .env:"
echo "   ./generate-passwords.sh | grep -E '^(POSTGRES|REDIS)_PASSWORD=' >> .env"

