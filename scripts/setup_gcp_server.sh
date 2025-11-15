#!/bin/bash
# Script para configurar uma máquina E2 nova no Google Cloud
# Execute este script na máquina E2 após criar a instância

set -e

echo "🔧 Orkestrai API - Setup do Servidor GCP E2"
echo "==========================================="
echo ""

# Cores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Verificar se é root
if [[ $EUID -eq 0 ]]; then
   echo -e "${RED}✗ Este script não deve ser executado como root${NC}" 
   echo "Execute como usuário normal: ./scripts/setup_gcp_server.sh"
   exit 1
fi

echo -e "${YELLOW}Este script vai:${NC}"
echo "  1. Atualizar o sistema"
echo "  2. Instalar Docker e Docker Compose"
echo "  3. Configurar firewall (UFW)"
echo "  4. Criar diretórios necessários"
echo "  5. Configurar swap (se necessário)"
echo ""
read -p "Continuar? [y/N]: " confirm

if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
    echo "Cancelado."
    exit 0
fi

echo ""
echo "1️⃣ Atualizando sistema..."
sudo apt-get update
sudo apt-get upgrade -y

echo ""
echo "2️⃣ Instalando Docker..."
# Remover versões antigas
sudo apt-get remove -y docker docker-engine docker.io containerd runc 2>/dev/null || true

# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
rm get-docker.sh

# Adicionar usuário ao grupo docker
sudo usermod -aG docker $USER

# Instalar Docker Compose
sudo apt-get install -y docker-compose-plugin

echo -e "${GREEN}✓ Docker instalado com sucesso${NC}"

echo ""
echo "3️⃣ Configurando firewall (UFW)..."
sudo apt-get install -y ufw

# Configurar regras
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 8001/tcp  # API
sudo ufw --force enable

echo -e "${GREEN}✓ Firewall configurado${NC}"

echo ""
echo "4️⃣ Criando diretórios..."
mkdir -p ~/orkestrai-api
mkdir -p ~/orkestrai-api/backups
mkdir -p ~/orkestrai-api/logs

echo ""
echo "5️⃣ Verificando swap..."
if free | awk '/^Swap:/ {exit !$2}'; then
    echo -e "${GREEN}✓ Swap já configurado${NC}"
else
    echo "Criando arquivo de swap de 2GB..."
    sudo fallocate -l 2G /swapfile
    sudo chmod 600 /swapfile
    sudo mkswap /swapfile
    sudo swapon /swapfile
    echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
    echo -e "${GREEN}✓ Swap criado${NC}"
fi

echo ""
echo "6️⃣ Instalando utilitários..."
sudo apt-get install -y \
    curl \
    wget \
    git \
    htop \
    ncdu \
    net-tools \
    vim

echo ""
echo "7️⃣ Otimizando configurações do sistema..."
# Aumentar limites de arquivos abertos
sudo tee -a /etc/security/limits.conf > /dev/null <<EOF
* soft nofile 65536
* hard nofile 65536
EOF

# Otimizar parâmetros do kernel
sudo tee -a /etc/sysctl.conf > /dev/null <<EOF
# Network optimizations
net.core.somaxconn = 1024
net.ipv4.tcp_max_syn_backlog = 2048
net.ipv4.ip_local_port_range = 1024 65535

# File system
fs.file-max = 65536
EOF

sudo sysctl -p

echo ""
echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}✓ Setup concluído com sucesso!${NC}"
echo -e "${GREEN}=========================================${NC}"
echo ""
echo -e "${YELLOW}⚠️ IMPORTANTE:${NC}"
echo "  1. FAÇA LOGOUT E LOGIN novamente para aplicar grupo docker"
echo "  2. Configure o firewall no Google Cloud Console:"
echo "     - Vá em VPC Network > Firewall"
echo "     - Crie regra: allow-orkestrai-api"
echo "     - Protocolo: TCP"
echo "     - Porta: 8001"
echo ""
echo "Próximos passos:"
echo "  1. Faça logout: exit"
echo "  2. Faça login novamente via SSH"
echo "  3. Verifique Docker: docker --version"
echo "  4. Clone o projeto no diretório ~/orkestrai-api"
echo "  5. Configure o arquivo .env"
echo "  6. Execute o deploy"
echo ""
echo "Configuração atual do servidor:"
echo "  - Docker: $(docker --version 2>/dev/null || echo 'Faça relogin')"
echo "  - Compose: $(docker compose version 2>/dev/null || echo 'Faça relogin')"
echo "  - Memória: $(free -h | awk '/^Mem:/ {print $2}')"
echo "  - Disco: $(df -h / | tail -1 | awk '{print $4}') livres"
echo "  - IP: $(hostname -I | awk '{print $1}')"

