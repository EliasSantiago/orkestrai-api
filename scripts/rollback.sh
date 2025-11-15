#!/bin/bash
# Script para fazer rollback para versão anterior da aplicação

set -e

echo "⏪ Orkestrai API - Rollback"
echo "==========================="
echo ""

# Cores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Verificar se há backup de imagem
if ! docker images | grep -q "orkestrai-api.*backup"; then
    echo -e "${RED}✗ Nenhuma imagem de backup encontrada!${NC}"
    echo ""
    echo "Para criar backup antes de deploy:"
    echo "  docker tag orkestrai-api:latest orkestrai-api:backup"
    exit 1
fi

echo -e "${YELLOW}Imagens disponíveis:${NC}"
docker images orkestrai-api --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"
echo ""

read -p "Tem certeza que deseja fazer rollback? [y/N]: " confirm
if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
    echo "Cancelado."
    exit 0
fi

echo ""
echo "1️⃣ Parando container atual..."
docker stop orkestrai-api || true
docker rm orkestrai-api || true

echo ""
echo "2️⃣ Fazendo rollback para imagem anterior..."
docker tag orkestrai-api:backup orkestrai-api:rollback
docker tag orkestrai-api:rollback orkestrai-api:latest

echo ""
echo "3️⃣ Iniciando aplicação com versão anterior..."
docker run -d \
    --name orkestrai-api \
    --network agents_network \
    --restart unless-stopped \
    -p 8001:8001 \
    --env-file .env \
    orkestrai-api:latest

echo ""
echo "4️⃣ Aguardando aplicação iniciar..."
sleep 10

echo ""
echo "5️⃣ Verificando status..."
if docker ps | grep -q orkestrai-api; then
    echo -e "${GREEN}✅ Rollback concluído com sucesso!${NC}"
    echo ""
    echo "Últimos logs:"
    docker logs --tail 20 orkestrai-api
    echo ""
    echo "Testar: curl http://localhost:8001/docs"
else
    echo -e "${RED}✗ Falha ao iniciar aplicação após rollback${NC}"
    docker logs orkestrai-api
    exit 1
fi

echo ""
echo "Para desfazer o rollback e voltar para a última versão:"
echo "  ./scripts/deploy_manual.sh"

