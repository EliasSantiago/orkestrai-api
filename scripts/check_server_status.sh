#!/bin/bash
# Script para verificar status dos serviços na máquina E2

echo "🔍 Orkestrai API - Status dos Serviços"
echo "======================================"
echo ""

# Cores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Verificar containers
echo "📦 Containers em execução:"
echo "-------------------------"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "orkestrai-api|agents_postgres|agents_redis|NAMES"
echo ""

# Status de cada serviço
echo "🔧 Status dos Serviços:"
echo "----------------------"

# PostgreSQL
if docker ps | grep -q agents_postgres; then
    if docker exec agents_postgres pg_isready -q; then
        echo -e "${GREEN}✓ PostgreSQL: Rodando e saudável${NC}"
    else
        echo -e "${YELLOW}⚠ PostgreSQL: Rodando mas não responde${NC}"
    fi
else
    echo -e "${RED}✗ PostgreSQL: Parado${NC}"
fi

# Redis
if docker ps | grep -q agents_redis; then
    if docker exec agents_redis redis-cli ping 2>/dev/null | grep -q PONG; then
        echo -e "${GREEN}✓ Redis: Rodando e saudável${NC}"
    else
        echo -e "${YELLOW}⚠ Redis: Rodando mas não responde${NC}"
    fi
else
    echo -e "${RED}✗ Redis: Parado${NC}"
fi

# API
if docker ps | grep -q orkestrai-api; then
    http_code=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8001/docs 2>/dev/null || echo "000")
    if [ "$http_code" = "200" ]; then
        echo -e "${GREEN}✓ API: Rodando e respondendo (HTTP $http_code)${NC}"
    else
        echo -e "${YELLOW}⚠ API: Rodando mas não responde corretamente (HTTP $http_code)${NC}"
    fi
else
    echo -e "${RED}✗ API: Parada${NC}"
fi

echo ""

# Uso de recursos
echo "💾 Uso de Recursos:"
echo "------------------"
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}" | grep -E "orkestrai-api|agents_postgres|agents_redis|NAME"
echo ""

# Espaço em disco
echo "💿 Espaço em Disco:"
echo "------------------"
df -h / | tail -1 | awk '{print "Usado: "$3" / "$2" ("$5")"}'
echo ""

# Docker disk usage
echo "🐳 Uso de Disco Docker:"
echo "----------------------"
docker system df
echo ""

# Últimos logs
echo "📋 Últimos Logs da API:"
echo "----------------------"
if docker ps | grep -q orkestrai-api; then
    docker logs --tail 10 orkestrai-api 2>&1
else
    echo "API não está rodando"
fi

echo ""
echo "=================================="
echo "Para ver logs em tempo real: docker logs -f orkestrai-api"
echo "Para reiniciar serviços: docker compose restart"
echo "Para parar tudo: docker compose down && docker stop orkestrai-api"

