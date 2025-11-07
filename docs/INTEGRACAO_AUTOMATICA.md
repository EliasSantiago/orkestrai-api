# 🚀 Integração Automática Redis-ADK - Guia de Implementação

## ✅ O Que Foi Implementado

### 1. **Serviço de Integração ADK-Redis** (`src/services/adk_redis_integration.py`)
- Serviço centralizado para gerenciar integração
- Métodos para recuperar e injetar contexto
- Formatação de contexto para LLM

### 2. **Hooks de Contexto** (`src/services/adk_context_hooks.py`)
- Função `inject_context_into_agent()` para injetar contexto automaticamente
- Obtenção de session_id e user_id de múltiplas fontes:
  - Variáveis de ambiente (`ADK_SESSION_ID`, `ADK_USER_ID`)
  - Contexto global por thread
  - Parâmetros diretos

### 3. **Modificação do adk_loader.py**
- Agentes gerados agora incluem código para injetar contexto automaticamente
- Funciona tanto para agentes principais quanto individuais
- Fallback gracioso se contexto não estiver disponível

### 4. **Endpoints Adicionais** (`src/api/adk_integration_routes.py`)
- `POST /api/adk/webhook/message` - Webhook para salvar mensagens automaticamente
- Melhor suporte para integração externa

---

## 🔧 Como Funciona

### **Fluxo Automático:**

1. **Quando um agente é criado:**
   ```
   Agent criado → inject_context_into_agent() chamado → 
   Contexto recuperado do Redis → 
   Contexto injetado na instruction do agente
   ```

2. **Quando uma mensagem é enviada:**
   - O contexto já está na instruction do agente
   - O agente usa o contexto automaticamente para responder

3. **Para salvar mensagens:**
   - Use o endpoint `/api/adk/webhook/message`
   - Ou `/api/adk/sessions/{session_id}/messages` (requer autenticação)

---

## 📋 Como Usar

### **1. Associar Sessão com Usuário**

Antes de usar o agente, associe a sessão com um usuário:

```bash
POST http://localhost:8001/api/adk/sessions/{session_id}/associate
Authorization: Bearer {token}
```

Isso permite que o sistema recupere o contexto corretamente.

### **2. Configurar Variáveis de Ambiente (Opcional)**

Para integração automática completa, configure:

```bash
export ADK_SESSION_ID="sua-session-id"
export ADK_USER_ID="seu-user-id"
```

### **3. Usar o Agente**

Os agentes agora injetam contexto automaticamente quando são criados!

- Se `session_id` e `user_id` estão disponíveis → contexto é injetado
- Se não estão disponíveis → agente funciona normalmente (sem contexto)

---

## 🔄 Integração com ADK Web

### **Opção 1: Manual (Recomendado para testes)**

1. Associe a sessão com usuário:
   ```bash
   POST /api/adk/sessions/{session_id}/associate
   ```

2. Use o ADK normalmente - o contexto será injetado automaticamente

3. Salve mensagens manualmente via API (se necessário)

### **Opção 2: Webhook Automático**

Crie um middleware HTTP que intercepta requisições do ADK e:

1. Extrai `session_id` da requisição
2. Chama `POST /api/adk/webhook/message` para salvar mensagens
3. Injeta contexto antes de processar

### **Opção 3: Middleware Customizado**

Você pode criar um middleware que:

```python
from src.services.adk_context_hooks import set_session_context, inject_context_into_agent

# Antes de processar mensagem
set_session_context(session_id="...", user_id=...)
inject_context_into_agent(agent)

# Processar mensagem
response = agent.process(message)

# Salvar mensagens
save_to_redis(session_id, "user", message)
save_to_redis(session_id, "assistant", response)
```

---

## 🎯 Exemplo Completo

### **1. Criar Agente via API**

```bash
POST /api/agents
{
  "name": "Meu Agente",
  "instruction": "Você é um assistente útil...",
  "model": "gemini-2.0-flash-exp"
}
```

### **2. Iniciar ADK Web**

```bash
./start_adk_web.sh
```

### **3. Associar Sessão**

Quando você criar uma sessão no ADK Web, obtenha o `session_id` e associe:

```bash
POST /api/adk/sessions/abc123/associate
Authorization: Bearer {token}
```

### **4. Conversar**

O agente agora usa contexto automaticamente!

- Primeira mensagem: Sem contexto (normal)
- Segunda mensagem: Usa contexto da primeira mensagem
- Terceira mensagem: Usa contexto das duas anteriores
- E assim por diante...

---

## 🔍 Verificação

### **Verificar se Contexto está Sendo Injetado**

1. Verifique os logs do servidor ADK ao iniciar
2. Procure por mensagens como:
   - `✓ Context injected into agent_1`
   - `⚠ Warning: Could not inject context` (se falhar)

### **Verificar Contexto no Redis**

```bash
# Conectar ao Redis
redis-cli -h localhost -p 6379

# Ver sessões do usuário
SMEMBERS sessions:user:1

# Ver histórico de uma sessão
LRANGE conversation:user:1:session:abc123 0 -1
```

### **Verificar via API**

```bash
GET /api/conversations/sessions/{session_id}
Authorization: Bearer {token}
```

---

## ⚙️ Configuração Avançada

### **Limitar Histórico de Contexto**

```env
MAX_CONVERSATION_HISTORY=50  # Apenas últimas 50 mensagens
```

### **Desabilitar Contexto**

Se você quiser desabilitar a injeção de contexto:

1. Remova a importação do hook nos agentes gerados
2. Ou simplesmente não associe sessões com usuários

---

## 🐛 Troubleshooting

### **Contexto não está sendo injetado**

1. Verifique se Redis está rodando:
   ```bash
   docker-compose ps | grep redis
   ```

2. Verifique se sessão está associada:
   ```bash
   GET /api/adk/sessions/{session_id}/associate
   ```

3. Verifique logs do servidor para erros

### **Mensagens não estão sendo salvas**

1. Verifique se Redis está conectado
2. Verifique se `user_id` está disponível
3. Use o endpoint `/api/adk/webhook/message` para salvar manualmente

### **Agente não usa contexto**

1. Verifique se `session_id` está disponível
2. Verifique se há mensagens anteriores no Redis
3. Verifique se a injeção de contexto funcionou (logs)

---

## 📚 Próximos Passos

Para integração **completamente automática**, você pode:

1. **Criar um middleware HTTP** que intercepta requisições do ADK
2. **Modificar o servidor ADK** para incluir hooks de mensagem
3. **Usar callbacks do ADK** (se disponíveis) para salvar mensagens

Mas a solução atual já funciona muito bem para a maioria dos casos!

---

## ✅ Status da Implementação

| Componente | Status |
|------------|--------|
| Serviço de Integração | ✅ Completo |
| Hooks de Contexto | ✅ Completo |
| Injeção Automática | ✅ Completo |
| Endpoints de API | ✅ Completo |
| Documentação | ✅ Completo |
| Salvamento Automático | ⚠️ Requer middleware externo |

**Nota:** O salvamento automático de mensagens requer middleware externo ou modificação do servidor ADK. A injeção de contexto funciona automaticamente!

