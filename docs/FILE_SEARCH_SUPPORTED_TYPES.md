# Tipos de Arquivo Suportados pelo File Search

## 📄 Documentos

| Extensão | MIME Type | Descrição |
|----------|-----------|-----------|
| `.pdf` | `application/pdf` | Documentos PDF |
| `.doc` | `application/msword` | Documentos Word (antigo) |
| `.docx` | `application/vnd.openxmlformats-officedocument.wordprocessingml.document` | Documentos Word (moderno) |
| `.rtf` | `application/rtf` | Rich Text Format |
| `.txt` | `text/plain` | Arquivos de texto simples |
| `.md` | `text/markdown` | Markdown |
| `.html` | `text/html` | HTML |
| `.csv` | `text/csv` | Valores separados por vírgula |

## 📊 Planilhas

| Extensão | MIME Type | Descrição |
|----------|-----------|-----------|
| `.xls` | `application/vnd.ms-excel` | Planilhas Excel (antigo) |
| `.xlsx` | `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet` | Planilhas Excel (moderno) |

## 📽️ Apresentações

| Extensão | MIME Type | Descrição |
|----------|-----------|-----------|
| `.pptx` | `application/vnd.openxmlformats-officedocument.presentationml.presentation` | Apresentações PowerPoint |

## 🖼️ Imagens

| Extensão | MIME Type | Descrição |
|----------|-----------|-----------|
| `.png` | `image/png` | PNG |
| `.jpg` / `.jpeg` | `image/jpeg` | JPEG |
| `.webp` | `image/webp` | WebP |
| `.heif` | `image/heif` | HEIF |

## 🎵 Áudio

| Extensão | MIME Type | Descrição |
|----------|-----------|-----------|
| `.mp3` | `audio/mpeg` | MP3 |
| `.m4a` | `audio/mp4` | M4A |
| `.wav` | `audio/wav` | WAV |

## 🎬 Vídeo

| Extensão | MIME Type | Descrição |
|----------|-----------|-----------|
| `.mp4` | `video/mp4` | MP4 |
| `.mpeg` | `video/mpeg` | MPEG |
| `.mov` | `video/quicktime` | QuickTime |
| `.avi` | `video/x-msvideo` | AVI |
| `.flv` | `video/x-flv` | Flash Video |
| `.webm` | `video/webm` | WebM |
| `.wmv` | `video/x-ms-wmv` | Windows Media Video |
| `.3gp` | `video/3gpp` | 3GPP |

## 💻 Código

| Extensão | MIME Type | Descrição |
|----------|-----------|-----------|
| `.py` | `text/x-python` | Python |
| `.java` | `text/x-java` | Java |
| `.c` | `text/x-c` | C |
| `.cpp` | `text/x-c++` | C++ |
| `.php` | `text/x-php` | PHP |
| `.sql` | `text/x-sql` | SQL |
| `.js` | `text/javascript` | JavaScript |
| `.css` | `text/css` | CSS |

## 📦 Outros

| Extensão | MIME Type | Descrição |
|----------|-----------|-----------|
| `.json` | `application/json` | JSON |
| `.xml` | `application/xml` | XML |

## ⚠️ Limites

- **Tamanho máximo**: 100 MB por arquivo
- **Tipos não suportados**: Arquivos binários sem extensão conhecida, executáveis, etc.

## 🔍 Detecção Automática

O sistema detecta automaticamente o MIME type baseado em:

1. **Content-Type do request** (se fornecido)
2. **Extensão do arquivo** (usando `mimetypes` do Python)
3. **Fallback manual** (mapeamento de extensões comuns)

Se nenhum MIME type puder ser determinado, o upload falhará com uma mensagem de erro clara.

