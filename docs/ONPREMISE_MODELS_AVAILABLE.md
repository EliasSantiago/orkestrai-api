# Modelos On-Premise Disponíveis

Lista atualizada dos modelos disponíveis na API on-premise em **11/11/2025**.

## 📦 Modelos Disponíveis

### Modelos de Código (Code Models)

| Modelo | Tamanho | Descrição |
|--------|---------|-----------|
| `qwen3-coder:30b` | 30B | Qwen3 Coder - Especializado em programação |

### Modelos de Raciocínio (Reasoning Models)

| Modelo | Tamanho | Descrição |
|--------|---------|-----------|
| `deepseek-r1:14b` | 14B | DeepSeek R1 - Raciocínio avançado |
| `deepseek-r1:8b` | 8B | DeepSeek R1 - Versão menor |
| `deepseek-r1:1.5b-qwen-distill-fp16` | 1.5B | DeepSeek R1 distilado (FP16) |

### Modelos Qwen (Qwen Family)

| Modelo | Tamanho | Quantização | Descrição |
|--------|---------|-------------|-----------|
| `qwen3:30b-a3b-instruct-2507-q4_K_M` | 30B | Q4_K_M | Qwen3 Instruct quantizado |
| `qwen3:30b-a3b-instruct-2507-fp16` | 30B | FP16 | Qwen3 Instruct precisão total |
| `qwen3:14b` | 14B | - | Qwen3 base |
| `qwen2.5:7b-instruct-fp16` | 7B | FP16 | Qwen 2.5 Instruct |
| `qwen2.5:14b` | 14B | - | Qwen 2.5 base |

### Modelos Gemma (Google Gemma)

| Modelo | Tamanho | Quantização | Descrição |
|--------|---------|-------------|-----------|
| `gemma3:27b-it-q4_K_M` | 27B | Q4_K_M | Gemma3 Instruct quantizado |
| `gemma3:12b-it-fp16` | 12B | FP16 | Gemma3 Instruct precisão total |
| `gemma3:12b-it-q4_K_M` | 12B | Q4_K_M | Gemma3 Instruct quantizado |
| `gemma3:12b` | 12B | - | Gemma3 base |
| `gemma3:latest` | - | - | Gemma3 versão mais recente |

### Modelos Llama (Meta Llama)

| Modelo | Tamanho | Quantização | Descrição |
|--------|---------|-------------|-----------|
| `llama3.1:8b-instruct-fp16` | 8B | FP16 | Llama 3.1 Instruct precisão total |
| `llama3.1:8b` | 8B | - | Llama 3.1 base |
| `llama3.2:3b` | 3B | - | Llama 3.2 compacto |

### Outros Modelos

| Modelo | Tamanho | Descrição |
|--------|---------|-----------|
| `gpt-oss:20b` | 20B | GPT Open Source |
| `phi4:14b` | 14B | Microsoft Phi-4 |
| `nomic-embed-text:latest` | - | Modelo de embeddings |

## 🎯 Como Usar os Modelos

### 1. Modelo Recomendado para Uso Geral

**`qwen3:30b-a3b-instruct-2507-q4_K_M`** - Bom equilíbrio entre qualidade e velocidade

```bash
curl -X POST http://localhost:8001/api/agents \
  -H "Authorization: Bearer SEU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Assistente Geral",
    "description": "Assistente versátil para diversas tarefas",
    "model": "qwen3:30b-a3b-instruct-2507-q4_K_M",
    "instruction": "Você é um assistente útil que responde em português brasileiro.",
    "tools": ["calculator", "get_current_time"]
  }'
```

### 2. Modelo para Programação

**`qwen3-coder:30b`** - Especializado em código

```bash
curl -X POST http://localhost:8001/api/agents \
  -H "Authorization: Bearer SEU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Assistente de Programação",
    "description": "Especialista em código e desenvolvimento",
    "model": "qwen3-coder:30b",
    "instruction": "Você é um expert em programação. Ajude com código, debugging e boas práticas.",
    "tools": []
  }'
```

### 3. Modelo Rápido e Leve

**`llama3.2:3b`** - Menor e mais rápido

```bash
curl -X POST http://localhost:8001/api/agents \
  -H "Authorization: Bearer SEU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Assistente Rápido",
    "description": "Respostas rápidas para tarefas simples",
    "model": "llama3.2:3b",
    "instruction": "Você é um assistente rápido e direto. Seja conciso nas respostas.",
    "tools": []
  }'
```

### 4. Modelo para Raciocínio Complexo

**`deepseek-r1:14b`** - Melhor para problemas complexos

```bash
curl -X POST http://localhost:8001/api/agents \
  -H "Authorization: Bearer SEU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Assistente de Raciocínio",
    "description": "Especialista em problemas complexos e análise profunda",
    "model": "deepseek-r1:14b",
    "instruction": "Você é um especialista em resolver problemas complexos. Analise profundamente antes de responder.",
    "tools": ["calculator"]
  }'
```

### 5. Modelo Premium (Alta Qualidade)

**`gemma3:27b-it-q4_K_M`** - Melhor qualidade

```bash
curl -X POST http://localhost:8001/api/agents \
  -H "Authorization: Bearer SEU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Assistente Premium",
    "description": "Respostas de alta qualidade para tarefas importantes",
    "model": "gemma3:27b-it-q4_K_M",
    "instruction": "Você é um assistente de elite. Forneça respostas detalhadas e precisas.",
    "tools": ["calculator", "get_current_time"]
  }'
```

## 📊 Comparação de Modelos

### Por Tamanho

| Categoria | Modelos | Uso Recomendado |
|-----------|---------|-----------------|
| **Pequeno (1.5-3B)** | `llama3.2:3b`, `deepseek-r1:1.5b-qwen-distill-fp16` | Respostas rápidas, tarefas simples |
| **Médio (7-8B)** | `qwen2.5:7b-instruct-fp16`, `llama3.1:8b`, `deepseek-r1:8b` | Uso geral, bom equilíbrio |
| **Grande (12-14B)** | `gemma3:12b`, `qwen3:14b`, `phi4:14b`, `deepseek-r1:14b` | Tarefas complexas, alta qualidade |
| **Extra Grande (20-30B)** | `gpt-oss:20b`, `qwen3:30b`, `gemma3:27b`, `qwen3-coder:30b` | Máxima qualidade, tarefas críticas |

### Por Velocidade vs Qualidade

```
Rápido          ←→          Qualidade
────────────────────────────────────────
llama3.2:3b
├─ qwen2.5:7b-instruct-fp16
├─ llama3.1:8b
├─ gemma3:12b-it-q4_K_M (quantizado)
├─ qwen3:14b
├─ deepseek-r1:14b
├─ gpt-oss:20b
├─ gemma3:27b-it-q4_K_M
└─ qwen3:30b-a3b-instruct-2507-fp16 (FP16 máxima qualidade)
```

### Por Especialização

| Especialização | Modelos Recomendados |
|----------------|---------------------|
| **Programação** | `qwen3-coder:30b` |
| **Raciocínio** | `deepseek-r1:14b`, `deepseek-r1:8b` |
| **Uso Geral** | `qwen3:30b-a3b-instruct-2507-q4_K_M`, `gemma3:12b-it-fp16`, `llama3.1:8b-instruct-fp16` |
| **Multilíngue** | `qwen3:30b`, `qwen2.5:7b` |
| **Rápido/Leve** | `llama3.2:3b`, `deepseek-r1:1.5b-qwen-distill-fp16` |

## 🔍 Entendendo Quantização

### Tipos de Quantização

- **FP16** (Float16): Precisão máxima, maior tamanho e uso de memória
- **Q4_K_M** (4-bit): Boa qualidade, menor tamanho (~75% menor que FP16)
- **Q4_K_S** (4-bit Small): Ainda menor, ligeira perda de qualidade

### Quando Usar Cada Tipo

| Tipo | Velocidade | Qualidade | Memória | Uso Recomendado |
|------|-----------|-----------|---------|-----------------|
| **FP16** | ⭐⭐ | ⭐⭐⭐⭐⭐ | Alta | Tarefas críticas |
| **Q4_K_M** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Média | Uso geral (recomendado) |
| **Base** | ⭐⭐⭐ | ⭐⭐⭐ | Variável | Depende do modelo |

## ⚠️ Importante: Conflitos de Nomes

### ✅ Sem Conflito

Todos os modelos on-premise têm `:` no nome, o que evita conflitos:

- `gemma3:12b` → **On-Premise** ✅
- `gemini-2.0-flash` → **Google Gemini API** ✅
- `llama3.1:8b` → **On-Premise** ✅
- `gpt-oss:20b` → **On-Premise** ✅
- `gpt-4o` → **OpenAI API** ✅

### Regra de Detecção

O sistema detecta automaticamente:

1. **Com `:` (dois-pontos)** → On-Premise
2. **Prefixo `gemini-`** → Google Gemini
3. **Prefixo `gpt-4`, `gpt-3.5`** (sem `:`) → OpenAI
4. **Prefixo `local-` ou `onpremise-`** → On-Premise

## 🚀 Script: Criar Agentes para Todos os Modelos

```python
#!/usr/bin/env python3
"""Cria agentes para cada modelo disponível na API on-premise."""

import requests

API_URL = "http://localhost:8001"
TOKEN = "SEU_TOKEN_AQUI"

MODELS = {
    "Programação": "qwen3-coder:30b",
    "Raciocínio": "deepseek-r1:14b",
    "Geral Premium": "qwen3:30b-a3b-instruct-2507-q4_K_M",
    "Rápido": "llama3.2:3b",
    "Alta Qualidade": "gemma3:27b-it-q4_K_M",
}

for name, model in MODELS.items():
    response = requests.post(
        f"{API_URL}/api/agents",
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Content-Type": "application/json"
        },
        json={
            "name": f"Assistente {name}",
            "description": f"Agente usando {model}",
            "model": model,
            "instruction": "Você é um assistente útil em português brasileiro.",
            "tools": ["calculator", "get_current_time"]
        }
    )
    
    if response.status_code == 201:
        agent = response.json()
        print(f"✅ Criado: {agent['name']} (ID: {agent['id']})")
    else:
        print(f"❌ Erro ao criar {name}: {response.text}")
```

## 📚 Recursos Adicionais

- **Endpoint da API**: `https://apidesenv.go.gov.br/ia/modelos-linguagem-natural/v2.0/`
- **Endpoint de Chat**: `/chat`
- **Endpoint de Modelos**: `/models`
- **Autenticação**: OAuth 2.0 (client_credentials)

## 🆘 Suporte

Se um modelo não estiver funcionando:

1. Verifique se está na lista de modelos disponíveis
2. Confirme que o nome está escrito corretamente (case-sensitive)
3. Use o formato exato com `:` (ex: `qwen3:30b`, não `qwen3-30b`)
4. Verifique os logs da aplicação para detalhes do erro

---

**Última atualização**: 11/11/2025

