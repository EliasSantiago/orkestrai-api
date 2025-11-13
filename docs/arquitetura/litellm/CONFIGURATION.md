# LiteLLM - Configuração Avançada

Este guia cobre configurações avançadas do LiteLLM, incluindo load balancing, fallbacks, observabilidade e customizações.

---

## 📋 Sumário

1. [Configuração de Modelos](#configuração-de-modelos)
2. [Load Balancing](#load-balancing)
3. [Fallback e Retries](#fallback-e-retries)
4. [Caching](#caching)
5. [Observabilidade e Logging](#observabilidade-e-logging)
6. [Rate Limiting](#rate-limiting)
7. [Custom Providers](#custom-providers)

---

## Configuração de Modelos

### Estrutura Básica no litellm_config.yaml

```yaml
model_list:
  - model_name: nome-do-modelo          # Nome que você usará no código
    litellm_params:
      model: provider/modelo-real       # Modelo real no provider
      api_key: os.environ/API_KEY_VAR   # API key (via env var)
      api_base: http://custom-url       # URL customizada (opcional)
      temperature: 0.7                  # Parâmetros padrão (opcional)
      max_tokens: 2048
```

### Exemplo: Múltiplas Configurações do Mesmo Modelo

Útil para load balancing entre diferentes instâncias/regiões:

```yaml
model_list:
  # GPT-4o - Instância 1 (primary)
  - model_name: gpt-4o
    litellm_params:
      model: openai/gpt-4o
      api_key: os.environ/OPENAI_API_KEY_1
      rpm: 500  # Requests per minute limit
  
  # GPT-4o - Instância 2 (backup)
  - model_name: gpt-4o
    litellm_params:
      model: openai/gpt-4o
      api_key: os.environ/OPENAI_API_KEY_2
      rpm: 300
  
  # Azure OpenAI - Instância 3 (fallback)
  - model_name: gpt-4o
    litellm_params:
      model: azure/gpt-4o
      api_key: os.environ/AZURE_OPENAI_KEY
      api_base: os.environ/AZURE_OPENAI_ENDPOINT
      api_version: "2024-02-15-preview"
```

### Parâmetros Específicos por Provider

#### Google Gemini

```yaml
- model_name: gemini-2.0-flash
  litellm_params:
    model: gemini/gemini-2.0-flash
    api_key: os.environ/GOOGLE_API_KEY
    safety_settings:
      - category: HARM_CATEGORY_HARASSMENT
        threshold: BLOCK_ONLY_HIGH
```

#### OpenAI / Azure OpenAI

```yaml
- model_name: gpt-4o
  litellm_params:
    model: azure/gpt-4o
    api_key: os.environ/AZURE_OPENAI_KEY
    api_base: os.environ/AZURE_OPENAI_ENDPOINT
    api_version: "2024-02-15-preview"
    deployment_id: gpt-4o-deployment
```

#### Anthropic Claude

```yaml
- model_name: claude-3-opus
  litellm_params:
    model: anthropic/claude-3-opus-20240229
    api_key: os.environ/ANTHROPIC_API_KEY
    max_tokens: 4096
```

#### Ollama

```yaml
- model_name: llama2-local
  litellm_params:
    model: ollama/llama2
    api_base: http://localhost:11434
    # Não precisa de API key para Ollama local
```

---

## Load Balancing

### Configurando Load Balancing

```yaml
model_list:
  # Definir múltiplas instâncias do mesmo modelo
  - model_name: gpt-4o
    litellm_params:
      model: openai/gpt-4o
      api_key: os.environ/OPENAI_KEY_1
  
  - model_name: gpt-4o
    litellm_params:
      model: openai/gpt-4o
      api_key: os.environ/OPENAI_KEY_2
  
  - model_name: gpt-4o
    litellm_params:
      model: openai/gpt-4o
      api_key: os.environ/OPENAI_KEY_3

# Estratégia de roteamento
router_settings:
  routing_strategy: "least-busy"  # Opções: simple-shuffle, least-busy, latency-based
  num_retries: 3
  timeout: 30
  fallback_models: ["gpt-4o-mini"]  # Fallback se todas as instâncias falharem
```

### Estratégias de Roteamento

| Estratégia | Descrição | Quando Usar |
|------------|-----------|-------------|
| `simple-shuffle` | Alterna aleatoriamente | Balanceamento básico |
| `least-busy` | Escolhe a instância menos ocupada | Alta carga |
| `latency-based` | Escolhe a instância mais rápida | Performance crítica |
| `usage-based` | Baseado em uso de quota | Otimizar custos |

---

## Fallback e Retries

### Configurar Fallbacks

```yaml
model_list:
  # Modelo principal
  - model_name: my-model
    litellm_params:
      model: openai/gpt-4o
      api_key: os.environ/OPENAI_API_KEY

router_settings:
  # Fallback cascade
  model_group_alias:
    my-model:
      - gpt-4o           # Tenta primeiro
      - gpt-4-turbo      # Se falhar, tenta este
      - gpt-3.5-turbo    # Último recurso
  
  # Configurações de retry
  num_retries: 3
  retry_after: 5  # segundos entre retries
  timeout: 60
  
  # Condições para fallback
  allowed_fails: 3  # Número de falhas antes de usar fallback
  cooldown_time: 60  # Tempo antes de tentar novamente após falha
```

### Configurar Retries no Código

```python
from src.config import Config

# No .env:
# LITELLM_NUM_RETRIES=3
# LITELLM_REQUEST_TIMEOUT=600

# Os retries são automáticos e configurados via Config
```

---

## Caching

### Habilitar Cache com Redis

```yaml
general_settings:
  # Habilitar cache
  cache: true
  
  # Configurar Redis
  cache_params:
    type: "redis"
    host: os.environ/REDIS_HOST  # localhost
    port: os.environ/REDIS_PORT  # 6379
    password: os.environ/REDIS_PASSWORD  # opcional
    
    # TTL do cache (segundos)
    ttl: 3600  # 1 hora
    
    # Namespace para as chaves
    namespace: "litellm_cache"
```

### Cache em Memória (Desenvolvimento)

```yaml
general_settings:
  cache: true
  cache_params:
    type: "local"  # Cache em memória
    ttl: 600  # 10 minutos
```

### Configurar Cache Seletivo

```python
# Desabilitar cache para requisições específicas
async for chunk in provider.chat(
    messages=messages,
    model="gemini/gemini-2.0-flash-exp",
    cache=False  # Desabilita cache para esta chamada
):
    print(chunk, end="")
```

---

## Observabilidade e Logging

### Integração com Langfuse

```yaml
general_settings:
  # Callbacks para observabilidade
  success_callback: ["langfuse"]
  failure_callback: ["langfuse"]
  
  # Configurar Langfuse
  langfuse_public_key: os.environ/LANGFUSE_PUBLIC_KEY
  langfuse_secret_key: os.environ/LANGFUSE_SECRET_KEY
  langfuse_host: https://cloud.langfuse.com
```

### Integração com MLflow

```yaml
general_settings:
  success_callback: ["mlflow"]
  
  mlflow_tracking_uri: os.environ/MLFLOW_TRACKING_URI
  mlflow_experiment_name: "litellm-production"
```

### Logging Customizado

```yaml
general_settings:
  set_verbose: true  # Habilitar logs detalhados
  
  # Configurar callbacks customizados
  success_callback: ["webhook"]
  webhook_url: https://seu-webhook.com/litellm-logs
```

### Exemplo de Callback Customizado

```python
# src/core/litellm_callbacks.py
from litellm.integrations.custom_logger import CustomLogger
import logging

logger = logging.getLogger(__name__)

class CustomLiteLLMLogger(CustomLogger):
    """Logger customizado para LiteLLM."""
    
    def log_pre_api_call(self, model, messages, kwargs):
        """Chamado antes da requisição."""
        logger.info(f"Chamando modelo: {model}")
        logger.debug(f"Mensagens: {messages}")
    
    def log_post_api_call(self, kwargs, response_obj, start_time, end_time):
        """Chamado após a requisição."""
        duration = end_time - start_time
        logger.info(f"Requisição concluída em {duration:.2f}s")
    
    def log_stream_event(self, kwargs, response_obj, start_time, end_time):
        """Chamado durante streaming."""
        pass
    
    def log_success_event(self, kwargs, response_obj, start_time, end_time):
        """Chamado em caso de sucesso."""
        logger.info("✅ Requisição bem-sucedida")
    
    def log_failure_event(self, kwargs, response_obj, start_time, end_time):
        """Chamado em caso de falha."""
        logger.error("❌ Requisição falhou")

# Registrar o logger
import litellm
litellm.callbacks = [CustomLiteLLMLogger()]
```

---

## Rate Limiting

### Configurar Rate Limits por Modelo

```yaml
model_list:
  - model_name: gpt-4o
    litellm_params:
      model: openai/gpt-4o
      api_key: os.environ/OPENAI_API_KEY
      
      # Rate limits
      rpm: 500   # Requests per minute
      tpm: 90000  # Tokens per minute
      
  - model_name: gemini-2.0-flash
    litellm_params:
      model: gemini/gemini-2.0-flash
      api_key: os.environ/GOOGLE_API_KEY
      rpm: 1000
      tpm: 4000000
```

### Rate Limiting Global

```yaml
general_settings:
  # Rate limit global (para todos os modelos)
  max_parallel_requests: 100
  
  # Queue para requisições acima do limite
  enable_request_queue: true
  queue_max_size: 1000
```

---

## Custom Providers

### Adicionar Provider Customizado

```yaml
model_list:
  - model_name: my-custom-model
    litellm_params:
      model: openai/text-davinci-003  # Usar formato OpenAI-compatible
      api_base: https://meu-servidor.com/v1
      api_key: os.environ/CUSTOM_API_KEY
      
      # Headers customizados (opcional)
      headers:
        X-Custom-Header: "value"
```

### Configurar Provider Local

```yaml
model_list:
  # Modelo servido localmente com vLLM
  - model_name: local-llama
    litellm_params:
      model: openai/llama-2-7b  # Formato OpenAI-compatible
      api_base: http://localhost:8000/v1
      # Sem api_key se não for necessário
```

---

## Configurações de Produção

### Exemplo Completo para Produção

```yaml
model_list:
  # Google Gemini - Primary
  - model_name: gemini-2.0-flash
    litellm_params:
      model: gemini/gemini-2.0-flash-exp
      api_key: os.environ/GOOGLE_API_KEY
      rpm: 1000
      tpm: 4000000
  
  # OpenAI - Secondary
  - model_name: gpt-4o
    litellm_params:
      model: openai/gpt-4o
      api_key: os.environ/OPENAI_API_KEY_1
      rpm: 500
      tpm: 90000
  
  - model_name: gpt-4o
    litellm_params:
      model: openai/gpt-4o
      api_key: os.environ/OPENAI_API_KEY_2
      rpm: 500
      tpm: 90000
  
  # Ollama - Fallback local
  - model_name: llama2-local
    litellm_params:
      model: ollama/llama2
      api_base: http://localhost:11434

general_settings:
  # Performance
  max_parallel_requests: 50
  request_timeout: 600
  
  # Reliability
  num_retries: 3
  retry_after: 5
  
  # Caching
  cache: true
  cache_params:
    type: "redis"
    host: localhost
    port: 6379
    ttl: 3600
  
  # Observability
  success_callback: ["langfuse"]
  set_verbose: false  # Desabilitar em produção

router_settings:
  routing_strategy: "least-busy"
  timeout: 30
  
  # Fallback cascade
  model_group_alias:
    primary:
      - gemini-2.0-flash
      - gpt-4o
      - llama2-local
```

---

## Variáveis de Ambiente

### .env para Produção

```bash
# ============================================
# LiteLLM Production Configuration
# ============================================

# Enable LiteLLM
LITELLM_ENABLED=true
LITELLM_VERBOSE=false
LITELLM_NUM_RETRIES=3
LITELLM_REQUEST_TIMEOUT=600

# API Keys
GOOGLE_API_KEY=AIza...
OPENAI_API_KEY_1=sk-proj-...
OPENAI_API_KEY_2=sk-proj-...
ANTHROPIC_API_KEY=sk-ant-...

# Ollama
OLLAMA_API_BASE_URL=http://localhost:11434

# Redis (para cache e rate limiting)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

# Observability (Langfuse)
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
```

---

## 🎯 Checklist de Configuração Avançada

- [ ] Load balancing configurado para modelos críticos
- [ ] Fallbacks definidos para alta disponibilidade
- [ ] Rate limits configurados para evitar throttling
- [ ] Cache habilitado para reduzir custos
- [ ] Observabilidade configurada (Langfuse/MLflow)
- [ ] Retries automáticos habilitados
- [ ] Timeout apropriado para o caso de uso
- [ ] Logging configurado para produção

---

## 📚 Referências

- [LiteLLM Proxy Docs](https://docs.litellm.ai/docs/proxy/quick_start)
- [Router Settings](https://docs.litellm.ai/docs/routing)
- [Caching](https://docs.litellm.ai/docs/caching)
- [Callbacks](https://docs.litellm.ai/docs/observability/callbacks)

---

**Última atualização**: 2025-11-12

