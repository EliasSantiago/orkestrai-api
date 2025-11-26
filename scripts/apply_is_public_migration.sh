#!/bin/bash
# Script para aplicar a migração is_public no servidor
# Execute este script diretamente no servidor

set -e

# Cores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🔧 Aplicando migração: add_is_public_to_agents${NC}"
echo "=========================================="
echo ""

# Detectar container da API
API_CONTAINER=$(docker ps --format '{{.Names}}' | grep -E 'orkestrai-api|api' | head -1)

if [ -z "$API_CONTAINER" ]; then
    echo -e "${RED}✗ Container da API não encontrado${NC}"
    echo ""
    echo "Containers disponíveis:"
    docker ps --format '{{.Names}}'
    exit 1
fi

echo -e "${GREEN}✓ Container encontrado: $API_CONTAINER${NC}"
echo ""

# Detectar container do Postgres
POSTGRES_CONTAINER=$(docker ps --format '{{.Names}}' | grep -E 'postgres' | head -1)

if [ -z "$POSTGRES_CONTAINER" ]; then
    echo -e "${RED}✗ Container do PostgreSQL não encontrado${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Container PostgreSQL: $POSTGRES_CONTAINER${NC}"
echo ""

# Aplicar migração SQL
echo -e "${YELLOW}📝 Aplicando migração SQL...${NC}"
echo ""

docker exec -i $POSTGRES_CONTAINER psql -U agentuser -d agentsdb << 'EOF'
-- Add is_public column to agents table
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name='agents' AND column_name='is_public'
    ) THEN
        ALTER TABLE agents 
        ADD COLUMN is_public BOOLEAN NOT NULL DEFAULT FALSE;
        
        RAISE NOTICE 'Column is_public added successfully';
    ELSE
        RAISE NOTICE 'Column is_public already exists';
    END IF;
END $$;

-- Create index for better query performance
CREATE INDEX IF NOT EXISTS idx_agents_is_public ON agents(is_public);

-- Display summary
SELECT 
    COUNT(*) as total_agents,
    SUM(CASE WHEN is_public THEN 1 ELSE 0 END) as public_agents,
    SUM(CASE WHEN NOT is_public THEN 1 ELSE 0 END) as private_agents
FROM agents;
EOF

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ Migração aplicada com sucesso!${NC}"
    echo ""
    
    # Reiniciar container da API para recarregar metadados
    echo -e "${YELLOW}🔄 Reiniciando container da API...${NC}"
    docker restart $API_CONTAINER
    
    echo ""
    echo -e "${GREEN}✅ Container reiniciado!${NC}"
    echo ""
    echo -e "${BLUE}A API estará disponível em alguns segundos...${NC}"
else
    echo ""
    echo -e "${RED}❌ Erro ao aplicar migração${NC}"
    exit 1
fi

echo ""
echo "=========================================="
echo -e "${GREEN}✅ Processo concluído!${NC}"
echo "=========================================="

