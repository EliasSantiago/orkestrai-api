# 🔄 Model Override - Guia Completo

## 📋 Visão Geral

Agora você pode **sobrescrever o modelo LLM** do agente diretamente no payload da requisição. Isso permite:

✅ Trocar de modelo quando um estiver sobrecarregado (erro 503)  
✅ Testar diferentes modelos com o mesmo agente  
✅ Usar modelos mais rápidos/baratos para queries simples  
✅ Flexibilidade total sem precisar modificar o agente  

## 🚀 Como Usar

### Sintaxe Básica

Adicione o campo `model` no payload da requisição:

```bash
curl -X 'POST' \
  'http://localhost:8001/api/agents/chat' \
  -H 'Authorization: Bearer YOUR_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "agent_id": 5,
    "message": "Sua mensagem aqui",
    "session_id": "sua-session-id",
    "model": "gpt-4o-mini"
  }'
```

### Campos do Payload

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `agent_id` | integer | ✅ Sim | ID do agente |
| `message` | string | ✅ Sim | Mensagem para o agente |
| `session_id` | string | ❌ Não | ID da sessão (auto-gerado se não fornecido) |
| `model` | string | ❌ Não | Modelo LLM para usar (sobrescreve o padrão do agente) |

## 📊 Modelos Disponíveis

### Listar Todos os Modelos

Para ver todos os modelos disponíveis na sua instalação:

```bash
curl -X 'POST' \
  'http://localhost:8001/api/agents/chat' \
  -H 'Authorization: Bearer YOUR_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "agent_id": 1,
    "message": "teste",
    "model": "modelo-invalido"
  }'
```

O erro retornará a lista de modelos disponíveis.

### Modelos Comuns

#### **Google Gemini** (via ADK)
- `gemini-2.0-flash-exp` (padrão)
- `gemini-2.5-flash`
- `gemini-2.0-flash-thinking-exp`
- `gemini-1.5-pro-latest`
- `gemini-1.5-flash-latest`

#### **OpenAI** (se configurado)
- `gpt-4o`
- `gpt-4o-mini` ⭐ (rápido e barato)
- `gpt-4-turbo`
- `gpt-3.5-turbo`

#### **Claude** (se configurado via OpenAI-compatible endpoint)
- `claude-3-5-sonnet-latest`
- `claude-3-opus-latest`
- `claude-3-haiku-latest`

#### **Ollama** (se configurado)
- Qualquer modelo instalado no Ollama local
- Ex: `llama3.1`, `mistral`, `phi3`, etc.

#### **On-Premise** (se configurado)
- Modelos configurados no servidor on-premise

## 💡 Exemplos Práticos

### Exemplo 1: Trocar Modelo por Sobrecarga (503)

**Cenário:** Seu agente usa `gemini-2.5-flash`, mas está recebendo erro 503.

```bash
# ❌ Usando modelo padrão (sobrecarregado)
curl -X 'POST' \
  'http://localhost:8001/api/agents/chat' \
  -H 'Authorization: Bearer YOUR_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "agent_id": 5,
    "message": "Pesquise sobre...",
    "session_id": "abc123"
  }'

# Resposta:
# {"detail": "503 UNAVAILABLE. The model is overloaded."}

# ✅ Trocando para outro modelo
curl -X 'POST' \
  'http://localhost:8001/api/agents/chat' \
  -H 'Authorization: Bearer YOUR_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "agent_id": 5,
    "message": "Pesquise sobre...",
    "session_id": "abc123",
    "model": "gpt-4o-mini"
  }'

# Resposta:
# {
#   "response": "Resposta do agente...",
#   "agent_id": 5,
#   "agent_name": "Assistente de Pesquisa",
#   "session_id": "abc123",
#   "model_used": "gpt-4o-mini"
# }
```

### Exemplo 2: Seu Caso Específico

```bash
curl -X 'POST' \
  'http://localhost:8001/api/agents/chat' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyQGV4YW1wbGUuY29tIiwidXNlcl9pZCI6MiwiZXhwIjoxNzY1MzgxODIyfQ.3Fa34NlIGldX7m3TKKN2fveptCgkXkmmswV-2Mdyk00' \
  -H 'Content-Type: application/json' \
  -d '{
    "agent_id": 5,
    "message": "Quero a lista de resultados dos jogos de ontem pelo campeonato brasileiro",
    "session_id": "f88381f9-a28f-4029-886c-15425ec4745a",
    "model": "gpt-4o-mini"
  }'
```

### Exemplo 3: Testar Diferentes Modelos

```bash
# Teste com Gemini (rápido, grátis)
curl -X 'POST' 'http://localhost:8001/api/agents/chat' \
  -H 'Authorization: Bearer YOUR_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "agent_id": 5,
    "message": "Teste de modelo",
    "model": "gemini-2.5-flash"
  }'

# Teste com GPT-4o-mini (rápido, barato)
curl -X 'POST' 'http://localhost:8001/api/agents/chat' \
  -H 'Authorization: Bearer YOUR_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "agent_id": 5,
    "message": "Teste de modelo",
    "model": "gpt-4o-mini"
  }'

# Teste com GPT-4o (mais inteligente, mais caro)
curl -X 'POST' 'http://localhost:8001/api/agents/chat' \
  -H 'Authorization: Bearer YOUR_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "agent_id": 5,
    "message": "Teste de modelo",
    "model": "gpt-4o"
  }'
```

### Exemplo 4: Usar Modelo Local (Ollama)

```bash
# Use modelo local instalado no Ollama
curl -X 'POST' 'http://localhost:8001/api/agents/chat' \
  -H 'Authorization: Bearer YOUR_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "agent_id": 5,
    "message": "Pergunta simples",
    "model": "llama3.1"
  }'
```

## 🎯 Resposta com model_used

A resposta agora inclui qual modelo foi usado:

```json
{
  "response": "Aqui está a lista dos resultados...",
  "agent_id": 5,
  "agent_name": "Assistente de Pesquisa Avançada",
  "session_id": "f88381f9-a28f-4029-886c-15425ec4745a",
  "model_used": "gpt-4o-mini"
}
```

## ⚠️ Notas Importantes

### 1. Validação de Modelo

Se você especificar um modelo inválido, receberá um erro 400:

```json
{
  "detail": "Model 'modelo-invalido' is not supported. Available models: {...}"
}
```

### 2. Compatibilidade com Ferramentas

Todos os modelos suportam as mesmas ferramentas (tools). O model override **não afeta** as ferramentas disponíveis para o agente.

### 3. Continuidade de Sessão

Você pode trocar de modelo **durante a mesma sessão**:

```bash
# Mensagem 1 - usa gemini
curl -X 'POST' ... -d '{
  "agent_id": 5,
  "message": "Primeira pergunta",
  "session_id": "abc123"
}'

# Mensagem 2 - troca para gpt-4o-mini
curl -X 'POST' ... -d '{
  "agent_id": 5,
  "message": "Segunda pergunta",
  "session_id": "abc123",
  "model": "gpt-4o-mini"
}'
```

A conversa continua, mesmo trocando de modelo!

### 4. Performance vs Custo

| Modelo | Velocidade | Custo | Inteligência | Uso Recomendado |
|--------|-----------|-------|--------------|-----------------|
| `gpt-4o-mini` | ⚡⚡⚡ | 💰 | ⭐⭐⭐ | Queries simples, alta volume |
| `gemini-2.5-flash` | ⚡⚡⚡ | 💰 Grátis | ⭐⭐⭐ | Uso geral, rápido |
| `gpt-4o` | ⚡⚡ | 💰💰💰 | ⭐⭐⭐⭐⭐ | Tarefas complexas |
| `claude-3-5-sonnet` | ⚡⚡ | 💰💰 | ⭐⭐⭐⭐⭐ | Análise profunda |

## 🔧 Troubleshooting

### Erro: "Model not supported"

**Solução:** Verifique se o modelo está disponível:
1. Veja a lista de modelos suportados no erro
2. Verifique se as API keys estão configuradas no `.env`
3. Para Ollama, verifique se o modelo está instalado

### Erro: "503 UNAVAILABLE"

**Solução:** Troque para outro modelo:
- De `gemini-*` para `gpt-4o-mini`
- De `gpt-*` para `gemini-2.5-flash`
- Use modelo local (Ollama) se disponível

### Modelo não aparece na lista

**Causa:** API key não configurada no `.env`

**Solução:**
- OpenAI: Configure `OPENAI_API_KEY`
- Gemini: Configure `GOOGLE_API_KEY`
- Ollama: Configure `OLLAMA_API_BASE_URL`
- On-premise: Configure `ONPREMISE_API_BASE_URL`

## 📚 Documentação da API

### Swagger/OpenAPI

Acesse a documentação interativa:
```
http://localhost:8001/docs
```

Lá você pode:
- Ver todos os modelos disponíveis
- Testar o endpoint `/api/agents/chat`
- Ver exemplos de requisições

## ✅ Checklist

- [ ] Entendi como adicionar `model` no payload
- [ ] Sei quais modelos estão disponíveis na minha instalação
- [ ] Testei trocar de modelo quando receber erro 503
- [ ] Verifico o `model_used` na resposta
- [ ] Sei como listar modelos disponíveis

---

**Data de implementação:** 10 de novembro de 2025  
**Status:** ✅ Funcionalidade implementada e testada  
**Compatibilidade:** Todos os agentes existentes continuam funcionando normalmente

