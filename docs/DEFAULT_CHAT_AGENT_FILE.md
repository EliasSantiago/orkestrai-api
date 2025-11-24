# Agente Padrão de Chat (Arquivo)

## Visão Geral

Foi implementado um agente padrão de chat que está disponível em arquivo (`agents/default_chat_agent/agent.py`). Quando o frontend não passa `agent_id` na requisição de chat, o backend automaticamente usa este agente padrão.

## Estrutura do Agente Padrão

O agente padrão está localizado em:
```
agents/
  default_chat_agent/
    __init__.py
    agent.py
```

### Características do Agente Padrão

- **Nome**: Chat Geral
- **Descrição**: Agente de chat geral disponível para todos os usuários
- **Modelo padrão**: `gpt-4o-mini`
- **Ferramentas**: Nenhuma (pode ser expandido no futuro)
- **Instrução**: Assistente de IA útil e prestativo, capaz de ajudar com programação, escrita, análise, pesquisa e muito mais

## Implementação

### 1. Arquivo do Agente (`agents/default_chat_agent/agent.py`)

O agente segue a estrutura ADK padrão:
- Define um `root_agent` usando `google.adk.agents.Agent`
- Configura modelo, nome, descrição e instruções
- Pode ser editado diretamente no arquivo para personalização

### 2. Serviço de Carregamento (`src/services/default_agent_loader.py`)

Criado serviço `load_default_agent()` que:
- Importa o agente do arquivo
- Converte para entidade `Agent` do domínio
- Retorna `None` se não conseguir carregar (permite fallback)

### 3. Modificações na Rota de Chat (`src/api/agent_chat_routes.py`)

A rota `/api/agents/chat` foi modificada para:
- Carregar o agente padrão quando `agent_id` não for fornecido
- Usar `execute_with_agent()` do use case quando usar agente padrão
- Retornar `agent_id: 0` na resposta para indicar agente padrão

### 4. Use Case de Chat (`src/application/use_cases/agents/chat_with_agent.py`)

Adicionado método `execute_with_agent()` que:
- Aceita um agente diretamente (não precisa buscar no banco)
- Permite usar agentes de arquivo sem necessidade de ID de banco
- Mantém toda a lógica de chat (histórico, tools, etc.)

## Fluxo de Funcionamento

1. **Usuário faz login** → Frontend sincroniza token
2. **Usuário envia mensagem** → Frontend faz `POST /api/agents/chat` sem `agent_id`
3. **Backend recebe requisição** → Verifica se `agent_id` foi fornecido
4. **Se não fornecido** → Backend carrega agente padrão de `agents/default_chat_agent/agent.py`
5. **Backend processa mensagem** → Usa o agente padrão para gerar resposta
6. **Backend retorna resposta** → Inclui `session_id` e `agent_id: 0` para continuidade

## Uso

### Via API

```bash
# Chat sem especificar agent_id (usa agente padrão)
curl -X POST http://localhost:8001/api/agents/chat \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Olá, como você pode me ajudar?",
    "model": "gpt-4o-mini"
  }'

# Chat especificando agent_id (usa agente específico do banco)
curl -X POST http://localhost:8001/api/agents/chat \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Olá, como você pode me ajudar?",
    "agent_id": 2,
    "model": "gpt-4o-mini"
  }'
```

### Via Frontend

O frontend já está configurado para funcionar automaticamente sem precisar especificar `agent_id`. O componente de chat simplesmente envia a mensagem e o backend escolhe o agente apropriado.

## Personalização

Para personalizar o agente padrão, edite o arquivo:
```
agents/default_chat_agent/agent.py
```

Você pode modificar:
- **Modelo**: Altere `model='gpt-4o-mini'` para outro modelo
- **Instrução**: Modifique o texto em `instruction=`
- **Ferramentas**: Adicione tools na lista `tools=[]`
- **Descrição**: Altere `description=`

Após modificar, reinicie o servidor backend para carregar as mudanças.

## Vantagens

1. **Não requer banco de dados**: O agente padrão está em arquivo, não precisa de migração
2. **Fácil de personalizar**: Basta editar o arquivo Python
3. **Sempre disponível**: Não depende de criação de usuário sistema ou agente no banco
4. **Fallback automático**: Se o arquivo não existir, faz fallback para primeiro agente do usuário

## Notas Importantes

- O agente padrão retorna `agent_id: 0` na resposta da API
- As sessões de conversa funcionam normalmente com o agente padrão
- O modelo pode ser sobrescrito passando `model` na requisição
- O agente padrão não usa ferramentas por padrão (pode ser expandido)

