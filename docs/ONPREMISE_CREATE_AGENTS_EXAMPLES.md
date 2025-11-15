# Exemplos: Criar Agentes com Provedor On-Premise

Guia completo com exemplos práticos para listar modelos disponíveis e criar agentes usando o provedor on-premise.

## 📋 Pré-requisitos

1. ✅ Variáveis de ambiente configuradas no `.env`
2. ✅ Servidor da aplicação rodando (`http://localhost:8001`)
3. ✅ Token de autenticação válido
4. ✅ API on-premise acessível

## 🔍 Passo 1: Listar Modelos Disponíveis

### Via cURL (Bash)

```bash
# Obter lista de modelos da API on-premise
curl -X GET "https://apidesenv.go.gov.br/ia/modelos-linguagem-natural/v2.0/models" \
  -H "Authorization: Bearer SEU_TOKEN_OAUTH" \
  --insecure

# Ou se você já configurou o OAuth, use o script Python abaixo
```

### Via Python (Recomendado)

```python
#!/usr/bin/env python3
"""Lista modelos disponíveis na API on-premise."""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from src.core.oauth_token_manager import OAuthTokenManager
import httpx
from src.config import Config

async def list_models():
    """List available models from on-premise API."""
    # Load environment
    load_dotenv()
    
    # Get OAuth token
    oauth_manager = OAuthTokenManager()
    token = await oauth_manager.get_token()
    
    # Build models endpoint URL
    models_url = f"{Config.ONPREMISE_API_BASE_URL}/models"
    
    # Make request
    async with httpx.AsyncClient(verify=Config.VERIFY_SSL, timeout=30.0) as client:
        response = await client.get(
            models_url,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if response.status_code == 200:
            models = response.json()
            print("📦 Modelos disponíveis na API on-premise:\n")
            
            if isinstance(models, dict) and "models" in models:
                # Format: {"models": [{"name": "...", "size": ...}]}
                for model in models["models"]:
                    name = model.get("name", "unknown")
                    size = model.get("size", "unknown")
                    print(f"  • {name} (size: {size})")
            elif isinstance(models, list):
                # Format: [{"name": "...", "size": ...}]
                for model in models:
                    name = model.get("name", "unknown")
                    size = model.get("size", "unknown")
                    print(f"  • {name} (size: {size})")
            else:
                print(f"  Response: {models}")
        else:
            print(f"❌ Erro: HTTP {response.status_code}")
            print(f"   {response.text}")

if __name__ == "__main__":
    asyncio.run(list_models())
```

Salve como `scripts/list_onpremise_models.py` e execute:

```bash
source .venv/bin/activate
python scripts/list_onpremise_models.py
```

## 🎯 Passo 2: Obter Token de Autenticação da Aplicação

Antes de criar agentes, você precisa de um token de autenticação da sua aplicação:

```bash
# Login para obter token
curl -X POST http://localhost:8001/api/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "seu_email@example.com",
    "password": "sua_senha"
  }'
```

Resposta:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Salve o `access_token` - você vai usar em todas as requisições!**

## 🤖 Passo 3: Criar Agentes com Modelos On-Premise

### Exemplo 1: Agente Básico com Modelo On-Premise

```bash
curl -X POST http://localhost:8001/api/agents \
  -H "Authorization: Bearer SEU_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Assistente GPT-OSS",
    "description": "Assistente usando modelo GPT-OSS hospedado on-premise",
    "model": "gpt-oss:20b",
    "instruction": "Você é um assistente útil que responde em português do Brasil. Seja claro, objetivo e sempre educado.",
    "tools": []
  }'
```

### Exemplo 2: Agente com Ferramentas

```bash
curl -X POST http://localhost:8001/api/agents \
  -H "Authorization: Bearer SEU_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Assistente Completo On-Premise",
    "description": "Assistente com calculadora e informações de tempo",
    "model": "llama-2:7b",
    "instruction": "Você é um assistente inteligente. Use a calculadora para operações matemáticas e consulte a hora quando necessário.",
    "tools": ["calculator", "time"]
  }'
```

### Exemplo 3: Agente para Análise de Código

```bash
curl -X POST http://localhost:8001/api/agents \
  -H "Authorization: Bearer SEU_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Revisor de Código",
    "description": "Especialista em revisar e melhorar código Python",
    "model": "onpremise-codellama:13b",
    "instruction": "Você é um especialista em Python. Analise código, identifique problemas, sugira melhorias e explique boas práticas de programação.",
    "tools": []
  }'
```

### Exemplo 4: Agente para Atendimento ao Cliente

```bash
curl -X POST http://localhost:8001/api/agents \
  -H "Authorization: Bearer SEU_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Atendente Virtual",
    "description": "Assistente para atendimento ao cliente",
    "model": "local-customer-service:latest",
    "instruction": "Você é um atendente virtual simpático e prestativo. Responda dúvidas dos clientes de forma clara e profissional. Sempre mantenha um tom cordial.",
    "tools": ["time"]
  }'
```

### Exemplo 5: Agente para Pesquisa Web

```bash
curl -X POST http://localhost:8001/api/agents \
  -H "Authorization: Bearer SEU_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Pesquisador Web On-Premise",
    "description": "Agente que busca informações na web usando Tavily",
    "model": "gpt-oss:20b",
    "instruction": "Você é um pesquisador especializado. Use a ferramenta de busca web para encontrar informações atualizadas e precisas. Sempre cite suas fontes.",
    "tools": ["web_search"]
  }'
```

## 🐍 Passo 4: Script Python para Criar Múltiplos Agentes

Crie o arquivo `scripts/create_onpremise_agents.py`:

```python
#!/usr/bin/env python3
"""
Script para criar agentes usando provedor on-premise.
"""

import requests
import json
from typing import List, Optional

# Configuração
API_BASE_URL = "http://localhost:8001"
ACCESS_TOKEN = "SEU_ACCESS_TOKEN_AQUI"  # Obtenha via /api/login

def create_agent(
    name: str,
    model: str,
    instruction: str,
    description: str = "",
    tools: Optional[List[str]] = None
) -> dict:
    """
    Cria um agente via API.
    
    Args:
        name: Nome do agente
        model: Modelo on-premise (ex: gpt-oss:20b)
        instruction: Instruções do agente
        description: Descrição opcional
        tools: Lista de ferramentas (opcional)
    
    Returns:
        Dados do agente criado
    """
    url = f"{API_BASE_URL}/api/agents"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "name": name,
        "description": description,
        "model": model,
        "instruction": instruction,
        "tools": tools or []
    }
    
    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code == 201:
        agent = response.json()
        print(f"✅ Agente criado: {agent['name']} (ID: {agent['id']})")
        return agent
    else:
        print(f"❌ Erro ao criar agente: {response.status_code}")
        print(f"   {response.text}")
        return None


def main():
    """Cria vários agentes de exemplo."""
    print("🤖 Criando agentes on-premise...\n")
    
    # Agente 1: Assistente Geral
    create_agent(
        name="Assistente On-Premise Geral",
        model="gpt-oss:20b",
        description="Assistente geral para diversas tarefas",
        instruction="Você é um assistente útil que responde em português. Seja claro e objetivo.",
        tools=["calculator", "time"]
    )
    
    # Agente 2: Especialista em Python
    create_agent(
        name="Especialista Python On-Premise",
        model="llama-2:7b",
        description="Especialista em programação Python",
        instruction="Você é um expert em Python. Ajude com código, debugging e boas práticas.",
        tools=[]
    )
    
    # Agente 3: Analista de Dados
    create_agent(
        name="Analista de Dados On-Premise",
        model="onpremise-analyst:latest",
        description="Especialista em análise de dados",
        instruction="Você é um analista de dados. Ajude com análises estatísticas e interpretação de dados.",
        tools=["calculator"]
    )
    
    # Agente 4: Tradutor
    create_agent(
        name="Tradutor On-Premise",
        model="local-translator:multilang",
        description="Tradutor multilíngue",
        instruction="Você é um tradutor profissional. Traduza textos com precisão mantendo o contexto.",
        tools=[]
    )
    
    # Agente 5: Pesquisador
    create_agent(
        name="Pesquisador Web On-Premise",
        model="gpt-oss:20b",
        description="Pesquisador com acesso à web",
        instruction="Você é um pesquisador. Use a busca web para encontrar informações atualizadas.",
        tools=["web_search", "time"]
    )
    
    print("\n✅ Todos os agentes foram criados!")


if __name__ == "__main__":
    main()
```

Execute:

```bash
# 1. Edite o script e adicione seu ACCESS_TOKEN
# 2. Execute:
source .venv/bin/activate
python scripts/create_onpremise_agents.py
```

## 📝 Passo 5: Listar Agentes Criados

```bash
# Listar todos os seus agentes
curl -X GET http://localhost:8001/api/agents \
  -H "Authorization: Bearer SEU_ACCESS_TOKEN"
```

Resposta:
```json
[
  {
    "id": 1,
    "name": "Assistente On-Premise Geral",
    "description": "Assistente geral para diversas tarefas",
    "model": "gpt-oss:20b",
    "instruction": "Você é um assistente útil...",
    "tools": ["calculator", "time"],
    "use_file_search": false,
    "user_id": 1,
    "created_at": "2025-11-10T...",
    "updated_at": "2025-11-10T..."
  },
  ...
]
```

## 💬 Passo 6: Conversar com os Agentes

```bash
# Conversar com um agente específico
curl -X POST http://localhost:8001/api/agents/1/chat \
  -H "Authorization: Bearer SEU_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Olá! Qual é a sua especialidade?",
    "session_id": "minha-sessao-123"
  }'
```

Com parâmetros personalizados:

```bash
curl -X POST http://localhost:8001/api/agents/1/chat \
  -H "Authorization: Bearer SEU_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Explique inteligência artificial de forma simples",
    "session_id": "minha-sessao-123",
    "temperature": 0.5,
    "num_predict": 1000,
    "top_p": 0.9
  }'
```

## 🎨 Modelos de Agentes por Caso de Uso

### 1️⃣ Suporte Técnico
```json
{
  "name": "Suporte Técnico On-Premise",
  "model": "gpt-oss:20b",
  "description": "Assistente para suporte técnico",
  "instruction": "Você é um especialista em suporte técnico. Diagnostique problemas, sugira soluções e seja paciente com usuários não técnicos.",
  "tools": ["time"]
}
```

### 2️⃣ Criação de Conteúdo
```json
{
  "name": "Criador de Conteúdo",
  "model": "llama-2:7b",
  "description": "Especialista em criação de conteúdo",
  "instruction": "Você é um criador de conteúdo criativo. Escreva textos envolventes, artigos e posts para redes sociais.",
  "tools": ["web_search"]
}
```

### 3️⃣ Análise Financeira
```json
{
  "name": "Analista Financeiro",
  "model": "onpremise-finance:latest",
  "description": "Especialista em finanças",
  "instruction": "Você é um analista financeiro. Ajude com cálculos, análises de investimentos e planejamento financeiro.",
  "tools": ["calculator"]
}
```

### 4️⃣ Professor Virtual
```json
{
  "name": "Professor Virtual",
  "model": "local-teacher:latest",
  "description": "Tutor educacional",
  "instruction": "Você é um professor paciente e didático. Explique conceitos complexos de forma simples, use exemplos práticos.",
  "tools": ["calculator", "web_search"]
}
```

### 5️⃣ Assistente Jurídico
```json
{
  "name": "Assistente Jurídico",
  "model": "gpt-oss:20b",
  "description": "Auxiliar em questões jurídicas",
  "instruction": "Você é um assistente jurídico. Forneça informações sobre leis e procedimentos legais. IMPORTANTE: Sempre mencione que não substitui um advogado.",
  "tools": ["web_search", "time"]
}
```

## 🔄 Atualizar Agente

```bash
# Atualizar instruções ou modelo de um agente
curl -X PUT http://localhost:8001/api/agents/1 \
  -H "Authorization: Bearer SEU_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "instruction": "Você é um assistente ainda mais útil agora!",
    "tools": ["calculator", "time", "web_search"]
  }'
```

## 🗑️ Deletar Agente

```bash
curl -X DELETE http://localhost:8001/api/agents/1 \
  -H "Authorization: Bearer SEU_ACCESS_TOKEN"
```

## 📊 Nomes de Modelos Válidos para On-Premise

Baseado na configuração do provedor, use um destes formatos:

### ✅ Formatos Aceitos Automaticamente:

1. **Com dois-pontos**: `modelo:versão`
   - `gpt-oss:20b`
   - `llama-2:7b`
   - `mixtral:8x7b`
   - `custom-model:latest`

2. **Com prefixo**: `local-*` ou `onpremise-*`
   - `local-gpt-custom`
   - `onpremise-llama`
   - `local-model-v2`

3. **Lista Configurada**: Se você definir `ONPREMISE_MODELS` no `.env`
   ```env
   ONPREMISE_MODELS=modelo1,modelo2,modelo3
   ```
   Apenas esses modelos serão aceitos.

### ❌ Formatos que Vão para Outros Provedores:

- `gpt-4o` → OpenAI
- `gpt-3.5-turbo` → OpenAI
- `gemini-2.0-flash-exp` → Gemini

## 🎯 Verificar Qual Provedor Será Usado

Script Python para verificar:

```python
from src.core.llm_factory import LLMFactory

# Testar diferentes modelos
models_to_test = [
    "gpt-oss:20b",
    "llama-2:7b",
    "local-model",
    "onpremise-custom",
    "gpt-4o",
    "gemini-2.0-flash-exp"
]

for model in models_to_test:
    provider = LLMFactory.get_provider(model)
    if provider:
        provider_name = provider.__class__.__name__
        print(f"✓ {model:30} → {provider_name}")
    else:
        print(f"✗ {model:30} → NÃO SUPORTADO")
```

## 🚀 Script Completo: Setup Rápido

Crie `scripts/quick_setup_onpremise.sh`:

```bash
#!/bin/bash

echo "🚀 Setup Rápido: Agentes On-Premise"
echo "===================================="

# 1. Obter token de autenticação
echo ""
echo "📝 Passo 1: Login"
read -p "Email: " email
read -sp "Senha: " password
echo ""

token_response=$(curl -s -X POST http://localhost:8001/api/login \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$email\",\"password\":\"$password\"}")

access_token=$(echo $token_response | jq -r '.access_token')

if [ "$access_token" == "null" ] || [ -z "$access_token" ]; then
    echo "❌ Erro no login"
    exit 1
fi

echo "✅ Login bem-sucedido!"

# 2. Criar agente
echo ""
echo "🤖 Passo 2: Criar agente"
read -p "Nome do modelo on-premise (ex: gpt-oss:20b): " model_name

agent_response=$(curl -s -X POST http://localhost:8001/api/agents \
  -H "Authorization: Bearer $access_token" \
  -H "Content-Type: application/json" \
  -d "{
    \"name\": \"Assistente $model_name\",
    \"description\": \"Agente usando modelo on-premise\",
    \"model\": \"$model_name\",
    \"instruction\": \"Você é um assistente útil que responde em português.\",
    \"tools\": [\"calculator\", \"time\"]
  }")

agent_id=$(echo $agent_response | jq -r '.id')

if [ "$agent_id" == "null" ] || [ -z "$agent_id" ]; then
    echo "❌ Erro ao criar agente"
    echo "$agent_response"
    exit 1
fi

echo "✅ Agente criado! ID: $agent_id"

# 3. Testar agente
echo ""
echo "💬 Passo 3: Testar agente"
curl -X POST "http://localhost:8001/api/agents/$agent_id/chat" \
  -H "Authorization: Bearer $access_token" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Olá! Você está funcionando?",
    "session_id": "test-session"
  }'

echo ""
echo "✅ Setup completo!"
```

Torne executável e rode:

```bash
chmod +x scripts/quick_setup_onpremise.sh
./scripts/quick_setup_onpremise.sh
```

## 📚 Recursos Adicionais

- **Documentação Completa**: `docs/ONPREMISE_PROVIDER_SETUP.md`
- **Quick Start**: `docs/ONPREMISE_QUICK_START.md`
- **Script de Teste**: `scripts/test_onpremise_provider.py`
- **API Docs**: `http://localhost:8001/docs` (Swagger UI)

## 🎓 Dicas Finais

1. **Sempre teste o modelo primeiro**: Use `scripts/test_onpremise_provider.py`
2. **Use nomes descritivos**: Facilita gerenciar múltiplos agentes
3. **Comece simples**: Crie um agente básico antes de adicionar ferramentas
4. **Monitore logs**: Observe os logs da aplicação para debug
5. **Ajuste parâmetros**: Temperature, num_predict, etc. conforme necessidade

---

**Pronto! Agora você pode criar quantos agentes quiser usando o provedor on-premise!** 🎉

