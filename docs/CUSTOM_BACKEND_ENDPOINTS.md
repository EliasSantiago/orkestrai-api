## Visão geral da API de backend usada pelo LobeChat (modo custom backend)

Este documento descreve **todos os endpoints HTTP** que o frontend do LobeChat utiliza quando o modo de **custom backend / custom auth** está habilitado (`NEXT_PUBLIC_ENABLE_CUSTOM_AUTH=1`), para que o seu backend possa implementar exatamente o contrato esperado.

- **Base URL**: configurada via `NEXT_PUBLIC_CUSTOM_API_BASE_URL` (ex.: `https://seu-backend.com/api`)
- **Autenticação**: todos os endpoints (exceto login e registro) usam **Bearer Token** no header `Authorization: Bearer <access_token>`
- **Formato de erro esperado**:
  - Preferencialmente: `{ "detail": [ { "msg": "Mensagem de erro legível" } ] }`
  - Alternativamente: `{ "message": "Mensagem de erro" }`
  - O frontend tenta ler `error.detail[0].msg` e, se não existir, `error.message`.

> Nas tabelas abaixo, as rotas são **relativas à Base URL**.  
> Exemplo: Base URL `https://seu-backend.com/api` + rota `auth/login` ⇒ `POST https://seu-backend.com/api/auth/login`.

---

## Tabela resumida de endpoints

| Grupo          | Método | Rota relativa                                   | Descrição rápida                                  |
|----------------|--------|-------------------------------------------------|---------------------------------------------------|
| Autenticação   | POST   | `auth/login`                                    | Login com e‑mail/senha                            |
| Autenticação   | POST   | `auth/register`                                 | Registro de novo usuário                          |
| Autenticação   | GET    | `auth/me`                                       | Dados do usuário autenticado                      |
| Agentes        | GET    | `agents`                                        | Listar agentes do usuário                         |
| Agentes        | GET    | `agents/{agentId}`                              | Detalhar um agente                                |
| Agentes        | POST   | `agents`                                        | Criar agente                                      |
| Agentes        | PUT    | `agents/{agentId}`                              | Atualizar agente                                  |
| Agentes        | DELETE | `agents/{agentId}`                              | Remover agente                                    |
| Chat           | POST   | `agents/chat`                                   | Enviar mensagem para um agente (chat)            |
| Sessões        | GET    | `conversations/sessions`                        | Listar IDs de sessões do usuário                  |
| Sessões        | GET    | `conversations/sessions/{sessionId}?limit={n}` | Histórico de mensagens de uma sessão              |
| Sessões        | GET    | `conversations/sessions/{sessionId}/info`      | Metadados de uma sessão                           |
| Sessões        | DELETE | `conversations/sessions/{sessionId}`           | Apagar uma sessão específica                      |
| Sessões        | DELETE | `conversations/sessions`                        | Apagar todas as sessões do usuário                |
| Sessões        | POST   | `conversations/sessions/{sessionId}/messages`  | Adicionar mensagem às mensagens da sessão         |
| Sessões        | POST   | `adk/sessions/{sessionId}/associate`           | Associar uma sessão ao usuário autenticado        |
| Preferências   | GET    | `/api/user/preferences`                         | Carregar preferências / settings do usuário       |
| Preferências   | PUT    | `/api/user/preferences`                         | Atualizar preferências / settings do usuário      |
| Preferências   | DELETE | `/api/user/preferences`                         | Resetar preferências / settings no backend        |

> Observação: as rotas de **preferências** estão sendo chamadas no código como `'/api/user/preferences'`.  
> Combine isso com a sua `NEXT_PUBLIC_CUSTOM_API_BASE_URL` de forma que o caminho final faça sentido (por exemplo, Base URL sem `/api` ou ajuste do path do backend).

---

## Autenticação

### POST `auth/login`

- **Descrição**: autentica o usuário e retorna um token de acesso.
- **Headers**:
  - `Content-Type: application/json`
- **Body (JSON)**:

```json
{
  "email": "user@example.com",
  "password": "string"
}
```

- **Resposta 200 (JSON)**:

```json
{
  "access_token": "jwt-ou-token",
  "token_type": "bearer"
}
```

- **Notas**:
  - O frontend salva `access_token` em `localStorage` e usa `Authorization: Bearer <access_token>` em todas as chamadas autenticadas.
  - Em caso de erro, retornar 4xx com corpo no formato de erro descrito na seção de visão geral.

---

### POST `auth/register`

- **Descrição**: registra um novo usuário.
- **Headers**:
  - `Content-Type: application/json`
- **Body (JSON)**:

```json
{
  "name": "Nome do Usuário",
  "email": "user@example.com",
  "password": "string",
  "password_confirm": "string"
}
```

- **Resposta 201/200 (JSON)**:

```json
{
  "id": 1,
  "name": "Nome do Usuário",
  "email": "user@example.com",
  "is_active": true
}
```

---

### GET `auth/me`

- **Descrição**: retorna os dados do usuário autenticado.
- **Headers**:
  - `Authorization: Bearer <access_token>`
- **Body**: vazio.
- **Resposta 200 (JSON)**:

```json
{
  "id": 1,
  "name": "Nome do Usuário",
  "email": "user@example.com",
  "is_active": true
}
```

- **Respostas de erro**:
  - `401 Unauthorized`: quando o token é inválido ou expirado. O frontend limpa o token local e considera o usuário deslogado.

---

## Agentes

### Modelo de dados esperado

**Resposta de agente** (`AgentResponse`):

```json
{
  "id": 1,
  "name": "Suporte",
  "description": "Atende dúvidas gerais",
  "instruction": "Você é um agente de suporte...",
  "model": "gpt-4o-mini",
  "tools": ["web_search", "file_search"],
  "use_file_search": true,
  "user_id": 1,
  "created_at": "2025-01-01T10:00:00Z",
  "updated_at": "2025-01-01T10:00:00Z"
}
```

**Criação (`AgentCreate`)**:

```json
{
  "name": "Suporte",
  "description": "Atende dúvidas gerais",
  "instruction": "Você é um agente de suporte...",
  "model": "gpt-4o-mini",
  "tools": ["web_search"],
  "use_file_search": true
}
```

**Atualização (`AgentUpdate`)** – todos os campos opcionais:

```json
{
  "name": "Suporte Atualizado",
  "description": null,
  "instruction": "Novo prompt do agente",
  "model": "gpt-4o-mini",
  "tools": ["web_search", "file_search"],
  "use_file_search": false
}
```

---

### GET `agents`

- **Descrição**: lista todos os agentes do usuário autenticado.
- **Headers**:
  - `Authorization: Bearer <access_token>`
- **Body**: vazio.
- **Resposta 200 (JSON)**:

```json
[
  {
    "id": 1,
    "name": "Suporte",
    "description": "Atende dúvidas gerais",
    "instruction": "Você é um agente de suporte...",
    "model": "gpt-4o-mini",
    "tools": ["web_search"],
    "use_file_search": true,
    "user_id": 1,
    "created_at": "2025-01-01T10:00:00Z",
    "updated_at": "2025-01-01T10:00:00Z"
  }
]
```

---

### GET `agents/{agentId}`

- **Descrição**: obtém um agente específico.
- **Headers**:
  - `Authorization: Bearer <access_token>`
- **Resposta 200 (JSON)**: objeto `AgentResponse`.

---

### POST `agents`

- **Descrição**: cria um novo agente.
- **Headers**:
  - `Authorization: Bearer <access_token>`
  - `Content-Type: application/json`
- **Body (JSON)**: objeto `AgentCreate`.
- **Resposta 201/200 (JSON)**: objeto `AgentResponse` criado.

---

### PUT `agents/{agentId}`

- **Descrição**: atualiza um agente existente.
- **Headers**:
  - `Authorization: Bearer <access_token>`
  - `Content-Type: application/json`
- **Body (JSON)**: objeto `AgentUpdate` (todos os campos opcionais).
- **Resposta 200 (JSON)**: objeto `AgentResponse` atualizado.

---

### DELETE `agents/{agentId}`

- **Descrição**: remove um agente.
- **Headers**:
  - `Authorization: Bearer <access_token>`
- **Resposta 204**: sem corpo.

---

## Chat com agentes

### Modelo de dados de chat

**Requisição (`ChatRequest`)**:

```json
{
  "message": "Texto da pergunta",
  "agent_id": 1,
  "session_id": "opcional-session-id-ou-null",
  "model": "opcional-model-id-ou-null"
}
```

**Resposta (`ChatResponse`)**:

```json
{
  "response": "Texto da resposta do agente",
  "agent_id": 1,
  "agent_name": "Suporte",
  "session_id": "session-id-gerado-ou-reusado",
  "model_used": "gpt-4o-mini"
}
```

---

### POST `agents/chat`

- **Descrição**: envia uma mensagem para um agente e recebe a resposta.
- **Headers**:
  - `Authorization: Bearer <access_token>`
  - `Content-Type: application/json`
- **Body (JSON)**: objeto `ChatRequest`.
- **Resposta 200 (JSON)**: objeto `ChatResponse`.
- **Notas**:
  - O backend pode criar automaticamente uma nova sessão se `session_id` vier nulo ou ausente.
  - `session_id` retornado é usado nas próximas chamadas para manter o histórico.

---

## Sessões e histórico de conversas

### Modelo de dados

**Mensagem de sessão (`SessionMessage`)**:

```json
{
  "role": "user ou assistant",
  "content": "Texto da mensagem",
  "timestamp": "2025-01-01T10:00:00Z",
  "metadata": {
    "qualquer_chave": "qualquer_valor"
  }
}
```

**Histórico de conversa (`ConversationHistory`)**:

```json
{
  "session_id": "session-id",
  "messages": [
    {
      "role": "user",
      "content": "Olá",
      "timestamp": "2025-01-01T10:00:00Z",
      "metadata": null
    }
  ]
}
```

**Info de sessão (`SessionInfo`)**:

```json
{
  "session_id": "session-id",
  "message_count": 42,
  "last_activity": "2025-01-01T10:00:00Z",
  "ttl": null
}
```

---

### GET `conversations/sessions`

- **Descrição**: lista todos os IDs de sessão do usuário atual.
- **Headers**:
  - `Authorization: Bearer <access_token>`
- **Resposta 200 (JSON)**:

```json
[
  "session-id-1",
  "session-id-2"
]
```

---

### GET `conversations/sessions/{sessionId}?limit={n}`

- **Descrição**: obtém o histórico de uma sessão, com limite opcional de mensagens.
- **Headers**:
  - `Authorization: Bearer <access_token>`
- **Query params**:
  - `limit` (opcional, inteiro): máximo de mensagens a retornar.
- **Resposta 200 (JSON)**: objeto `ConversationHistory`.

---

### GET `conversations/sessions/{sessionId}/info`

- **Descrição**: obtém informações resumidas da sessão.
- **Headers**:
  - `Authorization: Bearer <access_token>`
- **Resposta 200 (JSON)**: objeto `SessionInfo`.

---

### DELETE `conversations/sessions/{sessionId}`

- **Descrição**: remove uma sessão específica e seu histórico.
- **Headers**:
  - `Authorization: Bearer <access_token>`
- **Resposta 204**: sem corpo.

---

### DELETE `conversations/sessions`

- **Descrição**: remove todas as sessões do usuário autenticado.
- **Headers**:
  - `Authorization: Bearer <access_token>`
- **Resposta 204**: sem corpo.

---

### POST `conversations/sessions/{sessionId}/messages`

- **Descrição**: adiciona uma mensagem a uma sessão (sem necessariamente gerar resposta do modelo).
- **Headers**:
  - `Authorization: Bearer <access_token>`
  - `Content-Type: application/json`
- **Body (JSON)** – criação simples de mensagem:

```json
{
  "content": "Texto da mensagem",
  "metadata": {
    "qualquer_chave": "qualquer_valor"
  }
}
```

- **Resposta 204 ou 200**:
  - O frontend ignora o corpo da resposta; pode ser vazio.

---

### POST `adk/sessions/{sessionId}/associate`

- **Descrição**: associa uma sessão (por ID) ao usuário autenticado (útil quando a sessão foi criada antes do login).
- **Headers**:
  - `Authorization: Bearer <access_token>`
- **Body**: vazio.
- **Resposta 204 ou 200**:
  - O frontend não consome corpo; qualquer 2xx é considerado sucesso.

---

## Preferências e configurações de usuário

As preferências são usadas para sincronizar configurações de UI (tema, atalhos, guias, features de laboratório, etc.) entre frontend e backend.

> Importante: o código atual chama o endpoint como `customApiService.request('/api/user/preferences', ...)`.  
> Garanta que a combinação Base URL + `'/api/user/preferences'` resulte na URL correta do seu backend (por exemplo, Base URL = `https://seu-backend.com` ⇒ URL final `https://seu-backend.com/api/user/preferences`).

### Estrutura esperada (flexível)

O backend aceita/retorna um **JSON genérico**, por exemplo:

```json
{
  "useCmdEnterToSend": true,
  "guide": {
    "onboardingCompleted": true
  },
  "lab": {
    "newFeatureEnabled": false
  },
  "telemetry": false,
  "settings": {
    "theme": "dark",
    "language": "pt-BR"
  }
}
```

O frontend mapeia apenas algumas chaves específicas:

- `useCmdEnterToSend`
- `guide`
- `lab`
- `telemetry`
- `settings` (objeto aninhado com as configurações completas)

---

### GET `/api/user/preferences`

- **Descrição**: carrega preferências e settings do usuário para sincronizar com o client.
- **Headers**:
  - `Authorization: Bearer <access_token>`
- **Resposta 200 (JSON)**:
  - Objeto JSON com as chaves descritas acima (pode conter chaves extras ignoradas pelo frontend).

---

### PUT `/api/user/preferences`

- **Descrição**: atualiza preferências/settings no backend.
- **Headers**:
  - `Authorization: Bearer <access_token>`
  - `Content-Type: application/json`
- **Body (JSON)**:
  - Quando chamado a partir de `updatePreference`, envia apenas um subconjunto das chaves (por exemplo, só `guide` ou só `telemetry`).
  - Quando chamado a partir de `updateUserSettings`, envia um objeto com `{ "settings": { ... } }`.
- **Resposta 200/204**:
  - O frontend não depende do corpo da resposta.

---

### DELETE `/api/user/preferences`

- **Descrição**: reseta/remover todas as preferências/settings do usuário no backend.
- **Headers**:
  - `Authorization: Bearer <access_token>`
- **Resposta 204**:
  - Sem corpo.

---

## Resumo e recomendações

- **Autenticação**:
  - Use JWT ou similar e exponha `access_token` + `token_type` em `auth/login`.
  - Todos os demais endpoints devem validar `Authorization: Bearer <access_token>`.
- **Erros**:
  - Padronize para sempre retornar um JSON com `detail[0].msg` ou `message` para facilitar exibição de mensagens amigáveis no frontend.
- **Versionamento**:
  - Se for versionar a API (ex.: `/api/v1/...`), faça isso na `NEXT_PUBLIC_CUSTOM_API_BASE_URL` ou em prefixos estáveis, sem quebrar as rotas descritas acima.

Com este documento, o seu time de backend consegue implementar todo o contrato necessário para o LobeChat funcionar em modo **custom backend** (autenticação, agentes, chat, sessões e sincronização de preferências).


