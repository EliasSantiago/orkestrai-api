# Troubleshooting: Roteamento de Modelos

Este documento ajuda a resolver problemas de roteamento de modelos entre diferentes providers.

## 🔍 Problema: Modelo On-Premise sendo roteado para OpenAI

### Sintoma

Erro ao usar modelo on-premise (ex: `gpt-oss:20b`):
```
Error code: 404 - The model `gpt-oss:20b` does not exist or you do not have access to it.
```

### Causa

O modelo está sendo roteado para o provider errado. Por exemplo, `gpt-oss:20b` está indo para `OpenAIProvider` em vez de `OnPremiseProvider`.

### Solução

#### 1. Verificar Configuração

Certifique-se de que `ONPREMISE_API_BASE_URL` está configurado no `.env`:

```env
ONPREMISE_API_BASE_URL=https://apidesenv.go.gov.br/ia/modelos-linguagem-natural/v2.0/
```

#### 2. Verificar Roteamento

Teste qual provider está sendo usado:

```python
from src.core.llm_factory import LLMFactory

model = "gpt-oss:20b"
provider = LLMFactory.get_provider(model)
print(f"Provider: {provider.__class__.__name__}")
```

**Esperado:** `OnPremiseProvider`

#### 3. Padrões de Nomenclatura

O sistema detecta modelos on-premise pelos seguintes padrões:

- ✅ Modelos com `:` (ex: `gpt-oss:20b`, `llama-2:7b`)
- ✅ Modelos com prefixo `local-` (ex: `local-llama`)
- ✅ Modelos com prefixo `onpremise-` (ex: `onpremise-model`)
- ✅ Modelos na lista `ONPREMISE_MODELS` (se configurado)

#### 4. Configurar Lista de Modelos (Opcional)

Se quiser validação antecipada, configure:

```env
ONPREMISE_MODELS=gpt-oss:20b,llama-2:7b,outro-modelo
```

## 📋 Como o Roteamento Funciona

### Ordem de Verificação

1. **OnPremiseProvider** (verificado primeiro)
   - Aceita modelos com `:`, `local-`, `onpremise-`
   - Ou modelos na lista `ONPREMISE_MODELS`
   - Rejeita modelos conhecidos OpenAI/Gemini

2. **ADKProvider** (Gemini)
   - Aceita modelos que começam com `gemini-`

3. **OpenAIProvider** (verificado por último)
   - Aceita modelos conhecidos OpenAI
   - Rejeita modelos com `:` (indica on-premise)

### Exemplos

| Modelo | Provider | Motivo |
|--------|----------|--------|
| `gpt-oss:20b` | OnPremise | Tem `:` |
| `gpt-4o` | OpenAI | Modelo conhecido OpenAI |
| `gpt-4o-mini` | OpenAI | Modelo conhecido OpenAI |
| `gemini-2.0-flash-exp` | ADK | Começa com `gemini-` |
| `local-llama` | OnPremise | Prefixo `local-` |
| `llama-2:7b` | OnPremise | Tem `:` |

## ✅ Checklist de Verificação

- [ ] `ONPREMISE_API_BASE_URL` está configurado no `.env`
- [ ] `ONPREMISE_TOKEN_URL` está configurado (se usar OAuth)
- [ ] `ONPREMISE_CONSUMER_KEY` e `ONPREMISE_CONSUMER_SECRET` estão configurados (se usar OAuth)
- [ ] Modelo tem indicador on-premise (`:`, `local-`, `onpremise-`)
- [ ] Provider está sendo inicializado (verifique logs)

## 🔧 Debug

### Verificar Providers Disponíveis

```python
from src.core.llm_factory import LLMFactory

providers = LLMFactory._get_providers()
for provider in providers:
    print(f"Provider: {provider.__class__.__name__}")
```

### Verificar Modelo Específico

```python
from src.core.llm_factory import LLMFactory

model = "gpt-oss:20b"
is_supported = LLMFactory.is_model_supported(model)
provider = LLMFactory.get_provider(model)

print(f"Modelo: {model}")
print(f"Suportado: {is_supported}")
print(f"Provider: {provider.__class__.__name__ if provider else 'None'}")
```

### Verificar Todos os Modelos Suportados

```bash
curl http://localhost:8001/api/models
```

## 🐛 Problemas Comuns

### Problema 1: "Model not found" mesmo sendo on-premise

**Causa:** Provider on-premise não está configurado ou não está sendo inicializado.

**Solução:**
1. Verifique se `ONPREMISE_API_BASE_URL` está no `.env`
2. Reinicie a aplicação
3. Verifique logs para erros de inicialização

### Problema 2: Modelo on-premise indo para OpenAI

**Causa:** Modelo não tem indicador on-premise claro.

**Solução:**
1. Use `:` no nome (ex: `gpt-oss:20b`)
2. Use prefixo `local-` ou `onpremise-`
3. Configure `ONPREMISE_MODELS` com o nome exato

### Problema 3: Modelo OpenAI indo para OnPremise

**Causa:** Nome do modelo confunde o sistema.

**Solução:**
- Use nomes padrão OpenAI (ex: `gpt-4o`, `gpt-4o-mini`)
- Evite usar `:` em modelos OpenAI

## 📚 Referências

- [Configuração On-Premise](docs/ONPREMISE_OAUTH_SETUP.md)
- [Modelos Suportados](docs/MULTI_PROVIDER_SETUP.md)

