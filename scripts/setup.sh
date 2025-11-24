#!/bin/bash

# Script de instalação e configuração da aplicação

# Navegar para o diretório raiz do projeto (pai de scripts/)
cd "$(dirname "$0")/.."

echo "=========================================="
echo "Orkestrai API - Setup"
echo "=========================================="

# Função para detectar o sistema operacional
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if [ -f /etc/debian_version ]; then
            echo "debian"
        elif [ -f /etc/redhat-release ]; then
            echo "redhat"
        else
            echo "linux"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    else
        echo "unknown"
    fi
}

OS_TYPE=$(detect_os)

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "✗ Python 3 não encontrado. Por favor, instale Python 3.9 ou superior."
    exit 1
fi

echo "✓ Python encontrado: $(python3 --version)"

# Verificar dependências do sistema
echo ""
echo "Verificando dependências do sistema..."

# Verificar Tesseract OCR (para conversão de imagens)
TESSERACT_MISSING=false
if ! command -v tesseract &> /dev/null; then
    echo "⚠ Tesseract OCR não encontrado (necessário para OCR de imagens)"
    TESSERACT_MISSING=true
else
    echo "✓ Tesseract OCR encontrado: $(tesseract --version 2>&1 | head -n 1)"
fi

# Verificar FFmpeg (para conversão de vídeos)
FFMPEG_MISSING=false
if ! command -v ffmpeg &> /dev/null; then
    echo "⚠ FFmpeg não encontrado (necessário para transcrição de vídeos)"
    FFMPEG_MISSING=true
else
    echo "✓ FFmpeg encontrado: $(ffmpeg -version 2>&1 | head -n 1 | cut -d' ' -f3)"
fi

# Perguntar se deseja instalar dependências do sistema
if [ "$TESSERACT_MISSING" = true ] || [ "$FFMPEG_MISSING" = true ]; then
    echo ""
    echo "Algumas dependências do sistema estão faltando."
    read -p "Deseja instalar automaticamente? (requer sudo) [y/N]: " install_system_deps
    
    if [[ "$install_system_deps" =~ ^[Yy]$ ]]; then
        if [ "$OS_TYPE" = "debian" ]; then
            echo ""
            echo "Instalando dependências do sistema (Ubuntu/Debian)..."
            sudo apt-get update
            
            if [ "$TESSERACT_MISSING" = true ]; then
                echo "  → Instalando Tesseract OCR..."
                sudo apt-get install -y tesseract-ocr tesseract-ocr-por tesseract-ocr-eng
                echo "  ✓ Tesseract OCR instalado"
            fi
            
            if [ "$FFMPEG_MISSING" = true ]; then
                echo "  → Instalando FFmpeg..."
                sudo apt-get install -y ffmpeg
                echo "  ✓ FFmpeg instalado"
            fi
        elif [ "$OS_TYPE" = "macos" ]; then
            if ! command -v brew &> /dev/null; then
                echo "✗ Homebrew não encontrado. Instale o Homebrew primeiro: https://brew.sh"
            else
                echo ""
                echo "Instalando dependências do sistema (macOS)..."
                
                if [ "$TESSERACT_MISSING" = true ]; then
                    echo "  → Instalando Tesseract OCR..."
                    brew install tesseract tesseract-lang
                    echo "  ✓ Tesseract OCR instalado"
                fi
                
                if [ "$FFMPEG_MISSING" = true ]; then
                    echo "  → Instalando FFmpeg..."
                    brew install ffmpeg
                    echo "  ✓ FFmpeg instalado"
                fi
            fi
        else
            echo "⚠ Instalação automática não suportada para este sistema operacional."
            echo "  Por favor, instale manualmente:"
            if [ "$TESSERACT_MISSING" = true ]; then
                echo "    - Tesseract OCR: https://github.com/tesseract-ocr/tesseract"
            fi
            if [ "$FFMPEG_MISSING" = true ]; then
                echo "    - FFmpeg: https://ffmpeg.org/download.html"
            fi
        fi
    else
        echo ""
        echo "⚠ Dependências do sistema não instaladas."
        echo "  Para instalar manualmente:"
        if [ "$OS_TYPE" = "debian" ]; then
            if [ "$TESSERACT_MISSING" = true ]; then
                echo "    sudo apt-get install tesseract-ocr tesseract-ocr-por tesseract-ocr-eng"
            fi
            if [ "$FFMPEG_MISSING" = true ]; then
                echo "    sudo apt-get install ffmpeg"
            fi
        elif [ "$OS_TYPE" = "macos" ]; then
            if [ "$TESSERACT_MISSING" = true ]; then
                echo "    brew install tesseract tesseract-lang"
            fi
            if [ "$FFMPEG_MISSING" = true ]; then
                echo "    brew install ffmpeg"
            fi
        fi
    fi
fi

# Criar ambiente virtual
echo ""
if [ ! -d ".venv" ]; then
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

# Instalar dependências Python
echo ""
echo "Instalando dependências Python..."
pip install --upgrade pip

# Instalar PyTorch CPU-only primeiro para evitar downloads de CUDA
echo ""
echo "Instalando PyTorch CPU-only (para Whisper, sem CUDA)..."
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu
echo "✓ PyTorch CPU-only instalado"

# Instalar outras dependências
echo ""
echo "Instalando outras dependências..."
pip install -r requirements.txt

# Instalar Whisper após PyTorch (para garantir que use a versão CPU)
echo ""
echo "Instalando Whisper (transcrição de vídeos)..."
pip install "openai-whisper>=20231117"
echo "✓ Whisper instalado"

echo "✓ Todas as dependências Python instaladas"

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
echo "3. Execute a aplicação: ./scripts/start_backend.sh"
echo ""
echo "Recursos disponíveis:"
echo "  ✓ Conversão de PDFs para texto"
echo "  ✓ Conversão de DOCX/XLSX/CSV para texto"
if command -v tesseract &> /dev/null; then
    echo "  ✓ OCR de imagens (Tesseract instalado)"
else
    echo "  ⚠ OCR de imagens (Tesseract não instalado)"
fi
if command -v ffmpeg &> /dev/null; then
    echo "  ✓ Transcrição de vídeos (FFmpeg instalado)"
else
    echo "  ⚠ Transcrição de vídeos (FFmpeg não instalado)"
fi
echo ""

