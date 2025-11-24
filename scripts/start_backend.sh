#!/bin/bash
# Script para iniciar o backend em modo desenvolvimento (Python local)

set -e

# Cores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Obter diretório do script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Mudar para o diretório raiz do projeto
cd "$PROJECT_ROOT"

echo "🚀 Orkestrai API - Iniciando Backend (Modo Desenvolvimento)"
echo "============================================================"
echo ""

# Verificar se o arquivo .env existe
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  Arquivo .env não encontrado${NC}"
    echo "   Criando a partir do template..."
    if [ -f "env.template" ]; then
        cp env.template .env
        echo -e "${YELLOW}   Por favor, edite o arquivo .env com suas configurações antes de continuar${NC}"
        echo ""
        read -p "Pressione Enter após editar o .env ou Ctrl+C para cancelar..."
    else
        echo -e "${RED}✗ Arquivo env.template não encontrado${NC}"
        exit 1
    fi
fi

# Verificar se o ambiente virtual existe
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}⚠️  Ambiente virtual não encontrado${NC}"
    echo "   Criando ambiente virtual..."
    python3 -m venv .venv
    echo -e "${GREEN}✓ Ambiente virtual criado${NC}"
fi

# Ativar ambiente virtual
echo "🔧 Ativando ambiente virtual..."
source .venv/bin/activate

# Verificar se as dependências estão instaladas
if ! python3 -c "import fastapi" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  Dependências não encontradas${NC}"
    echo "   Instalando dependências..."
    pip install --upgrade pip
    pip install -r requirements.txt
    echo -e "${GREEN}✓ Dependências instaladas${NC}"
else
    echo -e "${GREEN}✓ Dependências já instaladas${NC}"
fi

echo ""

# Carregar variáveis do .env usando python-dotenv (mais seguro e confiável)
# python-dotenv já está nas dependências do projeto e trata corretamente valores com espaços
if [ -f ".env" ]; then
    # Carregar .env usando Python dotenv e exportar variáveis para o shell
    # Isso evita problemas com valores que contêm espaços ou caracteres especiais
    eval "$(python3 << 'PYEOF'
try:
    from dotenv import dotenv_values
    env_vars = dotenv_values('.env')
    for key, value in env_vars.items():
        if value is not None and key:
            # Escapar valores para shell (substituir ' por '\'')
            value_escaped = str(value).replace("'", "'\\''")
            print(f"export {key}='{value_escaped}'")
except ImportError:
    # Se python-dotenv não estiver disponível, usar fallback simples
    import re
    with open('.env', 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            # Extrair chave e valor
            match = re.match(r'^([^=]+)=(.*)$', line)
            if match:
                key = match.group(1).strip()
                value = match.group(2).strip()
                # Remover aspas externas
                if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
                    value = value[1:-1]
                value_escaped = value.replace("'", "'\\''")
                print(f"export {key}='{value_escaped}'")
except Exception as e:
    print(f"# Erro ao carregar .env: {e}", file=__import__('sys').stderr)
PYEOF
    )"
fi

# Verificar e iniciar containers Docker se necessário
POSTGRES_RUNNING=false
REDIS_RUNNING=false

# Detectar qual comando docker compose usar (moderno: docker compose ou antigo: docker-compose)
DOCKER_COMPOSE_CMD=""
if docker compose version >/dev/null 2>&1; then
    DOCKER_COMPOSE_CMD="docker compose"
elif command -v docker-compose >/dev/null 2>&1; then
    DOCKER_COMPOSE_CMD="docker-compose"
fi

if command -v docker &> /dev/null && [ -n "$DOCKER_COMPOSE_CMD" ]; then
    # Verificar se os containers estão rodando
    if docker ps | grep -q agents_postgres; then
        echo -e "${GREEN}✓ PostgreSQL (Docker) está rodando${NC}"
        POSTGRES_RUNNING=true
    else
        echo -e "${YELLOW}⚠️  PostgreSQL (Docker) não está rodando${NC}"
        echo "   Iniciando containers Docker..."
        
        # Iniciar apenas postgres e redis (não a API)
        cd "$PROJECT_ROOT"
        $DOCKER_COMPOSE_CMD up -d postgres redis
        
        if [ $? -eq 0 ]; then
            echo -e "${BLUE}⏳ Aguardando PostgreSQL e Redis ficarem prontos...${NC}"
            
            # Aguardar PostgreSQL ficar pronto (máximo 60 segundos)
            MAX_WAIT=60
            WAITED=0
            while [ $WAITED -lt $MAX_WAIT ]; do
                if docker exec agents_postgres pg_isready -U "${POSTGRES_USER:-agentuser}" -d "${POSTGRES_DB:-agentsdb}" >/dev/null 2>&1; then
                    echo -e "${GREEN}✓ PostgreSQL está pronto${NC}"
                    POSTGRES_RUNNING=true
                    break
                fi
                sleep 2
                WAITED=$((WAITED + 2))
                echo -n "."
            done
            echo ""
            
            if [ "$POSTGRES_RUNNING" = false ]; then
                echo -e "${RED}✗ Timeout aguardando PostgreSQL ficar pronto${NC}"
                echo "   Verifique os logs: docker logs agents_postgres"
            fi
            
            # Aguardar Redis ficar pronto (máximo 30 segundos)
            WAITED=0
            while [ $WAITED -lt 30 ]; do
                # Tentar ping com senha se disponível
                if [ -n "$REDIS_PASSWORD" ]; then
                    if docker exec agents_redis redis-cli -a "$REDIS_PASSWORD" ping >/dev/null 2>&1; then
                        echo -e "${GREEN}✓ Redis está pronto${NC}"
                        REDIS_RUNNING=true
                        break
                    fi
                else
                    if docker exec agents_redis redis-cli ping >/dev/null 2>&1; then
                        echo -e "${GREEN}✓ Redis está pronto${NC}"
                        REDIS_RUNNING=true
                        break
                    fi
                fi
                sleep 1
                WAITED=$((WAITED + 1))
                echo -n "."
            done
            echo ""
            
            if [ "$REDIS_RUNNING" = false ]; then
                echo -e "${YELLOW}⚠️  Redis pode não estar pronto ainda${NC}"
            fi
        else
            echo -e "${RED}✗ Erro ao iniciar containers Docker${NC}"
            echo "   Verifique se o docker-compose.yml está configurado corretamente"
        fi
    fi
    
    # Verificar Redis (se ainda não foi verificado)
    if [ "$REDIS_RUNNING" = false ]; then
        if docker ps | grep -q agents_redis; then
            # Verificar se Redis está respondendo (com senha se disponível)
            if [ -n "$REDIS_PASSWORD" ]; then
                if docker exec agents_redis redis-cli -a "$REDIS_PASSWORD" ping >/dev/null 2>&1; then
                    echo -e "${GREEN}✓ Redis (Docker) está rodando${NC}"
                    REDIS_RUNNING=true
                else
                    echo -e "${YELLOW}⚠️  Redis (Docker) está rodando mas não está respondendo${NC}"
                fi
            else
                if docker exec agents_redis redis-cli ping >/dev/null 2>&1; then
                    echo -e "${GREEN}✓ Redis (Docker) está rodando${NC}"
                    REDIS_RUNNING=true
                else
                    echo -e "${YELLOW}⚠️  Redis (Docker) está rodando mas não está respondendo${NC}"
                fi
            fi
        fi
    fi
elif ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}⚠️  Docker não está instalado ou não está no PATH${NC}"
    echo "   Os containers não serão iniciados automaticamente"
elif [ -z "$DOCKER_COMPOSE_CMD" ]; then
    echo -e "${YELLOW}⚠️  docker compose não está disponível${NC}"
    echo "   Os containers não serão iniciados automaticamente"
    echo "   Instale Docker Compose ou use: docker-compose"
fi

echo ""

# Ajustar DATABASE_URL para desenvolvimento local
# Quando rodando localmente em Python, sempre usar "localhost" porque Docker expõe portas para o host
# O hostname "postgres" só funciona dentro da rede Docker
if [ -n "$DATABASE_URL" ]; then
    if echo "$DATABASE_URL" | grep -q "@postgres:"; then
        # Sempre trocar "postgres" por "localhost" quando rodando localmente
        # (Docker expõe portas para o host, então localhost funciona)
        export DATABASE_URL=$(echo "$DATABASE_URL" | sed 's/@postgres:/@localhost:/')
        echo -e "${BLUE}ℹ️  DATABASE_URL ajustado para desenvolvimento local (postgres → localhost)${NC}"
    fi
elif [ -n "$POSTGRES_PASSWORD" ] && [ -n "$POSTGRES_USER" ] && [ -n "$POSTGRES_DB" ]; then
    # Construir DATABASE_URL a partir das variáveis individuais
    # Sempre usar localhost quando rodando localmente (Docker expõe portas)
    POSTGRES_HOST="localhost"
    POSTGRES_PORT="${POSTGRES_PORT:-5432}"
    
    # URL-encode a senha para evitar problemas com caracteres especiais
    ENCODED_PASSWORD=$(python3 -c "import urllib.parse; print(urllib.parse.quote('$POSTGRES_PASSWORD', safe=''))")
    export DATABASE_URL="postgresql://${POSTGRES_USER}:${ENCODED_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}"
    echo -e "${BLUE}ℹ️  DATABASE_URL construído: postgresql://${POSTGRES_USER}:***@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}${NC}"
else
    echo -e "${RED}✗ ERRO: DATABASE_URL ou variáveis POSTGRES_* não estão definidas no .env${NC}"
    echo "   Configure DATABASE_URL ou POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB no arquivo .env"
    exit 1
fi

# Ajustar REDIS_URL para desenvolvimento local
if [ -n "$REDIS_URL" ]; then
    if echo "$REDIS_URL" | grep -q "@redis:"; then
        # Sempre trocar "redis" por "localhost" quando rodando localmente
        # (Docker expõe portas para o host, então localhost funciona)
        export REDIS_URL=$(echo "$REDIS_URL" | sed 's/@redis:/@localhost:/')
        echo -e "${BLUE}ℹ️  REDIS_URL ajustado para desenvolvimento local (redis → localhost)${NC}"
    fi
elif [ -n "$REDIS_PASSWORD" ]; then
    # Construir REDIS_URL a partir das variáveis individuais
    # Sempre usar localhost quando rodando localmente (Docker expõe portas)
    REDIS_HOST="localhost"
    REDIS_PORT="${REDIS_PORT:-6379}"
    
    # URL-encode a senha para evitar problemas com caracteres especiais
    ENCODED_REDIS_PASSWORD=$(python3 -c "import urllib.parse; print(urllib.parse.quote('$REDIS_PASSWORD', safe=''))")
    export REDIS_URL="redis://:${ENCODED_REDIS_PASSWORD}@${REDIS_HOST}:${REDIS_PORT}/0"
    echo -e "${BLUE}ℹ️  REDIS_URL construído: redis://:***@${REDIS_HOST}:${REDIS_PORT}/0${NC}"
fi

echo ""
echo "📋 Configuração:"
echo "----------------"
echo "  Host: 0.0.0.0"
echo "  Porta: 8001"
echo "  Modo: Desenvolvimento (--reload ativado)"
echo "  Docs: http://localhost:8001/docs"
echo "  API: http://localhost:8001"
echo "  Database: ${DATABASE_URL%%@*}@***"  # Mostrar apenas user, não senha
echo "  Redis: ${REDIS_URL%%@*}@***"  # Mostrar apenas protocolo, não senha
echo ""

# Verificação final antes de iniciar
if [ "$POSTGRES_RUNNING" = false ]; then
    echo -e "${YELLOW}⚠️  AVISO: PostgreSQL não está rodando - a aplicação pode falhar ao iniciar${NC}"
    if [ -n "$DOCKER_COMPOSE_CMD" ]; then
        echo "   Para iniciar manualmente: $DOCKER_COMPOSE_CMD up -d postgres redis"
    else
        echo "   Para iniciar manualmente: docker compose up -d postgres redis"
    fi
    echo ""
    read -p "Deseja continuar mesmo assim? (s/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Ss]$ ]]; then
        echo "Cancelado pelo usuário"
        exit 0
    fi
fi

# Iniciar o servidor
echo -e "${BLUE}🌐 Iniciando servidor FastAPI...${NC}"
echo ""
echo "Pressione Ctrl+C para parar o servidor"
echo "========================================"
echo ""

# Executar uvicorn em modo desenvolvimento
exec uvicorn src.api.main:app \
    --host 0.0.0.0 \
    --port 8001 \
    --reload \
    --reload-dir src \
    --log-level info

