#!/bin/bash
# Script para criar tabelas e aplicar migrações SQL

set -e

echo "🔄 Migrações do Banco de Dados"
echo "==============================="
echo ""

# Cores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Verificar se está rodando via Docker ou local
if [ -f "/.dockerenv" ]; then
    echo "📦 Executando dentro do container Docker"
    DB_HOST=${POSTGRES_HOST:-postgres}
else
    echo "💻 Executando localmente"
    # Carregar .env se existir
    if [ -f .env ]; then
        export $(cat .env | grep -v '^#' | xargs)
    fi
fi

# Aguardar PostgreSQL estar pronto
echo "⏳ Aguardando PostgreSQL..."
MAX_TRIES=30
TRIES=0

while [ $TRIES -lt $MAX_TRIES ]; do
    if python3 -c "from src.database import test_connection; exit(0 if test_connection() else 1)" 2>/dev/null; then
        echo -e "${GREEN}✓ PostgreSQL pronto!${NC}"
        break
    fi
    TRIES=$((TRIES + 1))
    echo "  Tentativa $TRIES/$MAX_TRIES..."
    sleep 2
done

if [ $TRIES -eq $MAX_TRIES ]; then
    echo -e "${RED}✗ Timeout: PostgreSQL não respondeu${NC}"
    exit 1
fi

echo ""
echo "1️⃣ Criando tabelas via SQLAlchemy ORM..."
echo "----------------------------------------"

# Executar init_db para criar tabelas via SQLAlchemy
python3 src/init_db.py

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Tabelas criadas com sucesso${NC}"
else
    echo -e "${RED}✗ Erro ao criar tabelas${NC}"
    exit 1
fi

echo ""
echo "2️⃣ Aplicando migrações SQL adicionais..."
echo "----------------------------------------"

# Verificar se há migrations SQL para aplicar
if [ -d "migrations" ] && [ "$(ls -A migrations/*.sql 2>/dev/null)" ]; then
    for migration in migrations/*.sql; do
        if [ -f "$migration" ]; then
            filename=$(basename "$migration")
            echo "  Aplicando: $filename"
            
            # Verificar se migration já foi aplicada
            APPLIED=$(python3 << EOF
from src.database import engine
from sqlalchemy import text

try:
    with engine.connect() as conn:
        # Criar tabela de controle se não existir
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                id SERIAL PRIMARY KEY,
                migration_name VARCHAR(255) UNIQUE NOT NULL,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        conn.commit()
        
        # Verificar se já foi aplicada
        result = conn.execute(text("""
            SELECT COUNT(*) FROM schema_migrations 
            WHERE migration_name = :name
        """), {"name": "$filename"})
        count = result.scalar()
        print(count)
except Exception as e:
    print(f"Error: {e}")
    exit(1)
EOF
            )
            
            if [ "$APPLIED" = "0" ]; then
                # Aplicar migration
                python3 << EOF
from src.database import engine
from sqlalchemy import text

try:
    with open("$migration", "r") as f:
        sql = f.read()
    
    with engine.connect() as conn:
        # Executar migration
        conn.execute(text(sql))
        
        # Registrar como aplicada
        conn.execute(text("""
            INSERT INTO schema_migrations (migration_name) 
            VALUES (:name)
        """), {"name": "$filename"})
        
        conn.commit()
    print("✓ Migration aplicada: $filename")
except Exception as e:
    print(f"✗ Erro ao aplicar migration: {e}")
    exit(1)
EOF
                
                if [ $? -eq 0 ]; then
                    echo -e "    ${GREEN}✓ Aplicada${NC}"
                else
                    echo -e "    ${RED}✗ Erro${NC}"
                    exit 1
                fi
            else
                echo -e "    ${YELLOW}⊘ Já aplicada (pulando)${NC}"
            fi
        fi
    done
    echo -e "${GREEN}✓ Todas as migrações SQL aplicadas${NC}"
else
    echo "  Nenhuma migration SQL encontrada"
fi

echo ""
echo "3️⃣ Verificando integridade do banco..."
echo "----------------------------------------"

# Listar tabelas criadas
python3 << 'EOF'
from src.database import engine
from sqlalchemy import text, inspect

try:
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    print(f"  Total de tabelas: {len(tables)}")
    print("")
    print("  Tabelas criadas:")
    for table in sorted(tables):
        # Contar registros
        with engine.connect() as conn:
            result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
            count = result.scalar()
        print(f"    ✓ {table:30} ({count} registros)")
    
    print("")
    print("✓ Banco de dados íntegro")
except Exception as e:
    print(f"✗ Erro ao verificar banco: {e}")
    exit(1)
EOF

if [ $? -eq 0 ]; then
    echo ""
    echo "==============================="
    echo -e "${GREEN}✅ Migrações concluídas com sucesso!${NC}"
    echo "==============================="
else
    echo -e "${RED}✗ Erro na verificação${NC}"
    exit 1
fi

