# Configuração do Provedor On-Premise

Este guia explica como configurar e usar o provedor LLM on-premise na aplicação.

## 📋 Visão Geral

O provedor on-premise permite que você use modelos de linguagem hospedados em infraestrutura própria, com suporte a:
- Autenticação OAuth 2.0 (client_credentials ou password grant)
- Formato de API similar ao Ollama/OpenAI
- Streaming de respostas em tempo real
- Configuração flexível de parâmetros

## 🔐 Autenticação OAuth

O provedor on-premise usa autenticação OAuth 2.0 para gerar tokens de acesso automaticamente.

### Variáveis de Ambiente Necessárias

Adicione as seguintes variáveis no arquivo `.env`:

```env
# URL base da API on-premise
ONPREMISE_API_BASE_URL=https://apidesenv.go.gov.br/ia/modelos-linguagem-natural/v2.0/

# Endpoint do chat (relativo à URL base)
ONPREMISE_CHAT_ENDPOINT=/api/chat

# URL para gerar token OAuth
ONPREMISE_TOKEN_URL=https://apidesenv.go.gov.br/token

# Consumer Key e Secret (credenciais OAuth)
ONPREMISE_CONSUMER_KEY=sua_consumer_key_aqui
ONPREMISE_CONSUMER_SECRET=sua_consumer_secret_aqui

# Tipo de grant OAuth (client_credentials ou password)
ONPREMISE_OAUTH_GRANT_TYPE=client_credentials

# Para grant type "password", adicione:
# ONPREMISE_USERNAME=seu_usuario
# ONPREMISE_PASSWORD=sua_senha

# Verificação SSL (false para certificados autoassinados)
VERIFY_SSL=false

# Opcional: Lista de modelos suportados (separados por vírgula)
# Se não especificado, qualquer nome de modelo será aceito
ONPREMISE_MODELS=modelo1,modelo2,modelo3
```

## 📦 Formato do Payload

O provedor on-premise envia requisições no seguinte formato:

```json
{
  "model": "nome-do-modelo",
  "messages": [
    {
      "role": "system",
      "content": "Você é um assistente útil."
    },
    {
      "role": "user",
      "content": "Olá, como você está?"
    }
  ],
  "stream": true,
  "options": {
    "temperature": 0.1,
    "top_p": 0.15,
    "top_k": 0,
    "num_predict": 500,
    "repeat_penalty": 1.1,
    "num_ctx": 4096,
    "seed": 0
  },
  "format": "string",
  "keep_alive": "5m"
}
```

### Campos Principais

- **model**: Nome do modelo a ser usado
- **messages**: Array de mensagens da conversa (role: system/user/assistant)
- **stream**: true para respostas em streaming, false para resposta completa
- **options**: Parâmetros de geração do modelo
  - **temperature**: Controle de aleatoriedade (0.0 a 1.0, padrão: 0.1)
  - **top_p**: Nucleus sampling (0.0 a 1.0, padrão: 0.15)
  - **top_k**: Top-K sampling (padrão: 0 = desabilitado)
  - **num_predict**: Número máximo de tokens a gerar (padrão: 500)
  - **repeat_penalty**: Penalidade para repetição (padrão: 1.1)
  - **num_ctx**: Tamanho da janela de contexto (padrão: 4096)
  - **seed**: Semente para reprodutibilidade (opcional)
- **format**: Formato da resposta (opcional, ex: "json")
- **keep_alive**: Tempo para manter o modelo carregado (opcional, ex: "5m")

## 🔄 Formatos de Resposta Suportados

O provedor on-premise suporta múltiplos formatos de resposta:

### 1. Formato OpenAI (SSE)
```json
data: {"choices": [{"delta": {"content": "texto"}}]}
data: [DONE]
```

### 2. Formato Ollama /api/chat
```json
{"message": {"role": "assistant", "content": "texto"}, "done": false}
{"message": {"role": "assistant", "content": ""}, "done": true}
```

### 3. Formato Ollama /api/generate
```json
{"response": "texto", "done": false}
{"response": "", "done": true}
```

### 4. Formato Direto
```json
{"content": "texto"}
```

## 🚀 Como Usar

### 1. Via API REST

Crie um agente com o modelo on-premise:

```bash
curl -X POST http://localhost:8001/api/agents \
  -H "Authorization: Bearer seu_token" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Assistente On-Premise",
    "description": "Assistente usando modelo on-premise",
    "model": "nome-do-modelo-onpremise",
    "instruction": "Você é um assistente útil."
  }'
```

### 2. Via Interface Web ADK

1. Acesse http://localhost:8000
2. Crie um novo agente
3. Selecione o modelo on-premise configurado
4. Configure as instruções e ferramentas
5. Comece a conversar!

### 3. Via Python

```python
from src.core.llm_factory import LLMFactory
from src.core.llm_provider import LLMMessage

# Obter o provedor para o modelo
provider = LLMFactory.get_provider("nome-do-modelo-onpremise")

# Criar mensagens
messages = [
    LLMMessage(role="system", content="Você é um assistente útil."),
    LLMMessage(role="user", content="Olá, como você está?")
]

# Fazer chat
async for chunk in provider.chat(
    messages=messages,
    model="nome-do-modelo-onpremise",
    temperature=0.1,
    num_predict=500
):
    print(chunk, end="", flush=True)
```

## 🔍 Detecção Automática de Modelos

O provedor on-premise é detectado automaticamente quando:

1. **ONPREMISE_MODELS está configurado**: Apenas os modelos listados são aceitos
2. **ONPREMISE_MODELS está vazio**: Aceita modelos que parecem on-premise:
   - Contém ":" no nome (ex: `gpt-oss:20b`, `llama-2:7b`)
   - Começa com `local-` ou `onpremise-`
   - Não são modelos conhecidos do OpenAI ou Gemini

### Exemplos de Nomes de Modelos

✅ **Aceitos como on-premise:**
- `gpt-oss:20b`
- `llama-2:7b`
- `local-model`
- `onpremise-mixtral`
- `custom-model:latest`

❌ **Rejeitados (OpenAI/Gemini):**
- `gpt-4o`
- `gpt-3.5-turbo`
- `gemini-2.0-flash-exp`

## 🛠️ Testando a Configuração

Use o script de teste incluído:

```bash
# Ativar ambiente virtual
source .venv/bin/activate

# Executar teste
python scripts/test_onpremise_provider.py
```

O script irá:
1. Verificar as variáveis de ambiente
2. Testar a geração de token OAuth
3. Fazer uma requisição de teste ao modelo
4. Exibir o resultado

## ⚠️ Troubleshooting

### Erro: "ONPREMISE_API_BASE_URL not configured"
**Solução**: Configure a variável `ONPREMISE_API_BASE_URL` no `.env`

### Erro: "Failed to generate OAuth token"
**Soluções**:
- Verifique se `ONPREMISE_TOKEN_URL` está correto
- Confirme que `ONPREMISE_CONSUMER_KEY` e `ONPREMISE_CONSUMER_SECRET` estão corretos
- Para grant type "password", verifique `ONPREMISE_USERNAME` e `ONPREMISE_PASSWORD`

### Erro de Certificado SSL
**Solução**: Adicione `VERIFY_SSL=false` no `.env` (apenas para desenvolvimento!)

### Timeout ou Conexão Recusada
**Soluções**:
- Verifique se o servidor está rodando e acessível
- Confirme se a URL base está correta
- Verifique firewall e políticas de rede

### Modelo Não Reconhecido
**Solução**: Configure `ONPREMISE_MODELS` com a lista de modelos ou use um nome de modelo com `:` ou prefixo `local-`/`onpremise-`

## 📊 Parâmetros Avançados

### Personalizando Parâmetros via API

```bash
curl -X POST http://localhost:8001/api/agents/{agent_id}/chat \
  -H "Authorization: Bearer seu_token" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Olá!",
    "session_id": "session123",
    "model": "gpt-oss:20b",
    "temperature": 0.5,
    "top_p": 0.9,
    "top_k": 40,
    "num_predict": 1000,
    "repeat_penalty": 1.2,
    "num_ctx": 8192,
    "seed": 42,
    "format": "json"
  }'
```

### Parâmetros Recomendados

**Para respostas criativas:**
```python
temperature=0.7
top_p=0.9
top_k=40
```

**Para respostas precisas:**
```python
temperature=0.1
top_p=0.15
top_k=0
```

**Para respostas longas:**
```python
num_predict=2000
num_ctx=8192
```

## 🔒 Segurança

⚠️ **IMPORTANTE**: 
- Nunca exponha as credenciais OAuth no código
- Use sempre `VERIFY_SSL=true` em produção
- Rotacione as credenciais periodicamente
- Use HTTPS para todas as comunicações
- Configure timeouts adequados

## 📝 Cache de Tokens

O provedor on-premise implementa cache automático de tokens OAuth:
- Tokens são armazenados em memória
- Renovação automática antes da expiração
- Margem de segurança de 60 segundos
- Cache limpo em caso de erro

## 🎯 Próximos Passos

1. Configure as variáveis de ambiente
2. Execute o script de teste
3. Crie um agente usando o modelo on-premise
4. Teste via API ou interface web
5. Ajuste os parâmetros conforme necessário

## 📚 Referências

- [Documentação da API On-Premise](https://apidesenv.go.gov.br/docs)
- [OAuth 2.0 Specification](https://oauth.net/2/)
- [Ollama API Documentation](https://github.com/ollama/ollama/blob/main/docs/api.md)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)

