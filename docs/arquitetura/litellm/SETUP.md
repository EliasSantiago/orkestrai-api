# LiteLLM - Guia de Instalação e Configuração

> **🎯 IMPORTANTE**: LiteLLM é agora o ÚNICO proxy recomendado para todos os modelos LLM.  
> A arquitetura foi simplificada para usar apenas o LiteLLM como gateway unificado.

## 📋 Pré-requisitos

- Python 3.10+
- pip instalado
- Acesso às APIs que você deseja usar (Google, OpenAI, etc.)
- (Opcional) Ollama instalado para modelos locais

## 🏗️ Arquitetura

**Antes**: Múltiplos providers (ADKProvider, OpenAIProvider, etc.)  
**Agora**: LiteLLM como ÚNICO proxy unificado ✅

Isso significa:
- ✅ Mais simples de configurar
- ✅ Mais fácil de manter
- ✅ Mais recursos (retries, fallbacks, observabilidade)

---

## 🚀 Instalação

### Passo 1: Instalar Dependências

O LiteLLM já está incluído no `requirements.txt`. Para instalar:

```bash
# Navegar para o diretório do projeto
cd /home/vdilinux/aplicações/api-adk-google-main

# Instalar todas as dependências
pip install -r requirements.txt

# Ou instalar apenas o LiteLLM
pip install litellm>=1.50.0
```

### Passo 2: Verificar Instalação

```bash
# Verificar se o LiteLLM foi instalado corretamente
python -c "import litellm; print(f'LiteLLM version: {litellm.__version__}')"
```

Saída esperada:
```
LiteLLM version: 1.50.0 (ou superior)
```

---

## ⚙️ Configuração Básica

### Passo 1: Configurar Variáveis de Ambiente

Edite o arquivo `.env` na raiz do projeto:

```bash
# ============================================
# LiteLLM Configuration
# ============================================

# Habilitar o LiteLLM provider (OBRIGATÓRIO - agora é o único proxy)
LITELLM_ENABLED=true

# Debug mode (opcional - útil para troubleshooting)
LITELLM_VERBOSE=false

# Retry settings
LITELLM_NUM_RETRIES=3
LITELLM_REQUEST_TIMEOUT=600  # 10 minutos

# ============================================
# API Keys dos Providers
# ============================================

# Google Gemini
GOOGLE_API_KEY=AIzaSy...

# OpenAI
OPENAI_API_KEY=sk-proj-...

# Anthropic Claude (opcional)
ANTHROPIC_API_KEY=sk-ant-...

# Ollama (se estiver usando modelos locais)
OLLAMA_API_BASE_URL=http://localhost:11434

# Outros providers (opcional)
COHERE_API_KEY=
HUGGINGFACE_API_KEY=
REPLICATE_API_KEY=
```

### Passo 2: Obter API Keys

#### Google Gemini
1. Acesse: https://makersuite.google.com/app/apikey
2. Clique em "Create API Key"
3. Copie a chave e cole em `GOOGLE_API_KEY`

#### OpenAI
1. Acesse: https://platform.openai.com/api-keys
2. Clique em "Create new secret key"
3. Copie a chave e cole em `OPENAI_API_KEY`

#### Anthropic Claude
1. Acesse: https://console.anthropic.com/
2. Vá em "API Keys"
3. Crie uma nova chave
4. Copie e cole em `ANTHROPIC_API_KEY`

#### Ollama (Local)
1. Instale o Ollama: https://ollama.ai/
2. Inicie o servidor:
   ```bash
   ollama serve
   ```
3. A URL padrão é `http://localhost:11434`

---

## 📝 Configuração do litellm_config.yaml

O arquivo `litellm_config.yaml` já está criado na raiz do projeto com configurações padrão.

### Estrutura Básica

```yaml
model_list:
  # Google Gemini Models
  - model_name: gemini-2.0-flash-exp
    litellm_params:
      model: gemini/gemini-2.0-flash-exp
      api_key: os.environ/GOOGLE_API_KEY
  
  # OpenAI Models
  - model_name: gpt-4o
    litellm_params:
      model: openai/gpt-4o
      api_key: os.environ/OPENAI_API_KEY
  
  # Ollama Models (local)
  - model_name: ollama/llama2
    litellm_params:
      model: ollama/llama2
      api_base: os.environ/OLLAMA_API_BASE_URL

general_settings:
  set_verbose: false
  request_timeout: 600
  num_retries: 3
```

### Personalizando Modelos

Para adicionar um novo modelo, adicione uma entrada em `model_list`:

```yaml
model_list:
  # Seu novo modelo
  - model_name: meu-modelo-customizado
    litellm_params:
      model: provider/modelo-name
      api_key: os.environ/SUA_API_KEY
      # Parâmetros opcionais
      temperature: 0.7
      max_tokens: 2048
```

---

## 🧪 Testando a Configuração

### Teste 1: Verificar Providers Disponíveis

Crie um arquivo `test_litellm.py`:

```python
from src.core.llm_factory import LLMFactory

# Listar todos os providers disponíveis
providers = LLMFactory._get_providers()
print(f"Providers disponíveis: {len(providers)}")

for provider in providers:
    print(f"  - {provider.__class__.__name__}")
    models = provider.get_supported_models()
    print(f"    Modelos: {len(models)}")
    for model in models[:3]:  # Mostrar primeiros 3
        print(f"      • {model}")
```

Execute:
```bash
python test_litellm.py
```

Saída esperada:
```
✓ LiteLLM provider initialized (unified LLM gateway)
  → All models will be routed through LiteLLM
  → Supported: Gemini, OpenAI, Claude, Ollama, Azure, and 100+ more

Providers disponíveis: 1
  - LiteLLMProvider
    Modelos: 25+
      • gemini/gemini-2.0-flash-exp
      • openai/gpt-4o
      • anthropic/claude-3-opus-20240229
      • ollama/llama2
      • ... e mais 90+ providers
```

> **✅ Sucesso!** Se você vê apenas o LiteLLMProvider, está correto!  
> A arquitetura agora usa apenas o LiteLLM como proxy unificado.

### Teste 2: Fazer uma Requisição Simples

```python
import asyncio
from src.core.llm_factory import LLMFactory
from src.core.llm_provider import LLMMessage

async def test_chat():
    # Obter provider para modelo
    provider = LLMFactory.get_provider("gemini/gemini-2.0-flash-exp")
    
    if not provider:
        print("❌ Provider não encontrado!")
        return
    
    print(f"✅ Provider encontrado: {provider.__class__.__name__}")
    
    # Criar mensagem de teste
    messages = [
        LLMMessage(role="user", content="Olá! Você está funcionando?")
    ]
    
    # Fazer requisição
    print("\nResposta:")
    async for chunk in provider.chat(
        messages=messages,
        model="gemini/gemini-2.0-flash-exp"
    ):
        print(chunk, end="", flush=True)
    
    print("\n\n✅ Teste concluído com sucesso!")

# Executar teste
asyncio.run(test_chat())
```

Execute:
```bash
python test_chat.py
```

### Teste 3: Testar Múltiplos Providers

```python
import asyncio
from src.core.llm_factory import LLMFactory
from src.core.llm_provider import LLMMessage

async def test_multiple_providers():
    models_to_test = [
        "gemini/gemini-2.0-flash-exp",
        "openai/gpt-4o-mini",
        "ollama/llama2",  # Se você tiver Ollama rodando
    ]
    
    messages = [
        LLMMessage(role="user", content="Diga olá em uma palavra.")
    ]
    
    for model in models_to_test:
        print(f"\n{'='*60}")
        print(f"Testando: {model}")
        print('='*60)
        
        provider = LLMFactory.get_provider(model)
        
        if not provider:
            print(f"❌ Provider não encontrado para {model}")
            continue
        
        try:
            print(f"Provider: {provider.__class__.__name__}")
            print("Resposta: ", end="")
            
            async for chunk in provider.chat(messages=messages, model=model):
                print(chunk, end="", flush=True)
            
            print("\n✅ Sucesso!")
            
        except Exception as e:
            print(f"\n❌ Erro: {e}")

# Executar
asyncio.run(test_multiple_providers())
```

---

## 🔍 Verificação da Configuração

### Checklist de Configuração

- [ ] LiteLLM instalado (`pip list | grep litellm`)
- [ ] `LITELLM_ENABLED=true` no `.env`
- [ ] Pelo menos uma API key configurada (Google, OpenAI, etc.)
- [ ] Arquivo `litellm_config.yaml` presente na raiz
- [ ] Testes executados com sucesso
- [ ] Sem erros nos logs

### Comandos de Verificação

```bash
# 1. Verificar se LiteLLM está instalado
pip show litellm

# 2. Verificar variáveis de ambiente
python -c "from src.config import Config; print(f'LiteLLM Enabled: {Config.LITELLM_ENABLED}')"

# 3. Verificar arquivo de configuração
ls -la litellm_config.yaml

# 4. Verificar API keys (mascarado)
python -c "from src.config import Config; print(f'Google API: {\"OK\" if Config.GOOGLE_API_KEY else \"NOT SET\"}')"
python -c "from src.config import Config; print(f'OpenAI API: {\"OK\" if Config.OPENAI_API_KEY else \"NOT SET\"}')"
```

---

## 🎯 Próximos Passos

Agora que o LiteLLM está configurado:

1. ✅ Leia [USAGE.md](./USAGE.md) para aprender a usar no código
2. ✅ Explore [CONFIGURATION.md](./CONFIGURATION.md) para configurações avançadas
3. ✅ Consulte [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) se tiver problemas

---

## 📞 Precisa de Ajuda?

- Documentação oficial: https://docs.litellm.ai/docs/
- GitHub Issues: https://github.com/BerriAI/litellm/issues
- Discord da LiteLLM: https://discord.com/invite/wuPM9dRgDw

---

**Última atualização**: 2025-11-12

