# Agente Padrão de Chat

## Visão Geral

Foi implementado um agente padrão de chat que está disponível para todos os usuários logados na aplicação. Quando o frontend não passa `agent_id` na requisição de chat, o backend automaticamente usa este agente padrão.

## Implementação

### 1. Usuário Sistema e Agente Padrão

- **Usuário Sistema**: Criado um usuário especial (`system@orkestrai.local`) que possui o agente padrão
- **Agente Padrão**: Criado um agente chamado "Chat Geral" com as seguintes características:
  - Nome: "Chat Geral"
  - Descrição: "Agente de chat geral disponível para todos os usuários"
  - Modelo padrão: `gpt-4o-mini`
  - Instrução: Assistente de IA útil e prestativo

### 2. Script de Criação

Foi criado o script `scripts/create_default_agent.py` que:
- Cria o usuário sistema (se não existir)
- Cria o agente padrão "Chat Geral" (se não existir)
- Retorna o ID do agente padrão

**Como executar:**
```bash
cd orkestrai-api
python scripts/create_default_agent.py
```

### 3. Modificações no Backend

#### Repository (`agent_repository_impl.py`)
- Adicionado método `get_default_agent()` que busca o agente padrão do usuário sistema

#### Use Case (`get_agent.py`)
- Adicionado método `get_default_agent()` que retorna o agente padrão

#### Rota de Chat (`agent_chat_routes.py`)
- Modificada a lógica para usar o agente padrão quando `agent_id` não for fornecido
- Se o agente padrão não existir, faz fallback para o primeiro agente do usuário

### 4. Modificações no Frontend

#### Componente de Chat (`components/dashboard/ai-chat/index.tsx`)
- Removida a necessidade de carregar agentes do usuário
- Removida a variável `agentId` do estado
- A requisição agora não passa `agent_id`, deixando o backend usar o agente padrão automaticamente

## Fluxo de Funcionamento

1. **Usuário faz login** → Frontend sincroniza token
2. **Usuário envia mensagem** → Frontend faz `POST /api/agents/chat` sem `agent_id`
3. **Backend recebe requisição** → Verifica se `agent_id` foi fornecido
4. **Se não fornecido** → Backend busca o agente padrão "Chat Geral"
5. **Backend processa mensagem** → Usa o agente padrão para gerar resposta
6. **Backend retorna resposta** → Inclui `session_id` para continuidade da conversa

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

# Chat especificando agent_id (usa agente específico)
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

O frontend agora funciona automaticamente sem precisar especificar `agent_id`. O componente de chat simplesmente envia a mensagem e o backend escolhe o agente apropriado.

## Próximos Passos

1. **Executar o script de criação**: Execute `python scripts/create_default_agent.py` para criar o agente padrão
2. **Testar**: Faça uma requisição de chat sem `agent_id` para verificar se está funcionando
3. **Personalizar**: Se necessário, ajuste as instruções do agente padrão editando diretamente no banco de dados

## Notas Importantes

- O agente padrão é criado uma única vez e fica disponível para todos os usuários
- Cada usuário pode ainda criar seus próprios agentes e usá-los especificando `agent_id`
- O agente padrão usa o modelo `gpt-4o-mini` por padrão, mas pode ser sobrescrito passando `model` na requisição
- As sessões de conversa funcionam normalmente com o agente padrão, mantendo contexto entre mensagens

