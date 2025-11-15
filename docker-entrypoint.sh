#!/bin/bash
# Docker entrypoint - Cria tabelas apenas se não existirem (primeira vez)

set -e

echo "🚀 Orkestrai API - Iniciando"
echo "=============================="

# Criar tabelas apenas se não existirem (seguro)
if [ "$SKIP_DB_INIT" != "true" ]; then
    echo ""
    echo "📦 Verificando banco de dados..."
    
    # Verificar se tabelas já existem
    python3 << 'EOF'
import sys
from src.database import engine, test_connection
from sqlalchemy import inspect

try:
    if not test_connection():
        print("⚠️  PostgreSQL não está pronto ainda")
        sys.exit(1)
    
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    if len(tables) > 0:
        print(f"✓ Banco já inicializado ({len(tables)} tabelas)")
        sys.exit(0)
    else:
        print("→ Primeira vez: criando tabelas...")
        from src.database import Base
        Base.metadata.create_all(bind=engine)
        print("✓ Tabelas criadas com sucesso")
        sys.exit(0)
except Exception as e:
    print(f"⚠️  Erro ao verificar banco: {e}")
    sys.exit(1)
EOF
    
    if [ $? -eq 0 ]; then
        echo "✓ Banco de dados pronto"
    else
        echo "⚠️  Aviso: Problema ao inicializar banco"
        echo "   A aplicação tentará continuar..."
    fi
    echo ""
fi

# Iniciar aplicação
echo "🌐 Iniciando servidor API..."
echo ""

exec "$@"

