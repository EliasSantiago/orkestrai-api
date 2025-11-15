# 🤖 Guia Completo de Agentes

## 📋 Tools Disponíveis

### 1. `calculator`
Calculadora matemática que calcula expressões de forma segura.

**Exemplo de uso no agente:**
```python
tools=["calculator"]
```

### 2. `get_current_time`
Retorna informações de data/hora em qualquer timezone.

**Exemplo de uso no agente:**
```python
tools=["get_current_time"]
```

---

## 📝 Criando Agentes

### Via API REST (Recomendado)

1. **Faça login**: `POST /api/auth/login`
2. **Crie agente**: `POST /api/agents`

### Exemplo: Agente Calculadora

```json
{
  "name": "Calculadora",
  "description": "Agente especializado em cálculos matemáticos",
  "instruction": "Você é um assistente especializado em cálculos matemáticos. Quando receber uma expressão matemática, use a ferramenta 'calculator' para calcular o resultado. Apresente o resultado de forma clara e use português brasileiro.",
  "model": "gemini-2.0-flash-exp",
  "tools": ["calculator"]
}
```

### Exemplo: Agente de Horário

```json
{
  "name": "Agente de Horário",
  "description": "Fornece informações sobre data e hora",
  "instruction": "Você é um assistente que fornece informações sobre data e hora. Quando o usuário perguntar sobre a hora atual, use a ferramenta 'get_current_time' para obter essas informações. Sempre informe o timezone quando relevante. Use português brasileiro.",
  "model": "gemini-2.0-flash-exp",
  "tools": ["get_current_time"]
}
```

### Exemplo: Agente Completo

```json
{
  "name": "Assistente Completo",
  "description": "Agente versátil com múltiplas ferramentas",
  "instruction": "Você é um assistente útil e versátil. Você pode:\n1. Realizar cálculos matemáticos usando 'calculator'\n2. Informar a hora atual usando 'get_current_time'\n\nSeja amigável e use português brasileiro.",
  "model": "gemini-2.0-flash-exp",
  "tools": ["calculator", "get_current_time"]
}
```

---

## 🔧 Campos do Payload

### `name` (obrigatório)
Nome do agente.

### `description` (opcional)
Descrição breve do que o agente faz.

### `instruction` (obrigatório)
Instruções detalhadas para o agente (system prompt). **Importante**: Explique quando usar cada tool.

### `model` (opcional, padrão: "gemini-2.0-flash-exp")
Modelo LLM:
- `gemini-2.0-flash-exp` (padrão)
- `gemini-1.5-pro`
- `gemini-1.5-flash`

### `tools` (opcional, padrão: [])
Array de strings com nomes das tools:
- `"calculator"`
- `"get_current_time"`

**Formato correto:**
```json
{
  "tools": ["calculator", "get_current_time"]
}
```

---

## 💡 Dicas para Escrever Instructions

1. **Seja específico**: Explique claramente quando usar cada tool
2. **Mencione as tools**: Referencie as tools pelo nome
3. **Defina o tom**: Formal, casual, educativo, etc.
4. **Idioma**: Especifique português brasileiro
5. **Exemplos**: Inclua exemplos de quando usar cada tool

### ✅ Boa Instruction

```
Você é um assistente matemático. 
Quando receber uma expressão matemática, use a tool 'calculator' para calcular o resultado.
Apresente o resultado de forma clara e explique os passos quando for educacional.
Use português brasileiro.
```

### ❌ Má Instruction

```
Você é um assistente.
```

---

## 🔄 Como Funcionam os Agentes

### Sistema de Carregamento

1. **Agentes são armazenados** no PostgreSQL
2. **Ao iniciar ADK Web**, agentes são sincronizados automaticamente
3. **Arquivos Python são gerados** dinamicamente em `.agents_db/`
4. **ADK Web carrega** os agentes gerados

### Estrutura Gerada

```
.agents_db/
  agents/
    db_agents/
      agent.py      # Gerado automaticamente
      __init__.py
```

---

## 🎯 Usando Agentes

### Via API REST

```bash
POST /api/agents/chat
{
  "message": "Quanto é 25 * 4?",
  "agent_id": 1,
  "session_id": "sessao123"
}
```

### Via ADK Web

1. Inicie: `./scripts/start_adk_web.sh`
2. Acesse: http://localhost:8000
3. Selecione o agente
4. Inicie conversa

---

## 📚 Mais Informações

- Consulte [Referência da API](api-reference.md) para detalhes dos endpoints
- Consulte [Contexto Redis](redis-conversations.md) para usar contexto conversacional

