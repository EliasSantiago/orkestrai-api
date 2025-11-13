# Exemplos de Criação de Agentes com LiteLLM

Esta pasta contém exemplos de payloads JSON para criar agentes usando o formato correto de modelos LiteLLM.

## 📋 Formato de Modelos

Com LiteLLM, os modelos seguem o formato: `provider/model-name`

Exemplos:
- Google Gemini: `gemini/gemini-2.0-flash-exp`
- OpenAI: `openai/gpt-4o`
- Anthropic Claude: `anthropic/claude-3-opus-20240229`
- Ollama: `ollama/llama2`

## 🚀 Como Usar

### Criar Agente via API

```bash
curl -X POST http://localhost:8001/api/agents \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d @examples/agents/gemini_assistant.json
```

### Criar Agente via Swagger UI

1. Acesse: http://localhost:8001/docs
2. Faça login para obter o token
3. Clique em "POST /api/agents"
4. Cole o conteúdo de um dos arquivos JSON
5. Execute

## 📁 Exemplos Disponíveis

### Google Gemini
- `gemini_assistant.json` - Assistente geral com Gemini Flash
- `gemini_pro_analyst.json` - Analista com Gemini Pro
- `gemini_thinking.json` - Modelo com raciocínio avançado
- `gemini_coding_assistant.json` - Assistente de programação

### OpenAI
- `gpt4o_assistant.json` - Assistente com GPT-4o
- `gpt4o_mini_assistant.json` - Assistente rápido e econômico
- `gpt3_turbo_simple.json` - Assistente simples e barato

### Anthropic Claude
- `claude_opus_writer.json` - Escritor profissional
- `claude_sonnet_analyst.json` - Analista de dados
- `claude_haiku_fast.json` - Respostas rápidas

### Ollama (Local)
- `ollama_llama2.json` - Modelo local Llama 2
- `ollama_mistral.json` - Modelo local Mistral
- `ollama_codellama.json` - Assistente de código local

### Casos Especiais
- `rag_file_search_agent.json` - Agente com RAG/File Search
- `multi_tool_agent.json` - Agente com múltiplas ferramentas
- `web_search_agent.json` - Agente com busca web

## 🔧 Campos do JSON

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `name` | string | ✅ Sim | Nome do agente |
| `description` | string | ❌ Não | Descrição do agente |
| `instruction` | string | ✅ Sim | Instruções do sistema para o agente |
| `model` | string | ✅ Sim | Modelo no formato `provider/model-name` |
| `tools` | array | ❌ Não | Lista de ferramentas (ex: `["calculator", "time"]`) |
| `use_file_search` | boolean | ❌ Não | Habilitar RAG/File Search (apenas Gemini) |

## 📝 Notas Importantes

### File Search / RAG
- ✅ **Funciona apenas com Gemini** (`gemini/` models)
- ❌ **Não funciona** com OpenAI, Claude, Ollama

Exemplo:
```json
{
  "model": "gemini/gemini-2.5-flash",
  "use_file_search": true
}
```

### Tools Disponíveis
- `calculator` - Calculadora matemática
- `time` - Informações de data/hora
- `web_search` - Busca web (requer Tavily API key)
- `google_calendar` - Google Calendar (requer OAuth)

## 🔗 Referências

- [Documentação LiteLLM](../docs/arquitetura/litellm/README.md)
- [Modelos Suportados](../docs/arquitetura/litellm/USAGE.md#nomenclatura-de-modelos)
- [API Docs](http://localhost:8001/docs)

---

**Última atualização**: 2025-11-12

