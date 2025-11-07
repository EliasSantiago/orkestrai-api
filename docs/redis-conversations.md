# 🔴 Contexto Conversacional com Redis

## ✅ Visão Geral

O sistema implementa contexto conversacional usando Redis para armazenar e recuperar histórico de conversas automaticamente.

---

## 🏗️ Arquitetura

### Componentes

1. **Redis Client** (`src/redis_client.py`) - Cliente Redis para operações
2. **Conversation Service** (`src/conversation_service.py`) - Serviço de alto nível
3. **ADK Middleware** (`src/adk_conversation_middleware.py`) - Integração com ADK
4. **Context Hooks** (`src/services/adk_context_hooks.py`) - Hooks para injeção automática

### Estrutura de Dados no Redis

```
conversation:user:{user_id}:session:{session_id}  # Lista de mensagens
sessions:user:{user_id}                            # Set de session_ids
session:user_id:{session_id}                      # Mapeamento sessão → usuário
```

### Formato das Mensagens

```json
{
  "role": "user|assistant",
  "content": "Texto da mensagem",
  "timestamp": "2025-01-20T10:00:00",
  "metadata": {}
}
```

---

## 🚀 Como Funciona

### 1. Injeção Automática de Contexto

Quando um agente é criado:
- Sistema recupera histórico do Redis
- Injeta contexto na instruction do agente
- Agente usa contexto automaticamente

### 2. Salvamento Automático

Quando você usa `POST /api/agents/chat`:
- Mensagem do usuário é salva automaticamente
- Resposta do agente é salva automaticamente
- Contexto é atualizado em tempo real

### 3. Recuperação de Contexto

- Sistema recupera últimas N mensagens (padrão: 100)
- Formata para o LLM
- Injeta na instruction do agente

---

## 📋 Endpoints de Conversas

### `GET /api/conversations/sessions`
Listar todas as sessões do usuário.

### `GET /api/conversations/sessions/{session_id}`
Obter histórico completo de uma sessão.

### `GET /api/conversations/sessions/{session_id}/info`
Informações da sessão (contagem, TTL, última atividade).

### `POST /api/conversations/sessions/{session_id}/messages`
Adicionar mensagem manualmente.

### `DELETE /api/conversations/sessions/{session_id}`
Deletar uma sessão específica.

### `DELETE /api/conversations/sessions`
Deletar todas as sessões do usuário.

---

## 🔗 Integração ADK

### Associar Sessão

```bash
POST /api/adk/sessions/{session_id}/associate
Authorization: Bearer {token}
```

### Obter Mensagens

```bash
GET /api/adk/sessions/{session_id}/messages
Authorization: Bearer {token}
```

### Salvar Mensagens

```bash
POST /api/adk/sessions/{session_id}/messages
Authorization: Bearer {token}
role=user&content=Mensagem
```

---

## ⚙️ Configuração

### Variáveis de Ambiente

```env
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
CONVERSATION_TTL=86400          # 24 horas em segundos
MAX_CONVERSATION_HISTORY=100    # Máximo de mensagens por sessão
```

### Ajustar TTL

```env
CONVERSATION_TTL=172800  # 48 horas
```

### Limitar Histórico

```env
MAX_CONVERSATION_HISTORY=50  # Apenas últimas 50 mensagens
```

---

## 💡 Exemplo de Uso

### 1. Criar Sessão

```javascript
const sessionId = `session_${Date.now()}`;

// Associar com usuário
await fetch(`/api/adk/sessions/${sessionId}/associate`, {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${token}` }
});
```

### 2. Chat com Contexto

```javascript
// Primeira mensagem
const response1 = await fetch('/api/agents/chat', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    message: 'Olá, meu nome é João',
    session_id: sessionId,
    agent_id: 1
  })
});

// Segunda mensagem (agente lembra do contexto!)
const response2 = await fetch('/api/agents/chat', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    message: 'Qual é o meu nome?',
    session_id: sessionId,  // Mesma sessão!
    agent_id: 1
  })
});
// Resposta: "Seu nome é João!"
```

### 3. Recuperar Histórico

```javascript
const history = await fetch(
  `/api/conversations/sessions/${sessionId}`,
  {
    headers: { 'Authorization': `Bearer ${token}` }
  }
);

const data = await history.json();
console.log('Histórico:', data.messages);
```

---

## 🔍 Verificação

### Verificar Redis

```bash
redis-cli -h localhost -p 6379 ping
# Deve retornar: PONG
```

### Ver Sessões no Redis

```bash
redis-cli
> SMEMBERS sessions:user:1
> LRANGE conversation:user:1:session:abc123 0 -1
```

---

## 🐛 Troubleshooting

### Contexto não está sendo usado

1. Verifique se Redis está rodando: `docker-compose ps`
2. Verifique se sessão está associada: `GET /api/adk/sessions/{session_id}/associate`
3. Verifique logs do servidor

### Mensagens não são salvas

1. Verifique se `session_id` está sendo passado
2. Verifique se Redis está conectado
3. Verifique se `user_id` está disponível

### Histórico não aparece

1. Verifique se mensagens foram salvas
2. Verifique se `session_id` está correto
3. Verifique se `user_id` corresponde ao token

---

## 📚 Mais Informações

- Consulte [Referência da API](api-reference.md) para detalhes dos endpoints
- Consulte [Frontend Guide](frontend-guide.md) para integração em frontend

