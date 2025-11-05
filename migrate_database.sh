#!/bin/bash

# Script para migrar o banco de dados (username -> name)

cd "$(dirname "$0")"

# Verificar se o ambiente virtual existe
if [ ! -d ".venv" ]; then
    echo "✗ Ambiente virtual não encontrado!"
    echo "Execute primeiro: ./setup.sh"
    exit 1
fi

# Ativar ambiente virtual
source .venv/bin/activate

# Executar migração
python -m src.migrate_username_to_name

