# File Converters

Este módulo fornece conversores para transformar vários tipos de arquivos em texto, permitindo que os modelos LLM processem o conteúdo.

## Conversores Disponíveis

### 1. PDF Converter (`PDFConverter`)
- **Bibliotecas**: `pdfplumber` (preferido) ou `PyPDF2` (fallback)
- **Suporta**: Arquivos PDF
- **Funcionalidade**: Extrai texto de PDFs, incluindo páginas múltiplas

### 2. DOCX Converter (`DOCXConverter`)
- **Biblioteca**: `python-docx`
- **Suporta**: Arquivos DOCX (Microsoft Word)
- **Funcionalidade**: Extrai texto de documentos Word, incluindo parágrafos e tabelas

### 3. XLSX Converter (`XLSXConverter`)
- **Biblioteca**: `openpyxl`
- **Suporta**: Arquivos XLSX (Microsoft Excel)
- **Funcionalidade**: Extrai dados de planilhas Excel, incluindo múltiplas abas

### 4. CSV Converter (`CSVConverter`)
- **Biblioteca**: `csv` (built-in)
- **Suporta**: Arquivos CSV
- **Funcionalidade**: Lê arquivos CSV com suporte a múltiplos encodings

### 5. Image Converter (`ImageConverter`)
- **Bibliotecas**: `pytesseract`, `Pillow`
- **Suporta**: PNG, JPEG, GIF, BMP, TIFF, WebP
- **Funcionalidade**: OCR (Optical Character Recognition) para extrair texto de imagens
- **Nota**: Requer instalação do Tesseract OCR no sistema

### 6. Video Converter (`VideoConverter`)
- **Biblioteca**: `openai-whisper`
- **Suporta**: MP4, MPEG, MOV, AVI, WebM
- **Funcionalidade**: Transcrição de áudio de vídeos usando Whisper
- **Nota**: Requer modelo Whisper (baixado automaticamente na primeira execução)

## Instalação

### Dependências Python

Instale as dependências Python:

```bash
pip install -r requirements.txt
```

As dependências incluem:
- `pdfplumber>=0.10.0`
- `PyPDF2>=3.0.0`
- `python-docx>=1.1.0`
- `openpyxl>=3.1.0`
- `pytesseract>=0.3.10`
- `Pillow>=10.0.0`
- `openai-whisper>=20231117`

### Dependências do Sistema

#### Tesseract OCR (para conversão de imagens)

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
sudo apt-get install tesseract-ocr-por  # Para suporte a português
sudo apt-get install tesseract-ocr-eng  # Para suporte a inglês
```

**macOS:**
```bash
brew install tesseract
brew install tesseract-lang  # Para suporte a múltiplos idiomas
```

**Windows:**
1. Baixe o instalador do Tesseract: https://github.com/UB-Mannheim/tesseract/wiki
2. Instale e adicione ao PATH
3. Baixe os arquivos de idioma (por.traineddata, eng.traineddata) e coloque em `C:\Program Files\Tesseract-OCR\tessdata\`

#### FFmpeg (para conversão de vídeos - requerido pelo Whisper)

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Windows:**
1. Baixe FFmpeg: https://ffmpeg.org/download.html
2. Extraia e adicione ao PATH

## Uso

```python
from src.services.file_converters import FileConverterService

# Inicializar o serviço
converter_service = FileConverterService()

# Converter um arquivo
result = await converter_service.convert_to_text(
    file_content=file_bytes,
    file_name="documento.pdf",
    mime_type="application/pdf"
)

if result.success:
    print(f"Texto extraído: {result.text}")
    print(f"Metadados: {result.metadata}")
else:
    print(f"Erro: {result.error}")
```

## Integração

O `FileConverterService` é automaticamente usado no processamento de arquivos enviados via API (`/api/agents/chat/stream/multipart`). Os arquivos são convertidos para texto antes de serem enviados ao modelo LLM.

## Notas

- **PDFs**: Se `pdfplumber` não estiver disponível, o sistema usa `PyPDF2` como fallback
- **Imagens**: Se o OCR falhar, a imagem pode ser enviada diretamente ao modelo (se o modelo suportar visão)
- **Vídeos**: O modelo Whisper é baixado automaticamente na primeira execução (pode demorar)
- **Performance**: Conversões de arquivos grandes podem demorar. Considere implementar processamento assíncrono para arquivos muito grandes

