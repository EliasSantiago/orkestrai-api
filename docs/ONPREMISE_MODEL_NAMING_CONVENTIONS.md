# Convenções de Nomenclatura para Modelos On-Premise

Guia completo sobre como nomear modelos on-premise e quando usar cada formato.

## 🎯 **Três Formas de Nomear Modelos**

### **1. Nome Real** (Recomendado)

Use o nome exato como retornado pela API on-premise:

```json
{
  "model": "qwen3:30b-a3b-instruct-2507-q4_K_M"
}
```

**Vantagens:**
- ✅ Nome real do modelo
- ✅ Mais limpo e conciso
- ✅ Segue convenção da indústria
- ✅ Facilita migração entre ambientes
- ✅ Detecção automática via `:` no nome

**Quando usar:**
- Uso geral (90% dos casos)
- Quando o nome já é único
- Em documentação e exemplos

### **2. Prefixo `onpremise-`** (Explícito)

Adicione o prefixo `onpremise-` ao nome do modelo:

```json
{
  "model": "onpremise-qwen3:30b-a3b-instruct-2507-q4_K_M"
}
```

**Vantagens:**
- ✅ Explícito e óbvio
- ✅ Garante 100% uso do provider on-premise
- ✅ Ótimo para debugging
- ✅ Útil em ambientes multi-provider

**Quando usar:**
- Ambientes com múltiplos providers
- Quando quer forçar on-premise
- Em testes e debugging
- Quando há conflito de nomes

### **3. Prefixo `local-`** (Alternativo)

Adicione o prefixo `local-` ao nome do modelo:

```json
{
  "model": "local-qwen3:30b-a3b-instruct-2507-q4_K_M"
}
```

**Vantagens:**
- ✅ Mais curto que `onpremise-`
- ✅ Mesma funcionalidade
- ✅ Indica hospedagem local

**Quando usar:**
- Preferência por nome mais curto
- Equivalente a `onpremise-`

## 📊 **Comparação Rápida**

| Formato | Exemplo | Tamanho | Clareza | Uso Recomendado |
|---------|---------|---------|---------|-----------------|
| **Nome Real** | `qwen3:30b` | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 90% dos casos |
| **onpremise-** | `onpremise-qwen3:30b` | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Multi-provider |
| **local-** | `local-qwen3:30b` | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Alternativa |

## 🎨 **Exemplos Práticos**

### **Exemplo 1: Uso Normal** (sem prefixo)

```json
{
  "name": "Assistente Geral",
  "model": "qwen3:30b-a3b-instruct-2507-q4_K_M",
  "instruction": "Você é um assistente útil.",
  "tools": []
}
```

✅ **Melhor para**: Uso diário, documentação, exemplos

### **Exemplo 2: Ambiente Complexo** (com prefixo)

```json
{
  "name": "Assistente On-Premise Explícito",
  "model": "onpremise-qwen3:30b-a3b-instruct-2507-q4_K_M",
  "instruction": "Você é um assistente que DEVE usar on-premise.",
  "tools": []
}
```

✅ **Melhor para**: Ambientes com Ollama + OnPremise configurados

### **Exemplo 3: Nome Curto** (com prefixo local-)

```json
{
  "name": "Assistente Local",
  "model": "local-llama3.2:3b",
  "instruction": "Assistente rápido e leve.",
  "tools": []
}
```

✅ **Melhor para**: Preferência por nomes mais curtos

## 🔍 **Como o Sistema Detecta**

### **Regras de Detecção (em ordem)**

1. **Prefixo Explícito** (prioridade máxima)
   ```
   onpremise-* → OnPremiseProvider
   local-* → OnPremiseProvider
   ```

2. **Dois-pontos no Nome**
   ```
   *:* → OnPremiseProvider (se on-premise está configurado)
   ```

3. **Prefixos de Outros Providers**
   ```
   gemini-* → Google Gemini
   gpt-4* → OpenAI (se não tem ":")
   ```

### **Fluxo de Decisão**

```
Modelo: "qwen3:30b"
    ↓
Tem "onpremise-" ou "local-"? NÃO
    ↓
OnPremise está configurado? SIM
    ↓
Tem ":" no nome? SIM
    ↓
✅ OnPremiseProvider
```

```
Modelo: "onpremise-qwen3:30b"
    ↓
Tem "onpremise-"? SIM
    ↓
✅ OnPremiseProvider (direto)
```

## 🚫 **Nomes que NÃO vão para On-Premise**

### **Modelos Google Gemini**
```
❌ gemini-2.0-flash → Google Gemini API
❌ gemini-1.5-pro → Google Gemini API
✅ gemma3:12b → On-Premise (note: gemma ≠ gemini)
```

### **Modelos OpenAI**
```
❌ gpt-4o → OpenAI API
❌ gpt-3.5-turbo → OpenAI API
✅ gpt-oss:20b → On-Premise (tem ":")
```

## 🎯 **Casos de Uso Específicos**

### **Caso 1: Ambiente de Desenvolvimento**

Use **nome real** para simplicidade:

```json
{
  "model": "llama3.2:3b"
}
```

### **Caso 2: Ambiente de Produção com Multi-Provider**

Use **prefixo explícito** para clareza:

```json
{
  "model": "onpremise-qwen3:30b-a3b-instruct-2507-q4_K_M"
}
```

### **Caso 3: Migração de Ambiente**

Use **nome real** para facilitar mudança:

```json
{
  "model": "qwen3:30b-a3b-instruct-2507-q4_K_M"
}
```

Trocar de on-premise para outro provider = só mudar config do `.env`

### **Caso 4: Debugging de Roteamento**

Use **prefixo explícito** para garantir provider:

```json
{
  "model": "onpremise-qwen3:30b-a3b-instruct-2507-q4_K_M"
}
```

Nos logs, verá claramente qual provider foi usado.

## 📝 **Recomendações por Cenário**

| Cenário | Recomendação | Exemplo |
|---------|--------------|---------|
| **Uso Normal** | Nome real | `qwen3:30b` |
| **Multi-Provider** | Com prefixo | `onpremise-qwen3:30b` |
| **Documentação** | Nome real | `qwen3:30b` |
| **Debug/Teste** | Com prefixo | `onpremise-qwen3:30b` |
| **Prod Crítico** | Com prefixo | `onpremise-qwen3:30b` |
| **Desenvolvimento** | Nome real | `qwen3:30b` |
| **CI/CD** | Nome real | `qwen3:30b` |

## 🔧 **Configuração Recomendada**

### **Opção A: Detecção Automática** (Recomendado)

```env
# .env
ONPREMISE_API_BASE_URL=https://apidesenv.go.gov.br/ia/modelos-linguagem-natural/v2.0/
ONPREMISE_CHAT_ENDPOINT=/chat
# ... outras configs
```

```json
{
  "model": "qwen3:30b-a3b-instruct-2507-q4_K_M"
}
```

✅ **Vantagens:**
- Detecção automática via `:`
- Código mais limpo
- Fácil migração

### **Opção B: Lista Explícita** (Mais Controle)

```env
# .env
ONPREMISE_API_BASE_URL=https://apidesenv.go.gov.br/ia/modelos-linguagem-natural/v2.0/
ONPREMISE_CHAT_ENDPOINT=/chat
ONPREMISE_MODELS=qwen3:30b-a3b-instruct-2507-q4_K_M,llama3.2:3b,gemma3:12b
# ... outras configs
```

```json
{
  "model": "qwen3:30b-a3b-instruct-2507-q4_K_M"
}
```

✅ **Vantagens:**
- Controle total sobre modelos aceitos
- Validação no backend
- Segurança adicional

### **Opção C: Prefixo Obrigatório** (Máxima Clareza)

```env
# .env - igual Opção A
```

```json
{
  "model": "onpremise-qwen3:30b-a3b-instruct-2507-q4_K_M"
}
```

✅ **Vantagens:**
- Zero ambiguidade
- Fácil identificar nos logs
- Ótimo para auditoria

## 🎓 **Boas Práticas**

### ✅ **Faça:**

1. **Use nomes reais** para uso geral
2. **Use prefixos** quando houver ambiguidade
3. **Documente** qual convenção seu projeto usa
4. **Seja consistente** na equipe
5. **Teste** o roteamento em desenvolvimento

### ❌ **Evite:**

1. **Misturar** convenções sem motivo
2. **Inventar** prefixos customizados
3. **Usar prefixos** desnecessariamente
4. **Esquecer** os dois-pontos (`:`)

## 🧪 **Testando Roteamento**

Use o script de teste:

```bash
python scripts/test_model_routing.py
```

Ou teste manualmente:

```python
from src.core.llm_factory import LLMFactory

# Teste 1: Nome real
provider = LLMFactory.get_provider("qwen3:30b")
print(provider.__class__.__name__)  # OnPremiseProvider

# Teste 2: Com prefixo
provider = LLMFactory.get_provider("onpremise-qwen3:30b")
print(provider.__class__.__name__)  # OnPremiseProvider

# Teste 3: Modelo Gemini
provider = LLMFactory.get_provider("gemini-2.0-flash")
print(provider.__class__.__name__)  # ADKProvider
```

## 📚 **Exemplos Completos**

### **Todos os 20 Modelos (3 formas)**

```json
// Forma 1: Nome Real (Recomendado)
{"model": "qwen3:30b-a3b-instruct-2507-q4_K_M"}
{"model": "deepseek-r1:14b"}
{"model": "llama3.1:8b-instruct-fp16"}
{"model": "gemma3:27b-it-q4_K_M"}
{"model": "phi4:14b"}

// Forma 2: Prefixo onpremise-
{"model": "onpremise-qwen3:30b-a3b-instruct-2507-q4_K_M"}
{"model": "onpremise-deepseek-r1:14b"}
{"model": "onpremise-llama3.1:8b-instruct-fp16"}
{"model": "onpremise-gemma3:27b-it-q4_K_M"}
{"model": "onpremise-phi4:14b"}

// Forma 3: Prefixo local-
{"model": "local-qwen3:30b-a3b-instruct-2507-q4_K_M"}
{"model": "local-deepseek-r1:14b"}
{"model": "local-llama3.1:8b-instruct-fp16"}
{"model": "local-gemma3:27b-it-q4_K_M"}
{"model": "local-phi4:14b"}
```

**Todas funcionam exatamente igual!** Escolha a que faz mais sentido para seu caso.

## 🎉 **Resumo**

| Pergunta | Resposta |
|----------|----------|
| **Qual usar na maioria dos casos?** | Nome real: `qwen3:30b` |
| **Quando usar prefixo?** | Multi-provider ou debugging |
| **`onpremise-` ou `local-`?** | Ambos funcionam igual |
| **Posso misturar?** | Sim, mas seja consistente |
| **Como testar?** | `scripts/test_model_routing.py` |
| **É obrigatório?** | Não, é opcional |

---

**Conclusão:** Use nomes reais para simplicidade, adicione prefixos quando precisar de clareza explícita! 🚀

