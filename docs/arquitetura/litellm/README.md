# LiteLLM - Gateway Unificado para LLMs

> **🎯 ARQUITETURA SIMPLIFICADA (v2.0 - 2025-11-12)**  
> LiteLLM é agora o **ÚNICO proxy** para todos os modelos LLM.  
> Mais simples. Mais poderoso. Mais recursos.

## 📚 Índice

1. [O que é LiteLLM?](#o-que-é-litellm)
2. [Por que usar LiteLLM?](#por-que-usar-litellm)
3. [Arquitetura da Integração](#arquitetura-da-integração)
4. [Configuração](#configuração)
5. [Guias Específicos](#guias-específicos)
6. [Referências](#referências)

## 🚨 Mudança Importante

**Nova arquitetura (v2.0)**: LiteLLM é o único proxy recomendado.  
**Migração**: Veja [MIGRATION_GUIDE.md](./MIGRATION_GUIDE.md)  
**Detalhes técnicos**: Veja [ARCHITECTURE_CHANGE.md](./ARCHITECTURE_CHANGE.md)

---

## O que é LiteLLM?

**LiteLLM** é uma biblioteca Python que fornece uma interface unificada para acessar **mais de 100 provedores de modelos LLM**, incluindo:

- ✅ **Google Gemini** (gemini-2.0-flash, gemini-1.5-pro, etc.)
- ✅ **OpenAI** (GPT-4o, GPT-4-turbo, GPT-3.5-turbo, etc.)
- ✅ **Anthropic Claude** (Claude 3 Opus, Sonnet, Haiku)
- ✅ **Ollama** (modelos locais como Llama, Mistral, Gemma)
- ✅ **Azure OpenAI**
- ✅ **Cohere**
- ✅ **HuggingFace**
- ✅ **Replicate**
- ✅ E mais de 90+ outros provedores...

### Características Principais

- 🔄 **Interface Unificada**: Use o mesmo código para todos os provedores
- 🔁 **Retries Automáticos**: Tenta novamente em caso de falha
- 📊 **Rastreamento de Custos**: Monitore quanto você está gastando
- ⚖️ **Load Balancing**: Distribua carga entre múltiplos modelos
- 🎯 **Fallback Logic**: Mude para modelo alternativo se o principal falhar
- 📝 **Logging & Observability**: Integração com Langfuse, Lunary, MLflow

---

## Por que usar LiteLLM?

### Antes do LiteLLM (Arquitetura Antiga)

```python
# Múltiplos providers, código complexo
if model.startswith("gpt"):
    provider = OpenAIProvider()
    response = await provider.chat(...)
elif model.startswith("gemini"):
    provider = ADKProvider()
    response = await provider.chat(...)
elif model.startswith("claude"):
    provider = AnthropicProvider()
    response = await provider.chat(...)
# ... e assim por diante
```

**Problemas:**
- ❌ Código duplicado para cada provider
- ❌ Difícil manutenção
- ❌ Sem retries automáticos
- ❌ Sem load balancing
- ❌ Sem fallbacks entre providers

### Depois do LiteLLM (Arquitetura Nova - RECOMENDADA)

```python
# Um único proxy para TUDO
from src.core.llm_factory import LLMFactory

# O LiteLLM roteia automaticamente para o provider correto
provider = LLMFactory.get_provider("gemini/gemini-2.0-flash-exp")
response = await provider.chat(messages=messages, model="gemini/gemini-2.0-flash-exp")

# Trocar de provider? Apenas mude o nome do modelo!
provider = LLMFactory.get_provider("openai/gpt-4o")
response = await provider.chat(messages=messages, model="openai/gpt-4o")
```

**Vantagens:**
- ✅ Um único proxy para 100+ providers
- ✅ Código limpo e unificado
- ✅ Retries automáticos
- ✅ Load balancing configurável
- ✅ Fallbacks entre modelos
- ✅ Cost tracking
- ✅ Observabilidade integrada

### Benefícios para o Projeto

1. **🚀 Simplicidade**: Um único provider para gerenciar
2. **🔄 Flexibilidade**: Troque de modelo/provider sem mudar código
3. **💪 Resiliência**: Retries automáticos e fallbacks configuráveis
4. **💰 Economia**: Compare custos e use modelos mais baratos
5. **⚖️ Escalabilidade**: Load balancing entre múltiplos endpoints
6. **📊 Observabilidade**: Logs, métricas e rastreamento unificados
7. **🛠️ Manutenibilidade**: Menos código para manter e testar

---

## Arquitetura da Integração

### Estrutura de Arquivos

```
api-adk-google-main/
├── litellm_config.yaml              # Configuração de modelos e providers
├── src/
│   ├── config.py                    # Configurações do LiteLLM
│   └── core/
│       ├── llm_factory.py           # Factory que inclui LiteLLMProvider
│       └── llm_providers/
│           └── litellm_provider.py  # Provider que usa LiteLLM
└── docs/
    └── arquitetura/
        └── litellm/                 # Esta documentação
            ├── README.md
            ├── SETUP.md
            ├── CONFIGURATION.md
            ├── USAGE.md
            └── TROUBLESHOOTING.md
```

### Fluxo de Funcionamento

```
┌─────────────┐
│   Request   │
│  (Agent)    │
└──────┬──────┘
       │
       v
┌──────────────────┐
│   LLMFactory     │ ◄── Roteia para LiteLLM (único proxy)
└──────┬───────────┘
       │
       v
┌──────────────────┐
│ LiteLLMProvider  │ ◄── Proxy unificado (ÚNICO provider ativo)
│   (ÚNICO)        │
└──────┬───────────┘
       │
       v
┌──────────────────┐
│    LiteLLM       │ ◄── Biblioteca que roteia para providers
│   (biblioteca)   │
└──────┬───────────┘
       │
       ├─────────────┬─────────────┬─────────────┬─────────────┐
       v             v             v             v             v
   ┌────────┐   ┌────────┐   ┌────────┐   ┌────────┐   ┌────────┐
   │ Gemini │   │ OpenAI │   │ Claude │   │ Ollama │   │ +100   │
   └────────┘   └────────┘   └────────┘   └────────┘   └────────┘
```

### Arquitetura Simplificada

**MUDANÇA ARQUITETURAL (2025-11-12):**

Agora usamos **APENAS o LiteLLM** como proxy unificado para todos os LLM providers.

#### ✅ Provider Único

**LiteLLMProvider** - ÚNICO proxy para TODOS os modelos
- ✅ Google Gemini (gemini-2.0-flash, gemini-1.5-pro, etc.)
- ✅ OpenAI (GPT-4o, GPT-4-turbo, GPT-3.5-turbo, etc.)
- ✅ Anthropic Claude (Claude 3 Opus, Sonnet, Haiku)
- ✅ Ollama (modelos locais: llama2, mistral, etc.)
- ✅ Azure OpenAI
- ✅ Cohere, HuggingFace, Replicate
- ✅ E mais 90+ outros providers

#### ❌ Providers Legados Removidos

Os providers antigos foram **completamente removidos**:
- ~~OnPremiseProvider~~ → Use `ollama/` ou custom providers via LiteLLM
- ~~OllamaProvider~~ → Use `ollama/modelo` via LiteLLM
- ~~ADKProvider~~ → Use `gemini/modelo` via LiteLLM
- ~~OpenAIProvider~~ → Use `openai/modelo` via LiteLLM

> **💡 Benefícios da arquitetura única:**
> - ✅ Código mais simples e limpo
> - ✅ Interface unificada para todos os providers
> - ✅ Retries automáticos
> - ✅ Load balancing configurável
> - ✅ Fallbacks entre modelos (configurável no YAML)
> - ✅ Cost tracking nativo
> - ✅ Observabilidade integrada

---

## Configuração

### 1. Variáveis de Ambiente

Adicione ao seu `.env`:

```bash
# Habilitar LiteLLM
LITELLM_ENABLED=true

# API Keys dos providers que você quer usar
GOOGLE_API_KEY=sua-chave-google
OPENAI_API_KEY=sua-chave-openai
ANTHROPIC_API_KEY=sua-chave-anthropic

# Ollama (se estiver rodando localmente)
OLLAMA_API_BASE_URL=http://localhost:11434

# Configurações opcionais
LITELLM_VERBOSE=false          # true para debug
LITELLM_NUM_RETRIES=3          # Número de tentativas
LITELLM_REQUEST_TIMEOUT=600    # Timeout em segundos (10 min)
```

### 2. Arquivo de Configuração

O arquivo `litellm_config.yaml` define os modelos disponíveis:

```yaml
model_list:
  - model_name: gemini-2.0-flash-exp
    litellm_params:
      model: gemini/gemini-2.0-flash-exp
      api_key: os.environ/GOOGLE_API_KEY
  
  - model_name: gpt-4o
    litellm_params:
      model: openai/gpt-4o
      api_key: os.environ/OPENAI_API_KEY
```

### 3. Instalação

```bash
# Instalar dependências (já incluído no requirements.txt)
pip install litellm>=1.50.0

# Ou reinstalar todas as dependências
pip install -r requirements.txt
```

---

## Guias Específicos

Para informações detalhadas sobre cada aspecto do LiteLLM, consulte:

### 📖 [SETUP.md](./SETUP.md)
- Instalação passo a passo
- Configuração inicial
- Testes de funcionamento

### ⚙️ [CONFIGURATION.md](./CONFIGURATION.md)
- Configuração avançada
- Customização de modelos
- Load balancing e fallbacks
- Integração com observability tools

### 💻 [USAGE.md](./USAGE.md)
- Como usar no código
- Exemplos práticos
- Criação de agentes com LiteLLM
- Testes e validação

### 🔧 [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) ⭐ NOVO
- Problemas comuns e soluções
- **SSL Certificate Verification Error** ← Solução para erro SSL
- Requested tools not found
- Invalid Model Error
- Connection Timeout
- API Key Invalid
- Debug mode

### 🚨 [SSL_FIX_GUIDE.md](./SSL_FIX_GUIDE.md) 🆘 RESOLVA AGORA
- **Guia rápido para corrigir erro SSL** (3 minutos)
- Passo a passo detalhado
- Configuração do VERIFY_SSL
- Solução para ambientes corporativos com proxy

### 🔄 [MIGRATION_GUIDE.md](./MIGRATION_GUIDE.md) ⭐ NOVO
- Guia de migração para arquitetura simplificada
- Conversão de modelos legados para formato LiteLLM
- Checklist de migração
- FAQ sobre a mudança

### 🔌 [ENDPOINTS_COMPATIBILITY.md](./ENDPOINTS_COMPATIBILITY.md) ⭐ NOVO
- Confirmação de compatibilidade com endpoints existentes
- O que continua funcionando (tudo!)
- Como testar seus endpoints
- FAQ sobre impacto da mudança

### 🔧 [TROUBLESHOOTING.md](./TROUBLESHOOTING.md)
- Problemas comuns e soluções
- Debugging
- FAQ

---

## Referências

### Documentação Oficial

- **LiteLLM Docs**: https://docs.litellm.ai/docs/
- **LiteLLM GitHub**: https://github.com/BerriAI/litellm
- **Google ADK Docs**: https://google.github.io/adk-docs/

### Documentação Relacionada no Projeto

- [ADDING_NEW_PROVIDER.md](../../ADDING_NEW_PROVIDER.md) - Como adicionar novos providers
- [MULTI_PROVIDER_SETUP.md](../../MULTI_PROVIDER_SETUP.md) - Configuração multi-provider
- [OLLAMA_SETUP.md](../../OLLAMA_SETUP.md) - Configuração do Ollama

### Links Úteis

- Lista de todos os providers suportados: https://docs.litellm.ai/docs/providers
- Cost tracking: https://docs.litellm.ai/docs/completion/cost_tracking
- Proxy Server: https://docs.litellm.ai/docs/proxy/quick_start

---

## Próximos Passos

1. ✅ Leia o [SETUP.md](./SETUP.md) para configurar o LiteLLM
2. ✅ Configure seus providers no `.env`
3. ✅ Teste com exemplos do [USAGE.md](./USAGE.md)
4. ✅ Explore configurações avançadas em [CONFIGURATION.md](./CONFIGURATION.md)

---

**Última atualização**: 2025-11-12
**Versão**: 1.0.0

