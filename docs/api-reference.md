# 📡 API Endpoints - Guia de Referência Rápida

## 🔐 **Autenticação**

```bash
POST /api/auth/register      # Registrar usuário
POST /api/auth/login         # Login (obter token)
GET  /api/auth/me            # Usuário atual
```

---

## 🤖 **Agentes**

```bash
GET    /api/agents                    # Listar agentes
POST   /api/agents                    # Criar agente
GET    /api/agents/{agent_id}         # Obter agente
PUT    /api/agents/{agent_id}         # Atualizar agente
DELETE /api/agents/{agent_id}         # Deletar agente
```

---

## 💬 **Chat com Agentes** ✅ **NOVO**

```bash
POST /api/agents/chat                 # Chat (usa primeiro agente)
POST /api/agents/{agent_id}/chat      # Chat com agente específico
```

**Request:**
```json
{
  "message": "Olá!",
  "session_id": "sessao123",  // Opcional - para contexto
  "agent_id": 1                // Opcional (só no /chat)
}
```

**Response:**
```json
{
  "response": "Olá! Como posso ajudar?",
  "agent_id": 1,
  "agent_name": "Meu Agente",
  "session_id": "sessao123"
}
```

---

## 📝 **Conversas**

```bash
GET    /api/conversations/sessions                    # Listar sessões
GET    /api/conversations/sessions/{session_id}       # Histórico
GET    /api/conversations/sessions/{session_id}/info   # Info da sessão
POST   /api/conversations/sessions/{session_id}/messages  # Adicionar mensagem
DELETE /api/conversations/sessions/{session_id}      # Deletar sessão
DELETE /api/conversations/sessions                    # Deletar todas
```

---

## 🔗 **LobeChat Compatibility** ✅ **NOVO**

Endpoints compatíveis com frontend LobeChat (tRPC):

```bash
GET /api/messages                    # Obter mensagens (compatível com message.getMessages)
GET /api/sessions/grouped            # Sessões agrupadas (compatível com session.getGroupedSessions)
GET /api/topics                      # Tópicos (retorna vazio, compatível com topic.getTopics)
GET /api/plugins                     # Plugins locais (retorna vazio, compatível com plugin.getPlugins)
GET /api/market                      # Marketplace (retorna vazio, compatível com market.getPluginList)
```

**Detalhes:** Consulte `LOBECHAT_COMPAT_API.md` para documentação completa.

---

## 🔗 **Integração ADK**

```bash
POST /api/adk/sessions/{session_id}/associate      # Associar sessão
POST /api/adk/sessions/{session_id}/messages       # Salvar mensagem
POST /api/adk/webhook/message                     # Webhook
```

---

## 📚 **Documentação Completa**

Consulte `FRONTEND_CUSTOMIZADO.md` para:
- Guia completo de implementação
- Exemplos de código React
- Fluxo completo de interação
- Arquitetura detalhada

