#!/bin/bash
# Script para configurar HTTPS com Nginx e Let's Encrypt
# Execute na máquina E2 após deploy básico funcionando

set -e

echo "🔒 Orkestrai API - Setup HTTPS"
echo "=============================="
echo ""

# Cores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Verificar se é root
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}✗ Este script precisa ser executado como root${NC}" 
   echo "Execute: sudo ./scripts/setup_https.sh"
   exit 1
fi

# Solicitar informações
echo -e "${YELLOW}Informações necessárias:${NC}"
read -p "Domínio (ex: api.orkestrai.com): " DOMAIN
read -p "Email para Let's Encrypt: " EMAIL
read -p "Usuário do sistema (para paths): " USERNAME

if [ -z "$DOMAIN" ] || [ -z "$EMAIL" ] || [ -z "$USERNAME" ]; then
    echo -e "${RED}✗ Todas as informações são obrigatórias!${NC}"
    exit 1
fi

echo ""
echo "Configurando HTTPS para:"
echo "  Domínio: $DOMAIN"
echo "  Email: $EMAIL"
echo "  Usuário: $USERNAME"
echo ""
read -p "Continuar? [y/N]: " confirm

if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
    echo "Cancelado."
    exit 0
fi

echo ""
echo "1️⃣ Instalando Nginx..."
apt-get update
apt-get install -y nginx

echo ""
echo "2️⃣ Instalando Certbot..."
apt-get install -y certbot python3-certbot-nginx

echo ""
echo "3️⃣ Configurando Nginx..."

# Criar diretório para certbot
mkdir -p /var/www/certbot

# Configuração temporária para obter certificado
cat > /etc/nginx/sites-available/orkestrai << EOF
server {
    listen 80;
    listen [::]:80;
    server_name $DOMAIN;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        proxy_pass http://localhost:8001;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Ativar configuração
ln -sf /etc/nginx/sites-available/orkestrai /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Testar configuração
nginx -t

# Recarregar Nginx
systemctl reload nginx

echo ""
echo "4️⃣ Obtendo certificado SSL..."
certbot --nginx -d $DOMAIN --non-interactive --agree-tos -m $EMAIL --redirect

echo ""
echo "5️⃣ Aplicando configuração completa do Nginx..."

# Configuração completa com HTTPS
cat > /etc/nginx/sites-available/orkestrai << EOF
upstream api_backend {
    server localhost:8001;
    keepalive 32;
}

server {
    listen 80;
    listen [::]:80;
    server_name $DOMAIN;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        return 301 https://\$server_name\$request_uri;
    }
}

server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name $DOMAIN;

    ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;
    ssl_trusted_certificate /etc/letsencrypt/live/$DOMAIN/chain.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    access_log /var/log/nginx/orkestrai_access.log;
    error_log /var/log/nginx/orkestrai_error.log;

    client_max_body_size 50M;

    location / {
        proxy_pass http://api_backend;
        proxy_http_version 1.1;
        
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_set_header X-Forwarded-Host \$host;
        proxy_set_header X-Forwarded-Port \$server_port;

        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }

    location /static/ {
        alias /home/$USERNAME/orkestrai-api/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
EOF

# Testar e recarregar
nginx -t
systemctl reload nginx

echo ""
echo "6️⃣ Configurando renovação automática..."

# Adicionar job ao cron para renovação automática
(crontab -l 2>/dev/null; echo "0 0,12 * * * certbot renew --quiet --post-hook 'systemctl reload nginx'") | crontab -

# Habilitar Nginx no boot
systemctl enable nginx

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ HTTPS configurado com sucesso!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Informações:"
echo "  🌐 URL: https://$DOMAIN"
echo "  📄 Docs: https://$DOMAIN/docs"
echo "  🔒 Certificado válido por 90 dias"
echo "  🔄 Renovação automática configurada"
echo ""
echo "Comandos úteis:"
echo "  - Status Nginx: systemctl status nginx"
echo "  - Recarregar: systemctl reload nginx"
echo "  - Testar config: nginx -t"
echo "  - Ver certificados: certbot certificates"
echo "  - Renovar manual: certbot renew"
echo ""
echo "Logs:"
echo "  - Nginx access: /var/log/nginx/orkestrai_access.log"
echo "  - Nginx error: /var/log/nginx/orkestrai_error.log"
echo ""
echo -e "${YELLOW}⚠️ IMPORTANTE:${NC}"
echo "  1. Certifique-se de que o DNS aponta para este servidor"
echo "  2. Firewall deve permitir portas 80 e 443"
echo "  3. Certificado renova automaticamente a cada 60 dias"

