# Guia Rápido: Criar Agente On-Premise

Guia prático com exemplos de JSON para criar agentes usando modelos on-premise.

## 🚀 Passo a Passo

### 1️⃣ Configure o `.env`

```env
# API On-Premise
ONPREMISE_API_BASE_URL=https://apidesenv.go.gov.br/ia/modelos-linguagem-natural/v2.0/
ONPREMISE_CHAT_ENDPOINT=/chat

# OAuth
ONPREMISE_TOKEN_URL=https://apidesenv.go.gov.br/token
ONPREMISE_CONSUMER_KEY=X1mgu5MTHdp6VxZEemXCLZ2FGloa
ONPREMISE_CONSUMER_SECRET=d1z8Pg2ZmHrZz9aFsuUlAFKRn7Aa
ONPREMISE_OAUTH_GRANT_TYPE=client_credentials

# SSL (desabilitar para desenvolvimento)
VERIFY_SSL=false
```

### 2️⃣ Faça Login na Aplicação

Use o endpoint `POST /api/login` para obter um token JWT.

### 3️⃣ Crie o Agente

Use o endpoint `POST /api/agents` com o JSON do agente.

## 📝 Exemplo Principal: Agente Completo (CORRIGIDO)

**JSON que você forneceu originalmente, agora corrigido:**

```json
{
  "name": "Assistente Completo",
  "description": "Agente versátil que pode realizar cálculos e informar a hora",
  "instruction": "Você é um assistente útil e versátil. Você pode:\n1. Realizar cálculos matemáticos usando a ferramenta 'calculator'\n2. Informar a hora atual em qualquer timezone usando a ferramenta 'get_current_time'\n\nSeja amigável, prestativo e use português brasileiro. Sempre explique o que está fazendo.",
  "model": "qwen3:30b-a3b-instruct-2507-q4_K_M",
  "tools": ["calculator", "get_current_time"]
}
```

**⚠️ MUDANÇAS IMPORTANTES:**

1. ✅ **Modelo alterado** de `"gemini-2.0-flash"` para `"qwen3:30b-a3b-instruct-2507-q4_K_M"`
   - `gemini-2.0-flash` → vai para Google Gemini API (não on-premise)
   - `qwen3:30b-a3b-instruct-2507-q4_K_M` → usa API on-premise ✅

2. ✅ **Ferramentas estão corretas:**
   - `calculator` ✅
   - `get_current_time` ✅

### 💡 **Uso Opcional de Prefixo Explícito**

Você também pode usar o prefixo `onpremise-` ou `local-` para forçar explicitamente o uso do provider on-premise:

```json
{
  "model": "onpremise-qwen3:30b-a3b-instruct-2507-q4_K_M"
}
```

**Quando usar o prefixo?**
- ✅ Para deixar explícito que é on-premise
- ✅ Em ambientes com múltiplos providers configurados
- ✅ Para debugging e testes
- ✅ Quando quiser garantir 100% que vai usar on-premise

**Prefixos suportados:**
- `onpremise-` → `onpremise-qwen3:30b`
- `local-` → `local-qwen3:30b`

**Ambos funcionam da mesma forma!**

## 🎯 Outros Exemplos de Modelos On-Premise

### Opção 1: Modelo Rápido e Leve

```json
{
  "name": "Assistente Rápido",
  "description": "Respostas rápidas para tarefas simples",
  "model": "llama3.2:3b",
  "instruction": "Você é um assistente rápido e direto.",
  "tools": []
}
```

### Opção 2: Especialista em Programação

```json
{
  "name": "Assistente de Código",
  "description": "Especialista em programação",
  "model": "qwen3-coder:30b",
  "instruction": "Você é um expert em programação. Ajude com código e debugging.",
  "tools": []
}
```

### Opção 3: Raciocínio Avançado

```json
{
  "name": "Assistente de Raciocínio",
  "description": "Especialista em problemas complexos",
  "model": "deepseek-r1:14b",
  "instruction": "Você é especialista em resolver problemas complexos.",
  "tools": ["calculator"]
}
```

### Opção 4: Alta Qualidade

```json
{
  "name": "Assistente Premium",
  "description": "Máxima qualidade nas respostas",
  "model": "gemma3:27b-it-q4_K_M",
  "instruction": "Você é um assistente de elite. Forneça respostas detalhadas.",
  "tools": ["calculator", "get_current_time"]
}
```

### Opção 5: GPT Open Source

```json
{
  "name": "Assistente GPT-OSS",
  "description": "Usando GPT Open Source",
  "model": "gpt-oss:20b",
  "instruction": "Você é um assistente útil em português brasileiro.",
  "tools": []
}
```

## ✅ Checklist Completo

### Configuração

- [ ] ✅ Arquivo `.env` configurado
- [ ] ✅ `ONPREMISE_API_BASE_URL` definida
- [ ] ✅ `ONPREMISE_CHAT_ENDPOINT=/chat` definido
- [ ] ✅ Credenciais OAuth configuradas
- [ ] ✅ `VERIFY_SSL=false` (se necessário)
- [ ] ✅ Servidor rodando (`python -m uvicorn src.api.main:app --reload --port 8001`)

### Autenticação

- [ ] ✅ Usuário criado no sistema
- [ ] ✅ Login realizado com sucesso
- [ ] ✅ Token JWT obtido e salvo

### Modelo

- [ ] ✅ Modelo escolhido da lista disponível
- [ ] ✅ Modelo usa formato com `:` (ex: `qwen3:30b`)
- [ ] ❌ **NÃO** usar `gemini-*` (vai para Google)
- [ ] ❌ **NÃO** usar `gpt-4o`, `gpt-3.5-turbo` (vai para OpenAI)

### Ferramentas

- [ ] ✅ `calculator` - para cálculos matemáticos
- [ ] ✅ `get_current_time` - para informações de tempo
- [ ] ❌ **NÃO** usar `"time"` (nome incorreto)

### Criação

- [ ] ✅ Endpoint correto (`POST /api/agents`)
- [ ] ✅ Header `Authorization` com Bearer token
- [ ] ✅ JSON válido no body
- [ ] ✅ Resposta HTTP 201 Created

## 🐛 Troubleshooting

### Problema: "gemini-2.0-flash não usa on-premise"

**Solução:** Modelos Gemini (com hífen `-`) usam Google API. Use modelos com `:` para on-premise.

```diff
- "model": "gemini-2.0-flash"  ❌
+ "model": "qwen3:30b-a3b-instruct-2507-q4_K_M"  ✅
```

### Problema: "Tool 'time' not found"

**Solução:** O nome correto da ferramenta é `get_current_time`.

```diff
- "tools": ["calculator", "time"]  ❌
+ "tools": ["calculator", "get_current_time"]  ✅
```

### Problema: "Modelo não encontrado"

**Solução:** Verifique a lista de modelos disponíveis usando o endpoint `GET /models` da API on-premise.

### Problema: "Erro 404 no chat endpoint"

**Solução:** Verifique se `ONPREMISE_CHAT_ENDPOINT=/chat` está no `.env`.

### Problema: "SSL Certificate Error"

**Solução:** Adicione no `.env`:

```env
VERIFY_SSL=false
```

⚠️ **ATENÇÃO:** Use `VERIFY_SSL=false` apenas em desenvolvimento!

## 📊 Tabela de Modelos por Uso

| Caso de Uso | Modelo Recomendado | Tamanho | Velocidade |
|-------------|-------------------|---------|-----------|
| **Uso Geral** | `qwen3:30b-a3b-instruct-2507-q4_K_M` | 30B | ⭐⭐⭐ |
| **Programação** | `qwen3-coder:30b` | 30B | ⭐⭐⭐ |
| **Rápido** | `llama3.2:3b` | 3B | ⭐⭐⭐⭐⭐ |
| **Raciocínio** | `deepseek-r1:14b` | 14B | ⭐⭐⭐⭐ |
| **Alta Qualidade** | `gemma3:27b-it-q4_K_M` | 27B | ⭐⭐⭐ |
| **Equilíbrio** | `gemma3:12b-it-fp16` | 12B | ⭐⭐⭐⭐ |

## 🚀 Como Usar os JSONs

1. **Via API REST:** Use o endpoint `POST /api/agents` com o JSON no body
2. **Via Interface Web:** Cole o JSON na interface de criação de agentes
3. **Via Swagger:** Acesse `http://localhost:8001/docs` e use o endpoint `/api/agents`

## 📚 Próximos Passos

1. ✅ Criar mais agentes com diferentes modelos
2. ✅ Testar diferentes ferramentas
3. ✅ Ajustar parâmetros (temperature, num_predict, etc.)
4. ✅ Integrar com interface web
5. ✅ Monitorar performance dos modelos

## 🎓 Dicas Importantes

1. **Sempre use modelos com `:` para on-premise**
   - ✅ `qwen3:30b`, `llama3.1:8b`, `gpt-oss:20b`
   - ❌ `gemini-2.0-flash`, `gpt-4o`

2. **Nomes corretos das ferramentas**
   - ✅ `calculator`, `get_current_time`
   - ❌ `time`, `calculator_tool`

3. **Configure OAuth corretamente**
   - Token expira após 1 hora
   - Sistema renova automaticamente

4. **Escolha o modelo adequado**
   - Rápido: `llama3.2:3b`
   - Balanceado: `qwen3:30b-a3b-instruct-2507-q4_K_M`
   - Qualidade: `gemma3:27b-it-q4_K_M`

---

**Pronto para começar! 🚀**

