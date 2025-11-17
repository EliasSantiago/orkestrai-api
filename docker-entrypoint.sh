#!/bin/bash
# Docker entrypoint - Cria tabelas apenas se não existirem (primeira vez)

set -e

echo "🚀 Orkestrai API - Iniciando"
echo "=============================="
echo ""

# Iniciar aplicação
echo "🌐 Iniciando servidor API..."
echo ""

exec "$@"
