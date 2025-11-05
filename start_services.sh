#!/bin/bash

# Script para iniciar todos os serviços (PostgreSQL e Redis)

cd "$(dirname "$0")"

echo "=========================================="
echo "Iniciando Serviços"
echo "=========================================="
echo ""

# Verificar se Docker está instalado
if ! command -v docker &> /dev/null; then
    echo "✗ Docker não está instalado!"
    exit 1
fi

# Verificar se docker-compose está disponível
if command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
elif docker compose version &> /dev/null; then
    COMPOSE_CMD="docker compose"
else
    echo "✗ docker-compose não está disponível!"
    exit 1
fi

echo "Iniciando PostgreSQL e Redis..."
$COMPOSE_CMD up -d

echo ""
echo "Aguardando serviços iniciarem..."
sleep 3

# Verificar status
echo ""
echo "Status dos serviços:"
$COMPOSE_CMD ps

echo ""
echo "=========================================="
echo "✓ Serviços iniciados!"
echo ""
echo "PostgreSQL: localhost:5432"
echo "Redis: localhost:6379"
echo "=========================================="

