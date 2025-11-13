#!/bin/bash

###############################################################################
# Script: Renovar Token JWT do LobeChat
# Descrição: Obtém novo token JWT e atualiza o docker-compose do LobeChat
# Autor: Sistema de Integração LobeChat
# Data: 2025-11-12
###############################################################################

set -e  # Sair se qualquer comando falhar

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configurações
API_URL="${API_URL:-http://localhost:8001}"
DOCKER_COMPOSE_FILE="${DOCKER_COMPOSE_FILE:-/home/vdilinux/aplicações/api-adk-google-main/chat-ui/docker-compose.lobechat.yml}"

echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}  Renovação de Token JWT - LobeChat  ${NC}"
echo -e "${BLUE}======================================${NC}"
echo ""

# 1. Solicitar credenciais
echo -e "${YELLOW}📝 Insira suas credenciais:${NC}"
read -p "Email: " EMAIL
read -sp "Senha: " PASSWORD
echo ""
echo ""

# 2. Fazer login e obter token
echo -e "${BLUE}🔐 Fazendo login na API...${NC}"
RESPONSE=$(curl -s -X POST "${API_URL}/api/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"${EMAIL}\",\"password\":\"${PASSWORD}\"}")

# Verificar se login foi bem-sucedido
if echo "$RESPONSE" | grep -q "access_token"; then
  TOKEN=$(echo "$RESPONSE" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
  echo -e "${GREEN}✓ Login bem-sucedido!${NC}"
  echo -e "${GREEN}✓ Token obtido: ${TOKEN:0:50}...${NC}"
else
  echo -e "${RED}✗ Erro ao fazer login!${NC}"
  echo -e "${RED}Resposta da API: $RESPONSE${NC}"
  exit 1
fi

# 3. Verificar se arquivo docker-compose existe
if [ ! -f "$DOCKER_COMPOSE_FILE" ]; then
  echo -e "${RED}✗ Arquivo docker-compose não encontrado: $DOCKER_COMPOSE_FILE${NC}"
  exit 1
fi

# 4. Fazer backup do arquivo original
BACKUP_FILE="${DOCKER_COMPOSE_FILE}.backup.$(date +%Y%m%d_%H%M%S)"
echo -e "${BLUE}💾 Criando backup em: $BACKUP_FILE${NC}"
cp "$DOCKER_COMPOSE_FILE" "$BACKUP_FILE"

# 5. Atualizar o token no arquivo
echo -e "${BLUE}📝 Atualizando token no docker-compose...${NC}"
sed -i "s|OPENAI_API_KEY:.*|OPENAI_API_KEY: \"$TOKEN\"|" "$DOCKER_COMPOSE_FILE"

if [ $? -eq 0 ]; then
  echo -e "${GREEN}✓ Token atualizado com sucesso!${NC}"
else
  echo -e "${RED}✗ Erro ao atualizar token!${NC}"
  echo -e "${YELLOW}Restaurando backup...${NC}"
  cp "$BACKUP_FILE" "$DOCKER_COMPOSE_FILE"
  exit 1
fi

# 6. Perguntar se deseja reiniciar o LobeChat
echo ""
read -p "🔄 Deseja reiniciar o LobeChat agora? (s/N): " RESTART
if [[ "$RESTART" =~ ^[Ss]$ ]]; then
  echo -e "${BLUE}🔄 Reiniciando LobeChat...${NC}"
  
  # Parar o LobeChat
  docker-compose -f "$DOCKER_COMPOSE_FILE" down
  
  # Iniciar o LobeChat com novo token
  docker-compose -f "$DOCKER_COMPOSE_FILE" up -d
  
  echo -e "${GREEN}✓ LobeChat reiniciado com sucesso!${NC}"
  echo -e "${GREEN}✓ Acesse em: http://localhost:3210${NC}"
else
  echo -e "${YELLOW}⚠️  Lembre-se de reiniciar o LobeChat manualmente:${NC}"
  echo -e "${YELLOW}   docker-compose -f $DOCKER_COMPOSE_FILE down${NC}"
  echo -e "${YELLOW}   docker-compose -f $DOCKER_COMPOSE_FILE up -d${NC}"
fi

echo ""
echo -e "${GREEN}======================================${NC}"
echo -e "${GREEN}  ✓ Processo concluído com sucesso!  ${NC}"
echo -e "${GREEN}======================================${NC}"
echo ""
echo -e "${BLUE}📋 Informações:${NC}"
echo -e "  • Backup criado em: ${BACKUP_FILE}"
echo -e "  • Token expira em aproximadamente 30 dias"
echo -e "  • Execute este script novamente quando o token expirar"
echo ""

