#!/bin/bash
# Script de deploy manual para a máquina E2
# Use este script para fazer deploy manual sem GitHub Actions

set -e

echo "🚀 Orkestrai API - Deploy Manual"
echo "================================="

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Verificar se está na máquina de destino ou local
read -p "Executando na máquina E2 (servidor)? [y/N]: " is_server

if [[ "$is_server" =~ ^[Yy]$ ]]; then
    echo -e "${GREEN}✓ Executando deploy no servidor${NC}"
    
    # Verificar se .env existe
    if [ ! -f .env ]; then
        echo -e "${RED}✗ Arquivo .env não encontrado!${NC}"
        echo "Crie o arquivo .env com as configurações necessárias."
        echo "Você pode copiar do .env.example: cp .env.example .env"
        exit 1
    fi
    
    # Parar aplicação antiga
    echo "Parando aplicação antiga..."
    docker stop orkestrai-api 2>/dev/null || true
    docker rm orkestrai-api 2>/dev/null || true
    
    # Iniciar/verificar serviços de infraestrutura
    echo "Verificando serviços de infraestrutura..."
    docker compose up -d postgres redis
    
    # Aguardar PostgreSQL
    echo "Aguardando PostgreSQL ficar pronto..."
    sleep 10
    
    # Build da imagem
    echo "Construindo imagem Docker..."
    docker build -t orkestrai-api:latest .
    
    # Executar migrações
    echo "Executando migrações do banco..."
    docker run --rm \
        --network agents_network \
        --env-file .env \
        orkestrai-api:latest \
        python -c "from src.init_db import init_database; init_database()" || echo "Migration skipped"
    
    # Iniciar aplicação
    echo "Iniciando aplicação..."
    docker run -d \
        --name orkestrai-api \
        --network agents_network \
        --restart unless-stopped \
        -p 8001:8001 \
        --env-file .env \
        orkestrai-api:latest
    
    # Aguardar aplicação iniciar
    echo "Aguardando aplicação iniciar..."
    sleep 15
    
    # Verificar status
    if docker ps | grep -q orkestrai-api; then
        echo -e "${GREEN}✓ Deploy concluído com sucesso!${NC}"
        echo ""
        echo "Ver logs: docker logs -f orkestrai-api"
        echo "Status: docker ps | grep orkestrai-api"
        echo "API Docs: http://localhost:8001/docs"
        
        # Mostrar últimos logs
        echo ""
        echo "Últimos logs:"
        docker logs --tail 20 orkestrai-api
    else
        echo -e "${RED}✗ Falha ao iniciar aplicação${NC}"
        docker logs orkestrai-api
        exit 1
    fi
    
else
    # Deploy remoto
    read -p "IP da máquina E2: " server_ip
    read -p "Usuário SSH: " ssh_user
    
    echo -e "${YELLOW}Fazendo deploy para $ssh_user@$server_ip${NC}"
    
    # Criar tarball do projeto
    echo "Criando pacote..."
    tar -czf /tmp/orkestrai-api.tar.gz \
        --exclude='.git' \
        --exclude='__pycache__' \
        --exclude='.env' \
        --exclude='*.pyc' \
        --exclude='venv' \
        --exclude='chat-ui' \
        .
    
    # Transferir para servidor
    echo "Transferindo arquivos..."
    scp /tmp/orkestrai-api.tar.gz $ssh_user@$server_ip:~/orkestrai-api.tar.gz
    
    # Executar deploy remoto
    echo "Executando deploy remoto..."
    ssh $ssh_user@$server_ip << 'ENDSSH'
        set -e
        mkdir -p ~/orkestrai-api
        cd ~/orkestrai-api
        tar -xzf ~/orkestrai-api.tar.gz
        rm ~/orkestrai-api.tar.gz
        
        # Executar deploy
        bash scripts/deploy_manual.sh <<< "y"
ENDSSH
    
    # Limpar arquivo local
    rm /tmp/orkestrai-api.tar.gz
    
    echo -e "${GREEN}✓ Deploy remoto concluído!${NC}"
    echo "Acesse: http://$server_ip:8001/docs"
fi

