# Configuração do Provedor Ollama

Este guia explica como configurar e usar o provedor Ollama para modelos LLM locais.

## 📋 Visão Geral

O Ollama é uma ferramenta para executar modelos LLM localmente. Este provedor permite usar modelos Ollama diretamente na aplicação.

## 🔧 Configuração

### 1. Adicionar Variáveis no `.env`

Adicione as seguintes variáveis de ambiente:

```env
# URL base da API Ollama (geralmente localhost:11434)
OLLAMA_API_BASE_URL=http://localhost:11434

# Lista de modelos disponíveis (OPCIONAL - separados por vírgula)
# Se não configurar, qualquer modelo Ollama será aceito
# OLLAMA_MODELS=gemma-2b-light:latest,llama2:7b,mistral:latest
```

### 2. Configuração Mínima

```env
# Configuração mínima
OLLAMA_API_BASE_URL=http://localhost:11434
```

### 3. Configuração com Lista de Modelos

```env
# Configuração com lista de modelos (validação antecipada)
OLLAMA_API_BASE_URL=http://localhost:11434
OLLAMA_MODELS=gemma-2b-light:latest,llama2:7b,mistral:latest
```

## 🚀 Como Funciona

### Endpoint Usado

O provedor Ollama usa o endpoint:
```
{OLLAMA_API_BASE_URL}/api/generate
```

Exemplo:
```
http://localhost:11434/api/generate
```

### Formato da Requisição

O provedor converte automaticamente as mensagens para o formato Ollama:

**Entrada (formato interno):**
```json
{
  "messages": [
    {"role": "system", "content": "Você é um assistente útil."},
    {"role": "user", "content": "Olá"}
  ],
  "model": "gemma-2b-light:latest"
}
```

**Enviado para Ollama:**
```json
{
  "model": "gemma-2b-light:latest",
  "prompt": "System: Você é um assistente útil.\n\nUser: Olá",
  "stream": true,
  "options": {
    "temperature": 0.7,
    "top_p": 0.9,
    "top_k": 40,
    "repeat_penalty": 1.1,
    "num_ctx": 1024
  }
}
```

### Formato da Resposta

Ollama retorna JSON lines (uma linha JSON por chunk):
```json
{"response": "Olá! Como posso ajudar?", "done": false}
{"response": " Estou aqui para", "done": false}
{"response": " responder suas perguntas.", "done": true}
```

O provedor extrai automaticamente o campo `response` e faz stream dos chunks.

## 📝 Exemplo de Uso

### 1. Criar Agente com Modelo Ollama

```bash
curl -X POST http://localhost:8001/api/agents \
  -H "Authorization: Bearer SEU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Assistente Ollama",
    "model": "gemma-2b-light:latest",
    "description": "Assistente usando modelo Ollama local",
    "instruction": "Você é um assistente útil e prestativo."
  }'
```

### 2. Testar Chat

```bash
curl -X POST http://localhost:8001/api/agents/chat \
  -H "Authorization: Bearer SEU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": 1,
    "message": "Olá, como você pode me ajudar?",
    "session_id": ""
  }'
```

## 🔍 Detecção de Modelos Ollama

O provedor detecta automaticamente modelos Ollama pelos seguintes padrões:

- ✅ Modelos com `:` (ex: `gemma-2b-light:latest`, `llama2:7b`)
- ✅ Modelos que começam com prefixos comuns:
  - `llama` (ex: `llama2`, `llama3`)
  - `mistral` (ex: `mistral:latest`)
  - `gemma` (ex: `gemma-2b-light:latest`)
  - `phi` (ex: `phi-2`)
  - `codellama` (ex: `codellama:7b`)
  - `neural-chat` (ex: `neural-chat:latest`)
  - `starling` (ex: `starling-lm:latest`)

### Exemplos de Modelos Suportados

| Modelo | Detectado? | Motivo |
|--------|------------|--------|
| `gemma-2b-light:latest` | ✅ Sim | Tem `:` |
| `llama2:7b` | ✅ Sim | Tem `:` |
| `mistral:latest` | ✅ Sim | Tem `:` e prefixo `mistral` |
| `llama3` | ✅ Sim | Prefixo `llama` |
| `gpt-4o` | ❌ Não | Não é modelo Ollama |

## ⚙️ Parâmetros Opcionais

Você pode passar parâmetros adicionais no chat:

```python
# Exemplo de uso programático
provider = OllamaProvider()
async for chunk in provider.chat(
    messages=[...],
    model="gemma-2b-light:latest",
    temperature=0.8,  # Personalizado
    top_p=0.95,       # Personalizado
    top_k=50,         # Personalizado
    repeat_penalty=1.2, # Personalizado
    num_ctx=2048      # Personalizado
):
    print(chunk, end="")
```

## 🔧 Troubleshooting

### Erro: "OLLAMA_API_BASE_URL not configured"

**Solução:** Adicione `OLLAMA_API_BASE_URL` no `.env`:
```env
OLLAMA_API_BASE_URL=http://localhost:11434
```

### Erro: "Connection refused"

**Causa:** Servidor Ollama não está rodando.

**Solução:**
1. Verifique se o Ollama está instalado e rodando:
   ```bash
   curl http://localhost:11434/api/tags
   ```
2. Se não estiver rodando, inicie o Ollama:
   ```bash
   ollama serve
   ```

### Erro: "Model not found"

**Causa:** Modelo não está disponível no Ollama.

**Solução:**
1. Liste modelos disponíveis:
   ```bash
   curl http://localhost:11434/api/tags
   ```
2. Baixe o modelo se necessário:
   ```bash
   ollama pull gemma-2b-light:latest
   ```

### Modelo sendo roteado para outro provider

**Causa:** Modelo não está sendo detectado como Ollama.

**Solução:**
1. Use formato com `:` (ex: `gemma-2b-light:latest`)
2. Ou configure `OLLAMA_MODELS` com o nome exato:
   ```env
   OLLAMA_MODELS=gemma-2b-light:latest
   ```

## 📚 Referências

- [Ollama Documentation](https://ollama.ai/docs)
- [Ollama API](https://github.com/ollama/ollama/blob/main/docs/api.md)
- [Available Models](https://ollama.ai/library)

## ✅ Checklist

- [ ] Ollama instalado e rodando
- [ ] `OLLAMA_API_BASE_URL` configurado no `.env`
- [ ] Modelo baixado no Ollama (ex: `ollama pull gemma-2b-light:latest`)
- [ ] Aplicação reiniciada
- [ ] Agente criado com modelo Ollama
- [ ] Chat testado com sucesso

