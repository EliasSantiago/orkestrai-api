# 🎨 Como Criar um Frontend Customizado - Guia Completo

## 📋 **Como o ADK Web Funciona Internamente**

O ADK Web (`adk web`) cria um servidor HTTP que:
1. Carrega agentes de arquivos Python (`agents/*/agent.py`)
2. Expõe endpoints HTTP para interagir com os agentes
3. Mantém sessões de conversa
4. Gerencia o estado da conversa

**Mas você não precisa usar o ADK Web!** Você pode criar seu próprio frontend usando a API REST.

---

## 🚀 **Endpoints Disponíveis na API**

### **1. Autenticação** (`/api/auth`)

```bash
# Registrar usuário
POST /api/auth/register
{
  "name": "Usuário",
  "email": "usuario@example.com",
  "password": "senha123",
  "password_confirm": "senha123"
}

# Login (obter token)
POST /api/auth/login
{
  "email": "usuario@example.com",
  "password": "senha123"
}
# Retorna: { "access_token": "...", "token_type": "bearer" }

# Obter usuário atual
GET /api/auth/me
Authorization: Bearer {token}
```

---

### **2. Gerenciar Agentes** (`/api/agents`)

```bash
# Listar agentes do usuário
GET /api/agents
Authorization: Bearer {token}

# Criar agente
POST /api/agents
Authorization: Bearer {token}
{
  "name": "Meu Agente",
  "description": "Descrição",
  "instruction": "Você é um assistente útil...",
  "model": "gemini-2.0-flash-exp",
  "tools": ["calculator"]
}

# Obter agente específico
GET /api/agents/{agent_id}
Authorization: Bearer {token}

# Atualizar agente
PUT /api/agents/{agent_id}
Authorization: Bearer {token}
{
  "name": "Novo Nome",
  "instruction": "Nova instrução..."
}

# Deletar agente
DELETE /api/agents/{agent_id}
Authorization: Bearer {token}
```

---

### **3. Chat com Agentes** (`/api/agents`) ✅ **NOVO**

```bash
# Chat com agente (usa primeiro agente se não especificar)
POST /api/agents/chat
Authorization: Bearer {token}
{
  "message": "Olá, como você está?",
  "session_id": "sessao123",  // Opcional - para contexto
  "agent_id": 1  // Opcional - especifica qual agente usar
}

# Chat com agente específico
POST /api/agents/{agent_id}/chat
Authorization: Bearer {token}
{
  "message": "Olá, como você está?",
  "session_id": "sessao123"  // Opcional - para contexto
}
```

**Resposta:**
```json
{
  "response": "Olá! Estou bem, obrigado por perguntar.",
  "agent_id": 1,
  "agent_name": "Meu Agente",
  "session_id": "sessao123"
}
```

---

### **4. Gerenciar Conversas** (`/api/conversations`)

```bash
# Listar sessões do usuário
GET /api/conversations/sessions
Authorization: Bearer {token}

# Obter histórico de uma sessão
GET /api/conversations/sessions/{session_id}
Authorization: Bearer {token}

# Obter informações da sessão
GET /api/conversations/sessions/{session_id}/info
Authorization: Bearer {token}

# Adicionar mensagem manualmente
POST /api/conversations/sessions/{session_id}/messages
Authorization: Bearer {token}
{
  "content": "Mensagem do usuário",
  "metadata": {}
}

# Deletar sessão
DELETE /api/conversations/sessions/{session_id}
Authorization: Bearer {token}

# Deletar todas as sessões
DELETE /api/conversations/sessions
Authorization: Bearer {token}
```

---

### **5. Integração ADK** (`/api/adk`)

```bash
# Associar sessão ADK com usuário
POST /api/adk/sessions/{session_id}/associate
Authorization: Bearer {token}

# Salvar mensagem do ADK
POST /api/adk/sessions/{session_id}/messages
Authorization: Bearer {token}
{
  "role": "user",  // ou "assistant"
  "content": "Mensagem"
}

# Webhook para salvar mensagem
POST /api/adk/webhook/message
{
  "session_id": "sessao123",
  "role": "user",
  "content": "Mensagem",
  "user_id": 1  // Opcional se sessão já associada
}
```

---

## 🎯 **Fluxo Completo para Frontend Customizado**

### **1. Autenticação**

```javascript
// Login
const loginResponse = await fetch('http://localhost:8001/api/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'usuario@example.com',
    password: 'senha123'
  })
});

const { access_token } = await loginResponse.json();

// Salvar token
localStorage.setItem('token', access_token);
```

### **2. Listar Agentes**

```javascript
const agentsResponse = await fetch('http://localhost:8001/api/agents', {
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('token')}`
  }
});

const agents = await agentsResponse.json();
console.log('Agentes disponíveis:', agents);
```

### **3. Criar Sessão de Conversa**

```javascript
// Gerar session_id único
const sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

// Associar sessão com usuário (opcional, mas recomendado)
await fetch(`http://localhost:8001/api/adk/sessions/${sessionId}/associate`, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('token')}`
  }
});
```

### **4. Enviar Mensagem para Agente**

```javascript
async function sendMessage(message, agentId = null, sessionId = null) {
  const response = await fetch('http://localhost:8001/api/agents/chat', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${localStorage.getItem('token')}`
    },
    body: JSON.stringify({
      message: message,
      session_id: sessionId,
      agent_id: agentId
    })
  });
  
  const data = await response.json();
  return data;
}

// Usar
const result = await sendMessage('Olá!', agentId=1, sessionId='sessao123');
console.log('Resposta:', result.response);
```

### **5. Recuperar Histórico**

```javascript
async function getHistory(sessionId) {
  const response = await fetch(
    `http://localhost:8001/api/conversations/sessions/${sessionId}`,
    {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    }
  );
  
  const data = await response.json();
  return data.messages;
}

// Usar
const history = await getHistory('sessao123');
console.log('Histórico:', history);
```

---

## 📱 **Exemplo Completo de Frontend React**

```jsx
import React, { useState, useEffect } from 'react';

function ChatInterface() {
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [agents, setAgents] = useState([]);
  const [selectedAgent, setSelectedAgent] = useState(null);
  const [sessionId] = useState(`session_${Date.now()}`);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');

  // Login
  const login = async (email, password) => {
    const res = await fetch('http://localhost:8001/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    const data = await res.json();
    setToken(data.access_token);
    localStorage.setItem('token', data.access_token);
    
    // Associar sessão
    await fetch(`http://localhost:8001/api/adk/sessions/${sessionId}/associate`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${data.access_token}` }
    });
  };

  // Carregar agentes
  useEffect(() => {
    if (token) {
      fetch('http://localhost:8001/api/agents', {
        headers: { 'Authorization': `Bearer ${token}` }
      })
        .then(r => r.json())
        .then(data => {
          setAgents(data);
          if (data.length > 0) setSelectedAgent(data[0].id);
        });
    }
  }, [token]);

  // Enviar mensagem
  const sendMessage = async () => {
    if (!input.trim() || !selectedAgent) return;

    const userMessage = input;
    setInput('');
    
    // Adicionar mensagem do usuário à UI
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);

    // Enviar para API
    const res = await fetch('http://localhost:8001/api/agents/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        message: userMessage,
        agent_id: selectedAgent,
        session_id: sessionId
      })
    });

    const data = await res.json();
    
    // Adicionar resposta à UI
    setMessages(prev => [...prev, { role: 'assistant', content: data.response }]);
  };

  if (!token) {
    return <LoginForm onLogin={login} />;
  }

  return (
    <div className="chat-container">
      <div className="agents-list">
        <h3>Agentes</h3>
        {agents.map(agent => (
          <button
            key={agent.id}
            onClick={() => setSelectedAgent(agent.id)}
            className={selectedAgent === agent.id ? 'active' : ''}
          >
            {agent.name}
          </button>
        ))}
      </div>

      <div className="chat-messages">
        {messages.map((msg, idx) => (
          <div key={idx} className={`message ${msg.role}`}>
            {msg.content}
          </div>
        ))}
      </div>

      <div className="chat-input">
        <input
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyPress={e => e.key === 'Enter' && sendMessage()}
          placeholder="Digite sua mensagem..."
        />
        <button onClick={sendMessage}>Enviar</button>
      </div>
    </div>
  );
}

function LoginForm({ onLogin }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  return (
    <form onSubmit={e => { e.preventDefault(); onLogin(email, password); }}>
      <input
        type="email"
        value={email}
        onChange={e => setEmail(e.target.value)}
        placeholder="Email"
      />
      <input
        type="password"
        value={password}
        onChange={e => setPassword(e.target.value)}
        placeholder="Senha"
      />
      <button type="submit">Login</button>
    </form>
  );
}

export default ChatInterface;
```

---

## 🔧 **Como Funciona o Contexto**

Quando você passa `session_id` no chat:

1. **Sistema recupera contexto** do Redis (últimas mensagens)
2. **Injeta contexto** na instruction do agente
3. **Agente responde** com contexto completo
4. **Salva mensagens** automaticamente no Redis

**Exemplo:**
```javascript
// Primeira mensagem
await sendMessage('Olá, meu nome é João', agentId=1, sessionId='sessao123');

// Segunda mensagem (agente lembra do contexto!)
await sendMessage('Qual é o meu nome?', agentId=1, sessionId='sessao123');
// Resposta: "Seu nome é João!"
```

---

## 🛠️ **Tools Disponíveis**

Os agentes podem usar tools. As tools disponíveis são:

1. **`calculator`** - Calculadora matemática
   ```javascript
   // O agente usa automaticamente quando necessário
   await sendMessage('Quanto é 25 * 4 + 10?', agentId=1, sessionId='sessao123');
   ```

2. **`get_current_time`** - Informações de data/hora
   ```javascript
   await sendMessage('Que horas são?', agentId=1, sessionId='sessao123');
   ```

---

## 📊 **Arquitetura Completa**

```
┌─────────────────┐
│  Frontend       │
│  (React/Vue/etc)│
└────────┬────────┘
         │
         │ HTTP/REST
         │
         ▼
┌─────────────────┐
│  FastAPI        │
│  (Porta 8001)   │
│                 │
│  - /api/auth    │
│  - /api/agents  │
│  - /api/agents/ │
│    chat         │
│  - /api/conversations│
└────────┬────────┘
         │
         │
         ▼
┌─────────────────┐      ┌──────────────┐
│  PostgreSQL     │      │    Redis     │
│  (Agentes)      │      │  (Contexto)  │
└─────────────────┘      └──────────────┘
         │
         │
         ▼
┌─────────────────┐
│  Google ADK     │
│  (Agentes)      │
└─────────────────┘
```

---

## 🎯 **Resumo dos Endpoints Essenciais**

Para criar um frontend customizado, você precisa principalmente de:

1. **`POST /api/auth/login`** - Obter token
2. **`GET /api/agents`** - Listar agentes
3. **`POST /api/agents/chat`** - **Chat com agentes** ✅
4. **`GET /api/conversations/sessions/{session_id}`** - Histórico

**Esses 4 endpoints são suficientes para criar um chat completo!**

---

## 📚 **Documentação Interativa**

Acesse `http://localhost:8001/docs` para ver todos os endpoints com exemplos interativos (Swagger UI).

---

## ✅ **Pronto para Usar!**

Agora você tem tudo que precisa para criar um frontend customizado:
- ✅ Endpoints de autenticação
- ✅ Endpoints para gerenciar agentes
- ✅ **Endpoint de chat** para interagir com agentes
- ✅ Endpoints para gerenciar contexto/conversas
- ✅ Suporte automático a contexto via Redis

**Não precisa do ADK Web!** Você pode criar seu próprio frontend usando apenas a API REST.

