#!/bin/bash
# Script para executar migrations no servidor remoto via SSH
# Uso: ./scripts/run_migrations_remote.sh [usuario] [caminho_chave_ssh]

set -e

# Cores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configurações
SERVER_IP="34.42.168.19"
SSH_USER="${1:-ignitor_online}"
SSH_KEY="${2:-~/.ssh/id_rsa}"

echo -e "${BLUE}🚀 Executando Migrations no Servidor Remoto${NC}"
echo "=========================================="
echo ""
echo "Servidor: $SERVER_IP"
echo "Usuário: $SSH_USER"
echo "Chave SSH: $SSH_KEY"
echo ""

# Verificar se chave existe
if [ ! -f "$SSH_KEY" ]; then
    echo -e "${RED}✗ Chave SSH não encontrada: $SSH_KEY${NC}"
    echo ""
    echo "Uso:"
    echo "  $0 [usuario] [caminho_chave_ssh]"
    echo ""
    echo "Exemplo:"
    echo "  $0 ignitor_online ~/.ssh/gcp_deploy_key"
    exit 1
fi

echo -e "${YELLOW}1️⃣ Verificando containers Docker...${NC}"
echo "----------------------------------------"

# Ver containers
ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$SSH_USER@$SERVER_IP" << 'EOF'
    echo "Containers em execução:"
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    echo ""
EOF

if [ $? -ne 0 ]; then
    echo -e "${RED}✗ Erro ao conectar no servidor${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}2️⃣ Localizando container da API...${NC}"
echo "----------------------------------------"

# Encontrar container da API
API_CONTAINER=$(ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$SSH_USER@$SERVER_IP" \
    "docker ps --format '{{.Names}}' | grep -E 'orkestrai-api|api' | head -1")

if [ -z "$API_CONTAINER" ]; then
    echo -e "${RED}✗ Container da API não encontrado${NC}"
    echo ""
    echo "Containers disponíveis:"
    ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$SSH_USER@$SERVER_IP" \
        "docker ps --format '{{.Names}}'"
    exit 1
fi

echo -e "${GREEN}✓ Container encontrado: $API_CONTAINER${NC}"
echo ""

echo -e "${YELLOW}3️⃣ Verificando se script de migrations existe...${NC}"
echo "----------------------------------------"

# Verificar se script existe no container
ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$SSH_USER@$SERVER_IP" \
    "docker exec $API_CONTAINER test -f /app/scripts/migrate_database.sh"

if [ $? -ne 0 ]; then
    echo -e "${YELLOW}⚠️  Script não encontrado no container, tentando caminho alternativo...${NC}"
    # Tentar executar diretamente via Python
    echo ""
    echo -e "${YELLOW}4️⃣ Executando migrations via Python...${NC}"
    echo "----------------------------------------"
    
    ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$SSH_USER@$SERVER_IP" << EOF
        docker exec $API_CONTAINER bash -c "
            cd /app && \
            python3 src/init_db.py && \
            echo '' && \
            echo 'Aplicando migrations SQL...' && \
            for migration in migrations/*.sql; do
                if [ -f \"\$migration\" ]; then
                    filename=\$(basename \"\$migration\")
                    echo \"  Verificando: \$filename\"
                    python3 << PYEOF
from src.database import engine
from sqlalchemy import text

try:
    with engine.connect() as conn:
        # Criar tabela de controle se não existir
        conn.execute(text('''
            CREATE TABLE IF NOT EXISTS schema_migrations (
                id SERIAL PRIMARY KEY,
                migration_name VARCHAR(255) UNIQUE NOT NULL,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        '''))
        conn.commit()
        
        # Verificar se já foi aplicada
        result = conn.execute(text('''
            SELECT COUNT(*) FROM schema_migrations 
            WHERE migration_name = :name
        '''), {\"name\": \"\$filename\"})
        count = result.scalar()
        
        if count == 0:
            # Aplicar migration
            with open(\"\$migration\", \"r\") as f:
                sql = f.read()
            conn.execute(text(sql))
            conn.execute(text('''
                INSERT INTO schema_migrations (migration_name) 
                VALUES (:name)
            '''), {\"name\": \"\$filename\"})
            conn.commit()
            print(f\"  ✓ Aplicada: \$filename\")
        else:
            print(f\"  ⊘ Já aplicada: \$filename\")
except Exception as e:
    print(f\"  ✗ Erro: {e}\")
    exit(1)
PYEOF
                fi
            done
        "
EOF
else
    echo -e "${GREEN}✓ Script encontrado${NC}"
    echo ""
    echo -e "${YELLOW}4️⃣ Executando script de migrations...${NC}"
    echo "----------------------------------------"
    
    # Executar script de migrations
    ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$SSH_USER@$SERVER_IP" \
        "docker exec $API_CONTAINER bash /app/scripts/migrate_database.sh"
fi

if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo -e "${GREEN}✅ Migrations executadas com sucesso!${NC}"
    echo "=========================================="
    echo ""
    echo -e "${BLUE}Verificar migrations aplicadas:${NC}"
    echo "  ssh -i $SSH_KEY $SSH_USER@$SERVER_IP"
    echo "  docker exec -it $API_CONTAINER bash"
    echo "  docker exec agents_postgres psql -U agentuser -d agentsdb -c \"SELECT * FROM schema_migrations;\""
else
    echo ""
    echo "=========================================="
    echo -e "${RED}❌ Erro ao executar migrations${NC}"
    echo "=========================================="
    exit 1
fi

