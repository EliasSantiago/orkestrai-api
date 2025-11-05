#!/bin/bash

# Script de instalação e configuração da aplicação

echo "=========================================="
echo "Agents ADK Application - Setup"
echo "=========================================="

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "✗ Python 3 não encontrado. Por favor, instale Python 3.9 ou superior."
    exit 1
fi

echo "✓ Python encontrado: $(python3 --version)"

# Criar ambiente virtual
if [ ! -d ".venv" ]; then
    echo ""
    echo "Criando ambiente virtual..."
    python3 -m venv .venv
    echo "✓ Ambiente virtual criado"
else
    echo "✓ Ambiente virtual já existe"
fi

# Ativar ambiente virtual
echo ""
echo "Ativando ambiente virtual..."
source .venv/bin/activate

# Instalar dependências
echo ""
echo "Instalando dependências..."
pip install --upgrade pip
pip install -r requirements.txt

echo "✓ Dependências instaladas"

# Verificar arquivo .env
if [ ! -f ".env" ]; then
    echo ""
    echo "⚠ Arquivo .env não encontrado"
    echo "Criando .env a partir do .env.example..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "✓ Arquivo .env criado"
        echo ""
        echo "⚠ IMPORTANTE: Edite o arquivo .env e adicione suas API keys:"
        echo "   - GOOGLE_API_KEY"
        echo "   - OPENAI_API_KEY"
    else
        echo "✗ Arquivo .env.example não encontrado"
    fi
else
    echo "✓ Arquivo .env encontrado"
fi

# Verificar Docker
if command -v docker &> /dev/null && command -v docker compose &> /dev/null; then
    echo ""
    echo "✓ Docker e Docker Compose encontrados"
    echo ""
    echo "Para iniciar o PostgreSQL, execute:"
    echo "  docker-compose up -d"
else
    echo ""
    echo "⚠ Docker não encontrado. Você precisará instalá-lo para usar o PostgreSQL."
fi

echo ""
echo "=========================================="
echo "Setup concluído!"
echo "=========================================="
echo ""
echo "Próximos passos:"
echo "1. Edite o arquivo .env e adicione suas API keys"
echo "2. Inicie o PostgreSQL: docker-compose up -d"
echo "3. Execute a aplicação: python -m src.main"
echo ""

