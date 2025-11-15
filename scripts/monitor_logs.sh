#!/bin/bash
# Script para monitorar logs em tempo real de todos os serviços

echo "📊 Orkestrai API - Monitor de Logs"
echo "==================================="
echo ""

# Cores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PS3=$'\nEscolha uma opção: '
options=(
    "API - Logs em tempo real"
    "API - Últimas 50 linhas"
    "API - Buscar erro específico"
    "PostgreSQL - Logs"
    "Redis - Logs"
    "Todos os serviços - Logs combinados"
    "Nginx - Access log (se configurado)"
    "Nginx - Error log (se configurado)"
    "Ver estatísticas de acesso"
    "Sair"
)

while true; do
    echo ""
    select opt in "${options[@]}"
    do
        case $opt in
            "API - Logs em tempo real")
                echo -e "${BLUE}Monitorando logs da API em tempo real (Ctrl+C para sair)...${NC}"
                docker logs -f orkestrai-api
                break
                ;;
            "API - Últimas 50 linhas")
                echo -e "${BLUE}Últimas 50 linhas:${NC}"
                docker logs --tail 50 orkestrai-api
                break
                ;;
            "API - Buscar erro específico")
                read -p "Digite o termo para buscar: " search_term
                echo -e "${BLUE}Buscando '$search_term' nos logs:${NC}"
                docker logs orkestrai-api 2>&1 | grep -i "$search_term" | tail -20
                break
                ;;
            "PostgreSQL - Logs")
                echo -e "${BLUE}Logs do PostgreSQL:${NC}"
                docker logs --tail 50 agents_postgres
                break
                ;;
            "Redis - Logs")
                echo -e "${BLUE}Logs do Redis:${NC}"
                docker logs --tail 50 agents_redis
                break
                ;;
            "Todos os serviços - Logs combinados")
                echo -e "${BLUE}Logs de todos os serviços (Ctrl+C para sair):${NC}"
                docker-compose logs -f
                break
                ;;
            "Nginx - Access log (se configurado)")
                if [ -f /var/log/nginx/orkestrai_access.log ]; then
                    echo -e "${BLUE}Últimas 50 requisições:${NC}"
                    sudo tail -50 /var/log/nginx/orkestrai_access.log
                else
                    echo -e "${RED}Nginx não configurado ou log não encontrado${NC}"
                fi
                break
                ;;
            "Nginx - Error log (se configurado)")
                if [ -f /var/log/nginx/orkestrai_error.log ]; then
                    echo -e "${BLUE}Últimos erros do Nginx:${NC}"
                    sudo tail -50 /var/log/nginx/orkestrai_error.log
                else
                    echo -e "${RED}Nginx não configurado ou log não encontrado${NC}"
                fi
                break
                ;;
            "Ver estatísticas de acesso")
                echo -e "${BLUE}Estatísticas de acesso (últimas 1000 linhas):${NC}"
                echo ""
                if [ -f /var/log/nginx/orkestrai_access.log ]; then
                    echo "Top 10 IPs:"
                    sudo tail -1000 /var/log/nginx/orkestrai_access.log | awk '{print $1}' | sort | uniq -c | sort -rn | head -10
                    echo ""
                    echo "Top 10 endpoints:"
                    sudo tail -1000 /var/log/nginx/orkestrai_access.log | awk '{print $7}' | sort | uniq -c | sort -rn | head -10
                    echo ""
                    echo "Códigos de status:"
                    sudo tail -1000 /var/log/nginx/orkestrai_access.log | awk '{print $9}' | sort | uniq -c | sort -rn
                else
                    echo "Análise de logs Docker da API:"
                    docker logs --tail 1000 orkestrai-api 2>&1 | grep -E "GET|POST|PUT|DELETE|PATCH" | head -20
                fi
                break
                ;;
            "Sair")
                echo "Até logo!"
                exit 0
                ;;
            *) 
                echo -e "${RED}Opção inválida${NC}"
                break
                ;;
        esac
    done
done

