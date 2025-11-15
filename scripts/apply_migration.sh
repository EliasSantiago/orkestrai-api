#!/bin/bash
# Script para aplicar migration SQL manualmente em produção
# USO: ./scripts/apply_migration.sh migrations/nome_da_migration.sql

set -e

echo "⚠️  Aplicar Migration SQL - MODO MANUAL"
echo "========================================"
echo ""

# Cores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Verificar argumentos
if [ $# -eq 0 ]; then
    echo -e "${RED}✗ Erro: Migration SQL não especificada${NC}"
    echo ""
    echo "Uso:"
    echo "  ./scripts/apply_migration.sh migrations/nome_da_migration.sql"
    echo ""
    echo "Migrations disponíveis:"
    ls -1 migrations/*.sql 2>/dev/null || echo "  Nenhuma migration encontrada"
    exit 1
fi

MIGRATION_FILE=$1

# Verificar se arquivo existe
if [ ! -f "$MIGRATION_FILE" ]; then
    echo -e "${RED}✗ Erro: Arquivo não encontrado: $MIGRATION_FILE${NC}"
    exit 1
fi

MIGRATION_NAME=$(basename "$MIGRATION_FILE")

echo -e "${YELLOW}⚠️  ATENÇÃO - AMBIENTE DE PRODUÇÃO${NC}"
echo ""
echo "Migration: $MIGRATION_NAME"
echo ""
echo -e "${YELLOW}Esta operação pode modificar dados em produção!${NC}"
echo ""

# Mostrar conteúdo da migration
echo "Conteúdo da migration:"
echo "----------------------------------------"
cat "$MIGRATION_FILE"
echo "----------------------------------------"
echo ""

# Confirmação 1
read -p "Você revisou o SQL acima? (sim/não): " confirm1
if [ "$confirm1" != "sim" ]; then
    echo "Cancelado."
    exit 0
fi

# Verificar se já foi aplicada
echo ""
echo "Verificando se já foi aplicada..."
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
        """), {"name": "$MIGRATION_NAME"})
        count = result.scalar()
        print(count)
except Exception as e:
    print("ERROR")
EOF
)

if [ "$APPLIED" = "ERROR" ]; then
    echo -e "${RED}✗ Erro ao verificar banco de dados${NC}"
    exit 1
fi

if [ "$APPLIED" != "0" ]; then
    echo -e "${YELLOW}⚠️  Migration já foi aplicada anteriormente${NC}"
    echo ""
    read -p "Deseja reaplicar mesmo assim? (PERIGOSO) (sim/não): " confirm_reapply
    if [ "$confirm_reapply" != "sim" ]; then
        echo "Cancelado."
        exit 0
    fi
fi

# Confirmação 2 - Fazer backup
echo ""
echo -e "${YELLOW}📦 RECOMENDADO: Fazer backup antes${NC}"
read -p "Deseja fazer backup do banco agora? (sim/não): " do_backup
if [ "$do_backup" = "sim" ]; then
    echo "Fazendo backup..."
    bash scripts/backup_db.sh || echo "⚠️ Backup falhou, mas continuando..."
fi

# Confirmação 3 - Final
echo ""
echo -e "${RED}⚠️  ÚLTIMA CONFIRMAÇÃO${NC}"
echo ""
read -p "Digite 'APLICAR' para confirmar: " final_confirm
if [ "$final_confirm" != "APLICAR" ]; then
    echo "Cancelado."
    exit 0
fi

# Aplicar migration
echo ""
echo "Aplicando migration..."

python3 << EOF
from src.database import engine
from sqlalchemy import text

try:
    with open("$MIGRATION_FILE", "r") as f:
        sql = f.read()
    
    with engine.connect() as conn:
        # Executar migration
        print("Executando SQL...")
        conn.execute(text(sql))
        
        # Registrar como aplicada (se não foi reaplicação)
        if $APPLIED == 0:
            conn.execute(text("""
                INSERT INTO schema_migrations (migration_name) 
                VALUES (:name)
            """), {"name": "$MIGRATION_NAME"})
        
        conn.commit()
    
    print("✓ Migration aplicada com sucesso!")
except Exception as e:
    print(f"✗ ERRO ao aplicar migration: {e}")
    print("\nO banco pode estar em estado inconsistente!")
    print("Verifique manualmente e considere restaurar backup.")
    exit(1)
EOF

if [ $? -eq 0 ]; then
    echo ""
    echo "========================================"
    echo -e "${GREEN}✅ Migration aplicada com sucesso!${NC}"
    echo "========================================"
    echo ""
    echo "Verificar:"
    echo "  docker exec -it agents_postgres psql -U agentuser -d agentsdb"
else
    echo ""
    echo "========================================"
    echo -e "${RED}❌ ERRO ao aplicar migration${NC}"
    echo "========================================"
    echo ""
    echo "Ações:"
    echo "  1. Verificar logs acima"
    echo "  2. Verificar estado do banco"
    echo "  3. Considerar restaurar backup"
    exit 1
fi

