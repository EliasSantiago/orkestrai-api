#!/bin/bash

# Script para remover pacotes CUDA instalados anteriormente

# Navegar para o diretório raiz do projeto
cd "$(dirname "$0")/.."

echo "=========================================="
echo "Limpeza de Pacotes CUDA"
echo "=========================================="
echo ""

# Função para calcular tamanho de diretório
get_dir_size() {
    if [ -d "$1" ]; then
        du -sh "$1" 2>/dev/null | cut -f1 || echo "0"
    else
        echo "0"
    fi
}

# Verificar espaço antes da limpeza
echo "📊 Verificando espaço em disco antes da limpeza..."
TORCH_CACHE_SIZE_BEFORE=$(get_dir_size "$HOME/.cache/torch")
PIP_CACHE_SIZE_BEFORE=$(get_dir_size "$HOME/.cache/pip")
WHISPER_CACHE_SIZE_BEFORE=$(get_dir_size "$HOME/.cache/whisper")

echo "  Cache PyTorch: $TORCH_CACHE_SIZE_BEFORE"
echo "  Cache pip: $PIP_CACHE_SIZE_BEFORE"
echo "  Cache Whisper: $WHISPER_CACHE_SIZE_BEFORE"
echo ""

# Verificar se o ambiente virtual existe
if [ ! -d ".venv" ]; then
    echo "⚠ Ambiente virtual não encontrado (.venv)"
    echo "Continuando com limpeza do sistema..."
else
    echo "Ativando ambiente virtual..."
    source .venv/bin/activate
    echo "✓ Ambiente virtual ativado"
    echo ""
    
    # Desinstalar pacotes PyTorch com CUDA
    echo "1️⃣ Removendo pacotes PyTorch com CUDA do ambiente virtual..."
    pip uninstall -y torch torchvision torchaudio 2>/dev/null || true
    pip uninstall -y nvidia-cublas-cu11 nvidia-cudnn-cu11 nvidia-cuda-nvrtc-cu11 nvidia-cuda-runtime-cu11 2>/dev/null || true
    pip uninstall -y nvidia-cuda-cupti-cu11 nvidia-cuda-nvcc-cu11 2>/dev/null || true
    echo "✓ Pacotes PyTorch removidos"
    echo ""
fi

# Limpar cache do pip
echo "2️⃣ Limpando cache do pip..."
pip cache purge 2>/dev/null || true
echo "✓ Cache do pip limpo"
echo ""

# Verificar e remover pacotes CUDA do sistema (Ubuntu/Debian)
if command -v apt &> /dev/null; then
    echo "3️⃣ Verificando pacotes CUDA do sistema..."
    
    # Listar pacotes CUDA instalados
    CUDA_PACKAGES=$(dpkg -l | grep -i cuda | awk '{print $2}' | grep -v "^$" || true)
    
    if [ -n "$CUDA_PACKAGES" ]; then
        echo "Pacotes CUDA encontrados no sistema:"
        echo "$CUDA_PACKAGES" | while read pkg; do
            echo "  - $pkg"
        done
        echo ""
        read -p "Deseja remover estes pacotes CUDA do sistema? (requer sudo) [y/N]: " remove_system
        
        if [[ "$remove_system" =~ ^[Yy]$ ]]; then
            echo "Removendo pacotes CUDA do sistema..."
            echo "$CUDA_PACKAGES" | xargs sudo apt-get remove -y 2>/dev/null || true
            sudo apt-get autoremove -y 2>/dev/null || true
            sudo apt-get autoclean 2>/dev/null || true
            echo "✓ Pacotes CUDA removidos do sistema"
        else
            echo "⚠ Pacotes CUDA do sistema mantidos"
        fi
    else
        echo "✓ Nenhum pacote CUDA encontrado no sistema"
    fi
    echo ""
fi

# Limpar diretórios de cache do PyTorch
echo "4️⃣ Limpando cache do PyTorch..."
if [ -d "$HOME/.cache/torch" ]; then
    rm -rf "$HOME/.cache/torch" 2>/dev/null || true
    echo "✓ Cache do PyTorch removido"
else
    echo "✓ Cache do PyTorch não encontrado"
fi

# Limpar diretórios de cache do pip
echo ""
echo "5️⃣ Limpando diretórios de cache adicionais..."
if [ -d "$HOME/.cache/pip" ]; then
    rm -rf "$HOME/.cache/pip" 2>/dev/null || true
    echo "✓ Cache do pip removido"
fi

# Limpar diretório de modelos do Whisper (opcional)
echo ""
read -p "Deseja remover modelos do Whisper baixados? (~500MB-2GB) [y/N]: " remove_whisper
if [[ "$remove_whisper" =~ ^[Yy]$ ]]; then
    if [ -d "$HOME/.cache/whisper" ]; then
        rm -rf "$HOME/.cache/whisper" 2>/dev/null || true
        echo "✓ Modelos do Whisper removidos"
    else
        echo "✓ Modelos do Whisper não encontrados"
    fi
fi

echo ""
echo "=========================================="
echo "Limpeza concluída!"
echo "=========================================="
echo ""
echo "📊 Resumo da limpeza:"
echo "  - Cache PyTorch removido: $TORCH_CACHE_SIZE_BEFORE"
echo "  - Cache pip removido: $PIP_CACHE_SIZE_BEFORE"
if [[ "$remove_whisper" =~ ^[Yy]$ ]]; then
    echo "  - Cache Whisper removido: $WHISPER_CACHE_SIZE_BEFORE"
fi
echo ""
echo "✅ Para reinstalar sem CUDA, execute:"
echo "  ./scripts/setup.sh"
echo ""
echo "O novo setup.sh instalará apenas PyTorch CPU-only (sem CUDA)."
echo ""

