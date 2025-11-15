# 💬 Guia: Como Usar Chat com Contexto no Swagger

## 📋 Pré-requisitos

1. **Autenticação**: Você precisa estar autenticado (token JWT)
2. **Agente criado**: Deve ter pelo menos um agente criado
3. **Session ID**: Crie um `session_id` único (ex: `sessao123`)

---

## 🚀 Fluxo Completo Passo a Passo

### **Passo 1: Autenticar (se ainda não fez)**

1. Vá para `POST /api/auth/login`
2. Preencha:
   ```json
   {
     "email": "seu@email.com",
     "password": "sua_senha"
   }
   ```
3. Clique em **"Execute"**
4. Copie o `access_token` da resposta
5. Clique no botão **"Authorize"** (🔒) no topo do Swagger
6. Cole o token (sem "Bearer") e clique em **"Authorize"**

---

### **Passo 2: Vincular Session ao Usuário**

1. Vá para `POST /api/adk/sessions/{session_id}/associate`
2. No campo `session_id` (path parameter), digite: `sessao123` (ou qualquer ID único)
3. Clique em **"Execute"**
4. Você deve receber:
   ```json
   {
     "status": "success",
     "message": "Session associated with user"
   }
   ```

**✅ Agora a sessão está vinculada ao seu usuário!**

---

### **Passo 3: Iniciar Conversa com Contexto**

1. Vá para `POST /api/agents/chat`
2. Preencha o body:
   ```json
   {
     "message": "Olá, meu nome é João",
     "session_id": "sessao123",
     "agent_id": null
   }
   ```
   - `message`: Sua mensagem
   - `session_id`: O mesmo que você usou no Passo 2
   - `agent_id`: `null` (usa o primeiro agente) ou o ID de um agente específico

3. Clique em **"Execute"**
4. Você receberá a resposta do agente:
   ```json
   {
     "response": "Olá João! Como posso ajudar?",
     "agent_id": 1,
     "agent_name": "Nome do Agente",
     "session_id": "sessao123"
   }
   ```

**✅ A mensagem foi salva no Redis com contexto!**

---

### **Passo 4: Continuar a Conversa (com Contexto)**

1. Use o mesmo endpoint: `POST /api/agents/chat`
2. Preencha o body:
   ```json
   {
     "message": "Qual é o meu nome?",
     "session_id": "sessao123",
     "agent_id": null
   }
   ```
   - **Importante**: Use o mesmo `session_id`!

3. Clique em **"Execute"**
4. O agente deve lembrar do contexto:
   ```json
   {
     "response": "Seu nome é João!",
     "agent_id": 1,
     "agent_name": "Nome do Agente",
     "session_id": "sessao123"
   }
   ```

**✅ O agente lembrou do contexto da conversa anterior!**

---

## 📖 Endpoints Disponíveis

### **1. Chat com Agente (Principal)**

**Endpoint:** `POST /api/agents/chat`

**Body:**
```json
{
  "message": "Sua mensagem aqui",
  "session_id": "sessao123",  // Opcional - para contexto
  "agent_id": null            // Opcional - null usa primeiro agente
}
```

**O que faz:**
- ✅ Envia mensagem para o agente
- ✅ Se `session_id` fornecido: recupera contexto do Redis
- ✅ Se `session_id` fornecido: salva mensagens no Redis
- ✅ Retorna resposta do agente

---

### **2. Chat com Agente Específico**

**Endpoint:** `POST /api/agents/{agent_id}/chat`

**Path Parameter:**
- `agent_id`: ID do agente (ex: `1`)

**Body:**
```json
{
  "message": "Sua mensagem aqui",
  "session_id": "sessao123"
}
```

**O que faz:**
- ✅ Mesmo que `/api/agents/chat`, mas especifica o agente na URL

---

### **3. Ver Histórico da Conversa**

**Endpoint:** `GET /api/conversations/sessions/{session_id}`

**Path Parameter:**
- `session_id`: ID da sessão (ex: `sessao123`)

**Query Parameter (opcional):**
- `limit`: Número máximo de mensagens (ex: `10`)

**Resposta:**
```json
{
  "session_id": "sessao123",
  "messages": [
    {
      "role": "user",
      "content": "Olá, meu nome é João",
      "timestamp": "2025-01-15T10:00:00",
      "metadata": {}
    },
    {
      "role": "assistant",
      "content": "Olá João! Como posso ajudar?",
      "timestamp": "2025-01-15T10:00:01",
      "metadata": {}
    }
  ]
}
```

---

### **4. Ver Histórico (Alternativa ADK)**

**Endpoint:** `GET /api/adk/sessions/{session_id}/messages`

**Path Parameter:**
- `session_id`: ID da sessão

**Query Parameter (opcional):**
- `limit`: Número máximo de mensagens

**O que faz:**
- ✅ Mesmo que `/api/conversations/sessions/{session_id}`
- ✅ Conveniência para integração ADK

---

## 🎯 Exemplo Completo de Conversa

### **Mensagem 1: Apresentação**
```json
POST /api/agents/chat
{
  "message": "Olá, meu nome é Maria e tenho 25 anos",
  "session_id": "sessao123"
}
```

**Resposta:**
```json
{
  "response": "Olá Maria! Prazer em conhecê-la. Como posso ajudar?",
  "agent_id": 1,
  "agent_name": "Assistente",
  "session_id": "sessao123"
}
```

---

### **Mensagem 2: Pergunta com Contexto**
```json
POST /api/agents/chat
{
  "message": "Quantos anos eu tenho?",
  "session_id": "sessao123"
}
```

**Resposta:**
```json
{
  "response": "Você tem 25 anos, Maria!",
  "agent_id": 1,
  "agent_name": "Assistente",
  "session_id": "sessao123"
}
```

**✅ O agente lembrou do contexto!**

---

### **Mensagem 3: Verificar Histórico**
```json
GET /api/conversations/sessions/sessao123
```

**Resposta:**
```json
{
  "session_id": "sessao123",
  "messages": [
    {
      "role": "user",
      "content": "Olá, meu nome é Maria e tenho 25 anos",
      "timestamp": "2025-01-15T10:00:00"
    },
    {
      "role": "assistant",
      "content": "Olá Maria! Prazer em conhecê-la...",
      "timestamp": "2025-01-15T10:00:01"
    },
    {
      "role": "user",
      "content": "Quantos anos eu tenho?",
      "timestamp": "2025-01-15T10:00:05"
    },
    {
      "role": "assistant",
      "content": "Você tem 25 anos, Maria!",
      "timestamp": "2025-01-15T10:00:06"
    }
  ]
}
```

---

## 🔑 Pontos Importantes

### **1. Session ID**
- ✅ Use o mesmo `session_id` para manter o contexto
- ✅ Cada `session_id` é uma conversa separada
- ✅ O `session_id` pode ser qualquer string única

### **2. Contexto Automático**
- ✅ Quando você passa `session_id`, o contexto é injetado automaticamente
- ✅ Não precisa chamar endpoints separados para recuperar contexto
- ✅ O sistema busca o histórico do Redis automaticamente

### **3. Autenticação**
- ✅ Todos os endpoints requerem autenticação (exceto login/register)
- ✅ Use o botão **"Authorize"** no Swagger para adicionar o token
- ✅ O token expira após 30 dias (configurável)

### **4. Agente**
- ✅ Se não especificar `agent_id`, usa o primeiro agente do usuário
- ✅ Para usar um agente específico, passe o `agent_id` no body ou na URL

---

## 🐛 Troubleshooting

### **Erro: "Could not validate credentials"**
- ✅ Verifique se está autenticado (botão Authorize)
- ✅ Verifique se o token não expirou
- ✅ Faça login novamente se necessário

### **Erro: "No agents found for user"**
- ✅ Crie um agente primeiro: `POST /api/agents`
- ✅ Verifique se o agente está ativo (`is_active = true`)

### **Agente não lembra contexto**
- ✅ Verifique se está passando o mesmo `session_id`
- ✅ Verifique se Redis está rodando: `docker-compose ps`
- ✅ Verifique se a sessão foi associada: `POST /api/adk/sessions/{session_id}/associate`

### **Session ID não funciona**
- ✅ Certifique-se de associar a sessão primeiro: `POST /api/adk/sessions/{session_id}/associate`
- ✅ Use o mesmo `session_id` em todas as requisições

---

## 📝 Resumo do Fluxo

```
1. Login → Obter token
2. Authorize → Adicionar token no Swagger
3. Associate Session → POST /api/adk/sessions/{session_id}/associate
4. Chat → POST /api/agents/chat (com session_id)
5. Continuar Chat → POST /api/agents/chat (mesmo session_id)
6. Ver Histórico → GET /api/conversations/sessions/{session_id}
```

**Pronto! Agora você pode conversar com contexto usando o Swagger! 🎉**

