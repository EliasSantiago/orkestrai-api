# Guia de Migração - LiteLLM como Único Proxy

## 📢 Mudança Arquitetural Importante

**Data**: 12 de Novembro de 2025  
**Tipo**: Simplificação de Arquitetura  
**Impacto**: Baixo (compatibilidade retroativa mantida)

---

## O que mudou?

### Antes (Arquitetura Antiga)

```
LLMFactory
├── LiteLLMProvider (opcional)
├── OnPremiseProvider
├── OllamaProvider
├── ADKProvider (Gemini direto)
└── OpenAIProvider (OpenAI direto)
```

**Problema**: Múltiplos providers, código complexo, sem recursos avançados.

### Agora (Arquitetura Nova - RECOMENDADA)

```
LLMFactory
└── LiteLLMProvider (ÚNICO proxy unificado)
    └── Roteia para 100+ providers automaticamente
```

**Vantagens**:
- ✅ Um único ponto de controle
- ✅ Retries automáticos
- ✅ Load balancing
- ✅ Fallbacks configuráveis
- ✅ Cost tracking
- ✅ Observabilidade

---

## Preciso migrar?

### Resposta Curta: Não imediatamente

A mudança é **opt-in** e **retrocompatível**:

- ✅ Se você já usa `LITELLM_ENABLED=true`, não precisa fazer nada
- ✅ Se você usa providers legados, eles continuam funcionando
- ⚠️ Mas é **altamente recomendado** migrar para LiteLLM

### Resposta Longa: Sim, quando possível

Migrar para LiteLLM traz muitos benefícios. Veja como fazer isso.

---

## Como Migrar

### Passo 1: Habilitar LiteLLM

Edite o `.env`:

```bash
# Antes (ou ausente)
LITELLM_ENABLED=false

# Depois
LITELLM_ENABLED=true
```

### Passo 2: Atualizar Nomes dos Modelos

LiteLLM usa o formato `provider/modelo`:

#### Google Gemini

```python
# Antes (provider direto ADKProvider)
model = "gemini-2.0-flash-exp"
model = "gemini-1.5-pro"

# Depois (via LiteLLM)
model = "gemini/gemini-2.0-flash-exp"
model = "gemini/gemini-1.5-pro"
```

#### OpenAI

```python
# Antes (provider direto OpenAIProvider)
model = "gpt-4o"
model = "gpt-4o-mini"

# Depois (via LiteLLM)
model = "openai/gpt-4o"
model = "openai/gpt-4o-mini"
```

#### Ollama

```python
# Antes (provider direto OllamaProvider)
model = "llama2:latest"
model = "mistral:latest"

# Depois (via LiteLLM)
model = "ollama/llama2"
model = "ollama/mistral"
```

### Passo 3: Testar

```bash
python scripts/test_litellm_integration.py
```

Você deve ver:

```
✓ LiteLLM provider initialized (unified LLM gateway)
  → All models will be routed through LiteLLM
```

### Passo 4: Atualizar Agentes Existentes (Opcional)

Se você tem agentes criados com a nomenclatura antiga, pode atualizá-los:

```python
from src.database import SessionLocal
from src.models import AgentDB

db = SessionLocal()

# Buscar agentes com nomenclatura antiga
agents = db.query(AgentDB).filter(
    AgentDB.model.like("gemini-%")  # Sem prefixo
).all()

for agent in agents:
    # Atualizar para formato LiteLLM
    if agent.model.startswith("gemini-"):
        agent.model = f"gemini/{agent.model}"
        print(f"Atualizado: {agent.name} → {agent.model}")
    
    elif agent.model.startswith("gpt-"):
        agent.model = f"openai/{agent.model}"
        print(f"Atualizado: {agent.name} → {agent.model}")

db.commit()
db.close()
```

---

## Comparação de Código

### Criar Agente

#### Antes

```python
# Usando provider direto (ADKProvider)
agent = create_agent.execute(
    user_id=1,
    name="Assistente Gemini",
    model="gemini-2.0-flash-exp",  # Sem prefixo
    instruction="Você é um assistente útil.",
    tools=[]
)
```

#### Depois

```python
# Usando LiteLLM (recomendado)
agent = create_agent.execute(
    user_id=1,
    name="Assistente Gemini",
    model="gemini/gemini-2.0-flash-exp",  # Com prefixo
    instruction="Você é um assistente útil.",
    tools=[]
)
```

### Chat com Modelo

#### Antes

```python
# Provider selecionado automaticamente baseado no nome
provider = LLMFactory.get_provider("gemini-2.0-flash-exp")
# Retorna: ADKProvider

messages = [LLMMessage(role="user", content="Olá")]
async for chunk in provider.chat(messages=messages, model="gemini-2.0-flash-exp"):
    print(chunk, end="")
```

#### Depois

```python
# LiteLLM como único proxy
provider = LLMFactory.get_provider("gemini/gemini-2.0-flash-exp")
# Retorna: LiteLLMProvider (SEMPRE)

messages = [LLMMessage(role="user", content="Olá")]
async for chunk in provider.chat(messages=messages, model="gemini/gemini-2.0-flash-exp"):
    print(chunk, end="")
```

---

## Tabela de Conversão de Modelos

| Provider | Antes (Legado) | Depois (LiteLLM) |
|----------|----------------|------------------|
| **Google Gemini** | `gemini-2.0-flash-exp` | `gemini/gemini-2.0-flash-exp` |
| | `gemini-1.5-pro` | `gemini/gemini-1.5-pro` |
| | `gemini-1.5-flash` | `gemini/gemini-1.5-flash` |
| **OpenAI** | `gpt-4o` | `openai/gpt-4o` |
| | `gpt-4o-mini` | `openai/gpt-4o-mini` |
| | `gpt-3.5-turbo` | `openai/gpt-3.5-turbo` |
| **Anthropic** | ❌ Não suportado | `anthropic/claude-3-opus-20240229` |
| | ❌ Não suportado | `anthropic/claude-3-sonnet-20240229` |
| **Ollama** | `llama2:latest` | `ollama/llama2` |
| | `mistral:latest` | `ollama/mistral` |
| | `codellama:latest` | `ollama/codellama` |

---

## Compatibilidade Retroativa

### Modelos Legados Ainda Funcionam?

**Sim**, mas apenas se LiteLLM estiver desabilitado ou falhar:

```bash
# Se você mantiver LITELLM_ENABLED=false
# Os providers legados (ADK, OpenAI, etc.) serão usados
LITELLM_ENABLED=false
```

Neste caso:
- `gemini-2.0-flash-exp` → ADKProvider
- `gpt-4o` → OpenAIProvider
- `llama2:latest` → OllamaProvider

**Mas**: Você perde todos os benefícios do LiteLLM (retries, fallbacks, observabilidade, etc.)

### Recomendação

🎯 **Migre para LiteLLM** quando possível. É mais robusto e oferece recursos muito superiores.

---

## Checklist de Migração

Use este checklist para verificar sua migração:

- [ ] `LITELLM_ENABLED=true` configurado no `.env`
- [ ] API keys configuradas (GOOGLE_API_KEY, OPENAI_API_KEY, etc.)
- [ ] Arquivo `litellm_config.yaml` presente na raiz
- [ ] Script de teste executado com sucesso (`python scripts/test_litellm_integration.py`)
- [ ] Modelos atualizados para formato `provider/modelo`
- [ ] Agentes existentes atualizados (opcional)
- [ ] Testes de integração passando
- [ ] Documentação revisada

---

## Recursos Novos Disponíveis

Ao migrar para LiteLLM, você ganha acesso a:

### 1. Retries Automáticos

```bash
# Configure no .env
LITELLM_NUM_RETRIES=3
```

### 2. Load Balancing

```yaml
# Configure no litellm_config.yaml
model_list:
  - model_name: gpt-4o
    litellm_params:
      model: openai/gpt-4o
      api_key: os.environ/OPENAI_KEY_1
  
  - model_name: gpt-4o
    litellm_params:
      model: openai/gpt-4o
      api_key: os.environ/OPENAI_KEY_2

router_settings:
  routing_strategy: "least-busy"
```

### 3. Fallbacks

```yaml
router_settings:
  model_group_alias:
    smart-model:
      - gpt-4o           # Tenta primeiro
      - gpt-4-turbo      # Se falhar
      - gpt-3.5-turbo    # Último recurso
```

### 4. Observabilidade

```bash
# Integração com Langfuse, MLflow, etc.
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
```

```yaml
general_settings:
  success_callback: ["langfuse"]
```

### 5. Caching

```yaml
general_settings:
  cache: true
  cache_params:
    type: "redis"
    ttl: 3600
```

---

## FAQ

### Q: Posso usar LiteLLM e providers legados ao mesmo tempo?

**R**: Tecnicamente sim (os legados são fallback), mas não é recomendado. Use apenas LiteLLM para simplicidade.

### Q: Preciso recriar meus agentes?

**R**: Não, mas você pode atualizar os nomes dos modelos para o formato LiteLLM.

### Q: O que acontece se LiteLLM falhar?

**R**: Os providers legados são ativados automaticamente como fallback. Mas isso raramente deve acontecer.

### Q: Posso voltar para a arquitetura antiga?

**R**: Sim, basta configurar `LITELLM_ENABLED=false`. Mas você perde os benefícios do LiteLLM.

### Q: Quais providers são suportados?

**R**: 100+ providers incluindo: Gemini, OpenAI, Claude, Ollama, Azure, Cohere, HuggingFace, e muito mais.

---

## Suporte

Se você tiver problemas durante a migração:

1. Consulte: [TROUBLESHOOTING.md](./TROUBLESHOOTING.md)
2. Execute: `python scripts/test_litellm_integration.py`
3. Verifique logs com: `LITELLM_VERBOSE=true`
4. Leia a documentação: https://docs.litellm.ai/docs/

---

## Timeline Recomendada

- **Imediato**: Configure `LITELLM_ENABLED=true` para novos deployments
- **Curto prazo (1-2 semanas)**: Atualize modelos em agentes novos
- **Médio prazo (1 mês)**: Migre agentes existentes
- **Longo prazo (3 meses)**: Considere remover providers legados (se não houver uso)

---

**Última atualização**: 2025-11-12  
**Versão**: 2.0.0 (Arquitetura simplificada com LiteLLM único)

