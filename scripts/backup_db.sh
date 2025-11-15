#!/bin/bash
# Script para fazer backup do banco de dados PostgreSQL

set -e

# Cores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "💾 Orkestrai API - Backup do Banco de Dados"
echo "==========================================="
echo ""

# Carregar variáveis de ambiente
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
else
    echo -e "${RED}✗ Arquivo .env não encontrado!${NC}"
    exit 1
fi

# Diretório de backups
BACKUP_DIR="./backups"
mkdir -p $BACKUP_DIR

# Nome do arquivo com timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/orkestrai_backup_$TIMESTAMP.sql"

echo "Criando backup do banco de dados..."
echo "Arquivo: $BACKUP_FILE"
echo ""

# Fazer backup
docker exec agents_postgres pg_dump \
    -U ${POSTGRES_USER:-agentuser} \
    -d ${POSTGRES_DB:-agentsdb} \
    --clean \
    --if-exists \
    --create \
    > "$BACKUP_FILE"

# Comprimir
echo "Comprimindo backup..."
gzip "$BACKUP_FILE"
BACKUP_FILE="$BACKUP_FILE.gz"

# Verificar tamanho
SIZE=$(du -h "$BACKUP_FILE" | cut -f1)

echo ""
echo -e "${GREEN}✓ Backup criado com sucesso!${NC}"
echo "Arquivo: $BACKUP_FILE"
echo "Tamanho: $SIZE"
echo ""

# Manter apenas últimos 7 backups
echo "Limpando backups antigos (mantendo últimos 7)..."
cd $BACKUP_DIR
ls -t orkestrai_backup_*.sql.gz | tail -n +8 | xargs -r rm
echo ""

# Listar backups disponíveis
echo "📋 Backups disponíveis:"
echo "----------------------"
ls -lh orkestrai_backup_*.sql.gz 2>/dev/null || echo "Nenhum backup encontrado"
echo ""

echo "Para restaurar um backup use:"
echo "  gunzip -c $BACKUP_FILE | docker exec -i agents_postgres psql -U \${POSTGRES_USER} -d \${POSTGRES_DB}"

