# 🔗 LobeChat tRPC Compatibility API

Este documento descreve os endpoints criados para compatibilidade com o frontend LobeChat.

## 📋 Visão Geral

O frontend LobeChat usa tRPC para comunicação com o backend. Para manter compatibilidade sem usar tRPC, criamos endpoints REST que mapeiam para as chamadas tRPC originais.

## 🎯 Endpoints Implementados

### 1. **GET /api/messages** - Obter Mensagens

**Compatível com:** `trpc/lambda/message.getMessages`

**Query Parameters:**
- `session_id` (optional): ID da sessão para filtrar mensagens
- `topic_id` (optional): Não usado, mantido para compatibilidade
- `limit` (optional): Número máximo de mensagens (padrão: 100)

**Exemplo:**
```bash
GET /api/messages?session_id=sess_123&limit=50
```

**Response:**
```json
[
  {
    "role": "user",
    "content": "Olá!",
    "timestamp": "2025-11-18T10:30:00",
    "metadata": {}
  },
  {
    "role": "assistant",
    "content": "Olá! Como posso ajudar?",
    "timestamp": "2025-11-18T10:30:05",
    "metadata": {}
  }
]
```

---

### 2. **GET /api/sessions/grouped** - Sessões Agrupadas

**Compatível com:** `trpc/lambda/session.getGroupedSessions`

**Exemplo:**
```bash
GET /api/sessions/grouped
```

**Response:**
```json
[
  {
    "date": "2025-11-18",
    "sessions": [
      {
        "session_id": "sess_123",
        "title": "Conversa sobre Python",
        "message_count": 10,
        "last_activity": "2025-11-18T10:30:00",
        "ttl": 3600
      }
    ]
  },
  {
    "date": "2025-11-17",
    "sessions": [
      {
        "session_id": "sess_456",
        "title": "Dúvidas sobre API",
        "message_count": 5,
        "last_activity": "2025-11-17T15:20:00",
        "ttl": null
      }
    ]
  }
]
```

**Notas:**
- Sessões são agrupadas por data (YYYY-MM-DD)
- Título é gerado automaticamente a partir da primeira mensagem
- Ordenadas por data decrescente

---

### 3. **GET /api/topics** - Tópicos

**Compatível com:** `trpc/lambda/topic.getTopics`

**Query Parameters:**
- `session_id` (optional): Não usado, mantido para compatibilidade

**Exemplo:**
```bash
GET /api/topics?session_id=sess_123
```

**Response:**
```json
[]
```

**Nota:** Retorna array vazio pois funcionalidade de tópicos não é essencial.

---

### 4. **GET /api/plugins** - Plugins Locais

**Compatível com:** `trpc/lambda/plugin.getPlugins`

**Exemplo:**
```bash
GET /api/plugins
```

**Response:**
```json
[]
```

**Nota:** Retorna array vazio pois plugins locais não são usados.

---

### 5. **GET /api/market** - Marketplace

**Compatível com:** `trpc/lambda/market.getPluginList`

**Query Parameters:**
- `category` (optional): Categoria de filtro (não usado)
- `locale` (optional): Locale (padrão: "en", não usado)

**Exemplo:**
```bash
GET /api/market?category=assistant&locale=pt-BR
```

**Response:**
```json
{
  "plugins": [],
  "categories": [],
  "total": 0
}
```

**Nota:** Retorna marketplace vazio pois usamos o marketplace público do LobeChat.

---

## 🔐 Autenticação

Todos os endpoints requerem autenticação via JWT token no header:

```bash
Authorization: Bearer <token>
```

## 📊 Mapeamento tRPC → REST

| tRPC Call | REST Endpoint | Status |
|-----------|---------------|--------|
| `message.getMessages` | `GET /api/messages` | ✅ Implementado |
| `session.getGroupedSessions` | `GET /api/sessions/grouped` | ✅ Implementado |
| `topic.getTopics` | `GET /api/topics` | ✅ Retorna vazio |
| `plugin.getPlugins` | `GET /api/plugins` | ✅ Retorna vazio |
| `market.getPluginList` | `GET /api/market` | ✅ Retorna vazio |

## 🎨 Integração com Frontend

O frontend LobeChat pode ser configurado para usar estes endpoints ao invés de tRPC quando `NEXT_PUBLIC_ENABLE_CUSTOM_AUTH=1`.

**Exemplo de configuração no frontend:**

```typescript
// Interceptar chamadas tRPC e redirecionar para REST
const apiClient = {
  message: {
    getMessages: async (params) => {
      const response = await fetch(
        `${API_URL}/api/messages?session_id=${params.sessionId}&limit=${params.limit}`,
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );
      return response.json();
    }
  },
  // ... outros endpoints
};
```

## 📝 Notas de Implementação

1. **Endpoints Vazios**: Alguns endpoints retornam arrays/objetos vazios pois as funcionalidades não são essenciais:
   - Topics: Organização secundária de mensagens
   - Plugins: Sistema de plugins local não usado
   - Market: Marketplace público usado ao invés de custom

2. **Compatibilidade**: Todos os endpoints mantêm a mesma estrutura de resposta esperada pelo LobeChat para evitar quebras no frontend.

3. **Performance**: Endpoints de mensagens e sessões são otimizados para usar Redis quando disponível, com fallback para PostgreSQL.

4. **Segurança**: Todos os endpoints verificam autenticação e filtram dados por `user_id` para garantir isolamento entre usuários.

## 🔄 Próximos Passos

Se necessário implementar funcionalidades completas:

- [ ] Sistema de tópicos completo (agrupamento de mensagens)
- [ ] Sistema de plugins local
- [ ] Marketplace customizado

Por enquanto, os endpoints vazios são suficientes para manter compatibilidade com o frontend.

