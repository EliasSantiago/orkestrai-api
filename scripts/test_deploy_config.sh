#!/bin/bash
# Script para testar se a configuração de deploy está correta
# Execute antes de fazer o primeiro deploy

echo "🧪 Orkestrai API - Teste de Configuração de Deploy"
echo "=================================================="
echo ""

# Cores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

ERRORS=0
WARNINGS=0

# Função para imprimir resultado
print_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓${NC} $2"
    else
        echo -e "${RED}✗${NC} $2"
        ((ERRORS++))
    fi
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
    ((WARNINGS++))
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

# ==========================================
# TESTES LOCAIS
# ==========================================
echo "📋 Verificando Arquivos Locais..."
echo "-----------------------------------"

# Verificar arquivos necessários
[ -f "Dockerfile" ] && print_result 0 "Dockerfile existe" || print_result 1 "Dockerfile não encontrado"
[ -f ".dockerignore" ] && print_result 0 ".dockerignore existe" || print_result 1 ".dockerignore não encontrado"
[ -f "docker-compose.yml" ] && print_result 0 "docker-compose.yml existe" || print_result 1 "docker-compose.yml não encontrado"
[ -f "requirements.txt" ] && print_result 0 "requirements.txt existe" || print_result 1 "requirements.txt não encontrado"

# Verificar workflows
[ -f ".github/workflows/deploy.yml" ] && print_result 0 "Workflow de deploy existe" || print_result 1 "Workflow de deploy não encontrado"
[ -f ".github/workflows/ci.yml" ] && print_result 0 "Workflow de CI existe" || print_result 1 "Workflow de CI não encontrado"

# Verificar scripts
[ -f "scripts/deploy_manual.sh" ] && [ -x "scripts/deploy_manual.sh" ] && print_result 0 "Script de deploy manual existe e é executável" || print_result 1 "Script de deploy manual não encontrado ou não executável"
[ -f "scripts/check_server_status.sh" ] && [ -x "scripts/check_server_status.sh" ] && print_result 0 "Script de status existe e é executável" || print_result 1 "Script de status não encontrado ou não executável"

echo ""

# ==========================================
# TESTAR BUILD DOCKER LOCAL
# ==========================================
echo "🐳 Testando Build Docker Local..."
echo "-----------------------------------"

if command -v docker &> /dev/null; then
    print_result 0 "Docker instalado"
    
    echo "Construindo imagem de teste..."
    if docker build -t orkestrai-api:test . > /tmp/docker_build.log 2>&1; then
        print_result 0 "Build Docker bem-sucedido"
        
        # Verificar tamanho da imagem
        SIZE=$(docker images orkestrai-api:test --format "{{.Size}}")
        print_info "Tamanho da imagem: $SIZE"
        
        # Testar imports básicos
        echo "Testando imports da aplicação..."
        if docker run --rm orkestrai-api:test python -c "from src.api.main import app; print('✓ Imports OK')" > /dev/null 2>&1; then
            print_result 0 "Imports da aplicação OK"
        else
            print_result 1 "Erro ao importar aplicação"
        fi
        
        # Limpar imagem de teste
        docker rmi orkestrai-api:test > /dev/null 2>&1
    else
        print_result 1 "Falha no build Docker"
        echo ""
        echo "Últimas linhas do log de erro:"
        tail -10 /tmp/docker_build.log
    fi
else
    print_warning "Docker não instalado localmente (OK se vai fazer deploy remoto)"
fi

echo ""

# ==========================================
# VERIFICAR CONFIGURAÇÃO GIT/GITHUB
# ==========================================
echo "📦 Verificando Configuração Git/GitHub..."
echo "-----------------------------------------"

if [ -d ".git" ]; then
    print_result 0 "Repositório Git inicializado"
    
    # Verificar remote
    if git remote -v | grep -q "github.com"; then
        print_result 0 "Remote GitHub configurado"
        REPO_URL=$(git remote get-url origin)
        print_info "Repositório: $REPO_URL"
    else
        print_warning "Remote GitHub não encontrado"
    fi
    
    # Verificar branch
    CURRENT_BRANCH=$(git branch --show-current)
    print_info "Branch atual: $CURRENT_BRANCH"
    
    if [[ "$CURRENT_BRANCH" == "main" || "$CURRENT_BRANCH" == "master" ]]; then
        print_result 0 "Na branch principal (deploy automático ativo)"
    else
        print_warning "Não está na branch main/master (deploy não será acionado)"
    fi
    
    # Verificar arquivos não commitados
    if [ -z "$(git status --porcelain)" ]; then
        print_result 0 "Nenhuma mudança não commitada"
    else
        print_warning "Existem mudanças não commitadas"
        print_info "Execute: git add . && git commit -m 'Setup deploy'"
    fi
else
    print_result 1 "Não é um repositório Git"
fi

echo ""

# ==========================================
# VERIFICAR ARQUIVO .env
# ==========================================
echo "🔧 Verificando Arquivo .env..."
echo "------------------------------"

if [ -f ".env" ]; then
    print_warning ".env existe localmente (não deve ser commitado)"
    
    # Verificar se .env está no .gitignore
    if grep -q "^\.env$" .gitignore 2>/dev/null; then
        print_result 0 ".env está no .gitignore"
    else
        print_result 1 ".env NÃO está no .gitignore (PERIGO!)"
    fi
else
    print_result 0 ".env não existe localmente (correto)"
fi

# Verificar template
if [ -f "env.template" ]; then
    print_result 0 "Template de .env existe (env.template)"
else
    print_warning "Template de .env não encontrado"
fi

echo ""

# ==========================================
# INSTRUÇÕES PARA SECRETS DO GITHUB
# ==========================================
echo "🔐 Secrets do GitHub (Verificação Manual)"
echo "-----------------------------------------"
print_info "Você precisa configurar os seguintes secrets no GitHub:"
echo ""
echo "  1. GCP_HOST - IP da máquina E2"
echo "  2. GCP_USERNAME - Usuário SSH"
echo "  3. GCP_SSH_KEY - Chave privada SSH"
echo "  4. GCP_SSH_PORT - Porta SSH (opcional, padrão: 22)"
echo ""
print_info "Configure em: Settings → Secrets and variables → Actions"
echo ""

read -p "Os secrets do GitHub estão configurados? [y/N]: " secrets_ok
if [[ "$secrets_ok" =~ ^[Yy]$ ]]; then
    print_result 0 "Secrets do GitHub configurados (confirmado manualmente)"
else
    print_warning "Configure os secrets do GitHub antes do deploy"
fi

echo ""

# ==========================================
# INSTRUÇÕES PARA MÁQUINA E2
# ==========================================
echo "☁️ Máquina E2 Google Cloud (Verificação Manual)"
echo "----------------------------------------------"
print_info "Sua máquina E2 deve ter:"
echo ""
echo "  ✓ Docker instalado"
echo "  ✓ Docker Compose instalado"
echo "  ✓ Diretório ~/orkestrai-api criado"
echo "  ✓ Arquivo ~/orkestrai-api/.env configurado"
echo "  ✓ Chave SSH pública adicionada em ~/.ssh/authorized_keys"
echo "  ✓ Firewall configurado (porta 8001)"
echo ""
print_info "Use o script: ./scripts/setup_gcp_server.sh"
echo ""

read -p "A máquina E2 está configurada? [y/N]: " server_ok
if [[ "$server_ok" =~ ^[Yy]$ ]]; then
    print_result 0 "Máquina E2 configurada (confirmado manualmente)"
else
    print_warning "Configure a máquina E2 antes do deploy"
fi

echo ""

# ==========================================
# TESTE DE CONECTIVIDADE (OPCIONAL)
# ==========================================
echo "🌐 Teste de Conectividade (Opcional)"
echo "------------------------------------"

read -p "Deseja testar conexão SSH com a máquina E2? [y/N]: " test_ssh
if [[ "$test_ssh" =~ ^[Yy]$ ]]; then
    read -p "IP da máquina E2: " gcp_ip
    read -p "Usuário SSH: " gcp_user
    
    echo "Testando conexão SSH..."
    if ssh -o ConnectTimeout=5 -o BatchMode=yes "$gcp_user@$gcp_ip" "echo 'SSH OK'" 2>/dev/null; then
        print_result 0 "Conexão SSH bem-sucedida"
        
        # Verificar Docker no servidor
        echo "Verificando Docker no servidor..."
        if ssh "$gcp_user@$gcp_ip" "docker --version" > /dev/null 2>&1; then
            print_result 0 "Docker instalado no servidor"
        else
            print_result 1 "Docker não encontrado no servidor"
        fi
    else
        print_result 1 "Falha na conexão SSH"
        print_info "Verifique: IP, usuário, chave SSH"
    fi
else
    print_info "Teste de SSH pulado"
fi

echo ""

# ==========================================
# RESUMO
# ==========================================
echo "======================================"
echo "📊 RESUMO"
echo "======================================"
echo ""

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✅ Tudo pronto para deploy!${NC}"
    echo ""
    echo "Próximos passos:"
    echo "  1. Commit e push: git add . && git commit -m 'Setup deploy' && git push"
    echo "  2. Acompanhe no GitHub: Actions → Deploy to Google Cloud E2"
    echo "  3. Após deploy: http://SEU_IP:8001/docs"
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠️ Configuração OK com $WARNINGS aviso(s)${NC}"
    echo ""
    echo "Revise os avisos acima antes de fazer deploy."
else
    echo -e "${RED}❌ Encontrados $ERRORS erro(s) e $WARNINGS aviso(s)${NC}"
    echo ""
    echo "Corrija os erros antes de fazer deploy."
fi

echo ""
echo "Documentação completa: docs/DEPLOY_SETUP.md"
echo "Início rápido: QUICKSTART_DEPLOY.md"

exit $ERRORS

