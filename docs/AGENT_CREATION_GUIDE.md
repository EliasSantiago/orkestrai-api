# Guia de Criação de Agentes

Este guia explica como criar agentes usando a API, incluindo exemplos completos de payloads.

## 📋 Tools Disponíveis

As seguintes tools estão disponíveis para uso nos agentes:

1. **`calculator`** - Calculadora matemática
   - Calcula expressões matemáticas de forma segura
   - Exemplo de uso: `calculator("25 * 4 + 10")`

2. **`get_current_time`** - Informações de data/hora
   - Retorna a hora atual em qualquer timezone
   - **Importante**: Requer o parâmetro `timezone` (ex: "America/Sao_Paulo", "UTC")
   - Exemplo de uso: `get_current_time("America/Sao_Paulo")`
   - Se o timezone não for fornecido, usa "America/Sao_Paulo" como padrão

## 📝 Exemplos de Payloads

### Exemplo 1: Agente Calculadora

```json
{
  "name": "Calculadora",
  "description": "Agente especializado em cálculos matemáticos e operações numéricas",
  "instruction": "Você é um assistente especializado em cálculos matemáticos. Quando receber uma expressão matemática, use a ferramenta 'calculator' para calcular o resultado. Apresente o resultado de forma clara e explique o processo quando for educacional. Seja preciso e use português brasileiro.",
  "model": "gemini-2.0-flash-exp",
  "tools": [
    "calculator"
  ]
}
```

### Exemplo 2: Agente de Horário

```json
{
  "name": "Agente de Horário",
  "description": "Fornece informações sobre data e hora em diferentes timezones",
  "instruction": "Você é um assistente que fornece informações sobre data e hora. Quando o usuário perguntar sobre a hora atual, use a ferramenta 'get_current_time' para obter essas informações. Sempre informe o timezone quando relevante. Seja claro e use português brasileiro.",
  "model": "gemini-2.0-flash",
  "tools": [
    "get_current_time"
  ]
}
```

### Exemplo 3: Agente Completo (com múltiplas tools)

```json
{
  "name": "Assistente Completo",
  "description": "Agente versátil que pode realizar cálculos e informar a hora",
  "instruction": "Você é um assistente útil e versátil. Você pode:\n1. Realizar cálculos matemáticos usando a ferramenta 'calculator'\n2. Informar a hora atual em qualquer timezone usando a ferramenta 'get_current_time'\n\nSeja amigável, prestativo e use português brasileiro. Sempre explique o que está fazendo.",
  "model": "gemini-2.0-flash",
  "tools": [
    "calculator",
    "get_current_time"
  ]
}
```

### Exemplo 4: Agente Simples (sem tools)

```json
{
  "name": "Assistente Conversacional",
  "description": "Agente para conversas e perguntas gerais",
  "instruction": "Você é um assistente amigável e prestativo. Responda às perguntas dos usuários de forma clara e útil. Use português brasileiro e seja sempre educado.",
  "model": "gemini-2.0-flash",
  "tools": []
}
```

## 🔧 Campos do Payload

### `name` (obrigatório)
- **Tipo**: String
- **Descrição**: Nome do agente
- **Exemplo**: `"Calculadora"`

### `description` (opcional)
- **Tipo**: String
- **Descrição**: Descrição breve do que o agente faz
- **Exemplo**: `"Agente especializado em cálculos matemáticos"`

### `instruction` (obrigatório)
- **Tipo**: String
- **Descrição**: Instruções detalhadas para o agente (system prompt)
- **Importante**: Explique quando e como usar cada tool
- **Exemplo**: `"Você é um assistente especializado em cálculos. Use a tool 'calculator' quando receber expressões matemáticas."`

### `model` (opcional, padrão: "gemini-2.0-flash-exp")
- **Tipo**: String
- **Descrição**: Modelo LLM a ser usado
- **Valores disponíveis**:
  - `"gemini-2.0-flash-exp"` (padrão)
  - `"gemini-1.5-pro"`
  - `"gemini-1.5-flash"`

### `tools` (opcional, padrão: [])
- **Tipo**: Array de strings
- **Descrição**: Lista de nomes das tools disponíveis
- **Valores disponíveis**:
  - `"calculator"` - Calculadora matemática
  - `"get_current_time"` - Informações de data/hora
- **Exemplo**: `["calculator", "get_current_time"]`
- **Importante**: Você deve passar apenas o **nome da função** da tool, não o objeto completo

## ✅ Como Passar as Tools

**SIM, você deve passar apenas o nome da tool como string!**

As tools são armazenadas como um array de strings com os nomes das funções. O sistema reconhecerá esses nomes e carregará as tools correspondentes quando o agente for executado.

**Formato correto:**
```json
{
  "tools": ["calculator", "get_current_time"]
}
```

**Formato incorreto:**
```json
{
  "tools": [
    {
      "name": "calculator",
      "function": "..."
    }
  ]
}
```

## 📝 Exemplo Completo de Requisição

### Via cURL

```bash
curl -X POST "http://localhost:8001/api/agents" \
  -H "Authorization: Bearer SEU_TOKEN_AQUI" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Minha Calculadora",
    "description": "Calculadora matemática personalizada",
    "instruction": "Você é uma calculadora matemática. Use a tool calculator para resolver expressões. Seja claro e mostre os passos.",
    "model": "gemini-2.0-flash-exp",
    "tools": ["calculator"]
  }'
```

### Via Swagger UI

1. Faça login em `/api/auth/login` para obter o token
2. Clique em "Authorize" e cole o token
3. Acesse `POST /api/agents`
4. Preencha o payload com os dados acima
5. Clique em "Execute"

## 💡 Dicas para Escrever Instructions

1. **Seja específico**: Explique claramente quando usar cada tool
2. **Mencione as tools**: Referencie as tools pelo nome na instruction
3. **Defina o tom**: Especifique se o agente deve ser formal, casual, educativo, etc.
4. **Idioma**: Especifique o idioma (português brasileiro)
5. **Exemplos**: Inclua exemplos de quando usar cada tool

### Boa Instruction (com tools)
```
Você é um assistente matemático. 
Quando receber uma expressão matemática, use a tool 'calculator' para calcular o resultado.
Apresente o resultado de forma clara e explique os passos quando for educacional.
Use português brasileiro.
```

### Má Instruction
```
Você é um assistente.
```

## 🎯 Resumo

- **Tools**: Passe apenas os nomes como strings no array: `["calculator", "get_current_time"]`
- **Instruction**: Seja detalhado e explique quando usar cada tool
- **Model**: Use `gemini-2.0-flash-exp` (padrão) ou outro modelo disponível
- **Description**: Opcional, mas ajuda a organizar seus agentes

