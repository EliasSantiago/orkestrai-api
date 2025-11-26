#!/bin/bash
# Docker entrypoint - Executa migrations e inicia a aplicação

set -e

echo "🚀 Orkestrai API - Iniciando"
echo "=============================="
echo ""

# Executar migrations
if [ -f "/app/scripts/migrate_database.sh" ]; then
    echo "📦 Executando migrations..."
    bash /app/scripts/migrate_database.sh
    
    if [ $? -eq 0 ]; then
        echo "✅ Migrations concluídas com sucesso"
        echo ""
    else
        echo "❌ Erro ao executar migrations"
        exit 1
    fi
else
    echo "⚠️  Script de migrations não encontrado"
    echo ""
fi

# Executar migrations Python específicas (sistema de tokens)
echo "🔧 Verificando migrations Python específicas..."
if [ -f "/app/scripts/run_token_migrations.sh" ]; then
    bash /app/scripts/run_token_migrations.sh
    echo ""
fi

# Iniciar aplicação
echo "🌐 Iniciando servidor API..."
echo ""

exec "$@"
