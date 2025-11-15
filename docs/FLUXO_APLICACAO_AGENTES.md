# 📋 Fluxo Completo da Aplicação de Agentes

Este documento descreve o fluxo completo da aplicação, desde a criação de um agente até a conversa com ele, incluindo o gerenciamento de sessões e contexto.

## 📑 Índice

1. [Visão Geral](#visão-geral)
2. [Autenticação](#autenticação)
3. [Criação de Agente](#criação-de-agente)
4. [Sincronização Automática](#sincronização-automática)
5. [Iniciando uma Conversa](#iniciando-uma-conversa)
6. [Manutenção de Contexto](#manutenção-de-contexto)
7. [Fluxo Completo com Exemplos](#fluxo-completo-com-exemplos)
8. [Arquitetura de Dados](#arquitetura-de-dados)

---

## 🎯 Visão Geral

A aplicação permite criar agentes de IA usando o Google ADK e conversar com eles mantendo contexto de conversação. O sistema utiliza:

- **PostgreSQL**: Armazenamento persistente de usuários e agentes
- **Redis**: Armazenamento de contexto conversacional (sessões)
- **Google ADK**: Framework para execução de agentes
- **FastAPI**: API REST para interação

### Fluxo Simplificado

```
1. Autenticação → 2. Criar Agente → 3. Sincronização → 4. Chat → 5. Contexto
     ↓                ↓                  ↓              ↓          ↓
   Token JWT    PostgreSQL DB    Arquivos .agents_db  ADK Runner  Redis
```

---

## 🔐 Autenticação

### 1. Login

**Endpoint:** `POST /api/auth/login`

**Payload:**
```json
{
  "email": "usuario@example.com",
  "password": "senha123"
}
```

**Resposta:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**O que acontece:**
1. Sistema valida email e senha no PostgreSQL
2. Gera token JWT com `user_id` e `email`
3. Token expira em 30 dias (configurável)

**Uso do Token:**
- Incluir no header: `Authorization: Bearer {access_token}`
- Todas as requisições subsequentes precisam deste token

---

## 🤖 Criação de Agente

### 2. Criar Novo Agente

**Endpoint:** `POST /api/agents`

**Headers:**
```
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Payload:**
```json
{
  "name": "Calculadora",
  "description": "Agente especializado em cálculos matemáticos",
  "instruction": "Você é um assistente especializado em cálculos matemáticos. Quando receber uma expressão matemática, use a ferramenta 'calculator' para calcular o resultado.",
  "model": "gemini-2.0-flash-exp",
  "tools": ["calculator"]
}
```

**Resposta:**
```json
{
  "id": 5,
  "name": "Calculadora",
  "description": "Agente especializado em cálculos matemáticos",
  "instruction": "Você é um assistente especializado em cálculos matemáticos...",
  "model": "gemini-2.0-flash-exp",
  "tools": ["calculator"],
  "user_id": 1,
  "created_at": "2025-11-06T16:31:37.116810",
  "updated_at": "2025-11-06T16:31:37.116810"
}
```

**O que acontece:**

1. **Validação**: Sistema valida os dados do payload
2. **Sanitização**: Nome do agente é sanitizado para ser um identificador Python válido
   - Exemplo: "Assistente Completo" → "assistente_completo"
3. **Persistência**: Agente é salvo no PostgreSQL
   - Tabela: `agents`
   - Campos: `id`, `name`, `description`, `instruction`, `model`, `tools`, `user_id`, `is_active`
4. **Sincronização Automática**: Tarefa em background sincroniza para arquivos
   - Não bloqueia a resposta da API
   - Executa após a resposta ser enviada

---

## 🔄 Sincronização Automática

### 3. Sincronização para Arquivos

**Quando acontece:**
- Após criar um agente (`POST /api/agents`)
- Após atualizar um agente (`PUT /api/agents/{id}`)
- Após deletar um agente (`DELETE /api/agents/{id}`)

**O que acontece:**

1. **Background Task**: Sincronização executa em background (não bloqueia API)
2. **Carregamento**: Sistema carrega todos os agentes ativos do PostgreSQL
3. **Criação de Estrutura**: Cria diretórios em `.agents_db/agents/`
   - Formato: `{nome_sanitizado}_{id}/agent.py`
   - Exemplo: `calculadora_5/agent.py`
4. **Geração de Arquivos**: Cada agente recebe um arquivo `agent.py` com:
   - Importações necessárias
   - Configuração do Google API Key
   - Criação do objeto `Agent` do ADK
   - Hooks de contexto (se habilitado)

**Estrutura Criada:**
```
.agents_db/
└── agents/
    ├── assistente_completo_4/
    │   ├── __init__.py
    │   └── agent.py
    ├── calculadora_5/
    │   ├── __init__.py
    │   └── agent.py
    └── calculadora_8/
        ├── __init__.py
        └── agent.py
```

**Características:**
- Cada agente tem diretório único (nome + ID)
- Evita conflitos quando há agentes com mesmo nome
- Diretórios antigos são removidos automaticamente
- Arquivos são gerados automaticamente (não editar manualmente)

---

## 💬 Iniciando uma Conversa

### 4. Primeira Mensagem (Sem Session ID)

**Endpoint:** `POST /api/agents/chat`

**Headers:**
```
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Payload:**
```json
{
  "message": "Olá, meu nome é João Silva",
  "session_id": "",
  "agent_id": null
}
```

**Resposta:**
```json
{
  "response": "Olá João Silva, tudo bem? Em que posso te ajudar hoje?",
  "agent_id": 5,
  "agent_name": "Calculadora",
  "session_id": "session_674c7fd80927"
}
```

**O que acontece:**

1. **Geração de Session ID**: Se `session_id` estiver vazio, um novo é gerado
   - Formato: `session_{12_caracteres_hex}`
   - Exemplo: `session_674c7fd80927`

2. **Associação com Usuário**: Session ID é associado ao `user_id` do token
   - Permite recuperar contexto do usuário

3. **Seleção de Agente**:
   - Se `agent_id` fornecido: usa esse agente
   - Se `agent_id` null: usa o primeiro agente do usuário

4. **Criação do Agente ADK**:
   - Carrega dados do PostgreSQL
   - Sanitiza nome do agente
   - Mapeia tools (calculator, get_current_time)
   - Cria objeto `Agent` do Google ADK

5. **Salvamento da Mensagem**: Mensagem do usuário é salva no Redis
   - Chave: `conversation:{user_id}:{session_id}`
   - Formato: Lista de mensagens com `role` e `content`

6. **Injeção de Contexto**: Histórico de conversa é injetado na instrução do agente
   - Busca últimas 50 mensagens do Redis
   - Formata como texto e adiciona à instrução

7. **Criação do Runner**: `InMemoryRunner` é criado
   - Gerencia execução do agente
   - Cria `InvocationContext` automaticamente

8. **Criação de Sessão ADK**: Sessão é criada no serviço de sessão do ADK
   - Necessário para o Runner funcionar

9. **Execução do Agente**: `runner.run_async()` é chamado
   - Passa mensagem como `types.Content`
   - Retorna eventos assíncronos

10. **Processamento de Eventos**: Eventos são processados
    - Extrai texto de `event.content.parts`
    - Junta chunks em resposta completa

11. **Salvamento da Resposta**: Resposta do agente é salva no Redis
    - Role: "assistant"
    - Mantém histórico completo

12. **Retorno**: Resposta é retornada com `session_id` para uso futuro

---

## 🔄 Manutenção de Contexto

### 5. Continuando a Conversa (Com Session ID)

**Endpoint:** `POST /api/agents/chat`

**Payload:**
```json
{
  "message": "qual o meu nome?",
  "session_id": "session_674c7fd80927",
  "agent_id": null
}
```

**Resposta:**
```json
{
  "response": "Você me disse que seu nome é João Silva. Posso te ajudar com mais alguma coisa, João?",
  "agent_id": 5,
  "agent_name": "Calculadora",
  "session_id": "session_674c7fd80927"
}
```

**O que acontece:**

1. **Recuperação de Contexto**: Sistema busca histórico do Redis usando `session_id`
2. **Injeção na Instrução**: Histórico é formatado e injetado na instrução do agente
   ```
   CONVERSATION CONTEXT:
   Below is the recent conversation history. Use this context to provide relevant and coherent responses.
   
   Usuário: Olá, meu nome é João Silva
   Assistente: Olá João Silva, tudo bem? Em que posso te ajudar hoje?
   
   ---
   Continue the conversation naturally, using the context above to maintain coherence.
   ```
3. **Agente Responde**: Agente usa o contexto para responder de forma coerente

---

## 📊 Fluxo Completo com Exemplos

### Exemplo Completo: Criar Agente e Conversar

#### Passo 1: Autenticação
```bash
curl -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "usuario@example.com",
    "password": "senha123"
  }'
```

**Resposta:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### Passo 2: Criar Agente
```bash
curl -X POST http://localhost:8001/api/agents \
  -H "Authorization: Bearer {access_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Assistente Pessoal",
    "description": "Assistente que ajuda com tarefas do dia a dia",
    "instruction": "Você é um assistente pessoal útil e prestativo. Use português brasileiro.",
    "model": "gemini-2.0-flash-exp",
    "tools": []
  }'
```

**Resposta:**
```json
{
  "id": 9,
  "name": "Assistente Pessoal",
  "description": "Assistente que ajuda com tarefas do dia a dia",
  "instruction": "Você é um assistente pessoal útil e prestativo...",
  "model": "gemini-2.0-flash-exp",
  "tools": [],
  "user_id": 1,
  "created_at": "2025-11-06T17:30:00.000000",
  "updated_at": "2025-11-06T17:30:00.000000"
}
```

**O que acontece em background:**
- Arquivo criado: `.agents_db/agents/assistente_pessoal_9/agent.py`
- Agente disponível no ADK Web

#### Passo 3: Primeira Mensagem (Sem Session ID)
```bash
curl -X POST http://localhost:8001/api/agents/chat \
  -H "Authorization: Bearer {access_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Olá, meu nome é Maria e tenho 25 anos",
    "session_id": "",
    "agent_id": 9
  }'
```

**Resposta:**
```json
{
  "response": "Olá Maria, prazer em te conhecer! Como posso te ajudar hoje?",
  "agent_id": 9,
  "agent_name": "Assistente Pessoal",
  "session_id": "session_a1b2c3d4e5f6"
}
```

**Armazenado no Redis:**
```
conversation:1:session_a1b2c3d4e5f6 = [
  {"role": "user", "content": "Olá, meu nome é Maria e tenho 25 anos"},
  {"role": "assistant", "content": "Olá Maria, prazer em te conhecer! Como posso te ajudar hoje?"}
]
```

#### Passo 4: Segunda Mensagem (Com Session ID - Mantém Contexto)
```bash
curl -X POST http://localhost:8001/api/agents/chat \
  -H "Authorization: Bearer {access_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Quantos anos eu tenho?",
    "session_id": "session_a1b2c3d4e5f6",
    "agent_id": 9
  }'
```

**Resposta:**
```json
{
  "response": "Você tem 25 anos, Maria! Posso te ajudar com mais alguma coisa?",
  "agent_id": 9,
  "agent_name": "Assistente Pessoal",
  "session_id": "session_a1b2c3d4e5f6"
}
```

**Contexto Injetado no Agente:**
```
CONVERSATION CONTEXT:
Below is the recent conversation history. Use this context to provide relevant and coherent responses.

Usuário: Olá, meu nome é Maria e tenho 25 anos
Assistente: Olá Maria, prazer em te conhecer! Como posso te ajudar hoje?

---
Continue the conversation naturally, using the context above to maintain coherence.
```

---

## 🗄️ Arquitetura de Dados

### PostgreSQL - Tabela `agents`

```sql
CREATE TABLE agents (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    instruction TEXT NOT NULL,
    model VARCHAR(100) NOT NULL,
    tools JSONB DEFAULT '[]',
    user_id INTEGER NOT NULL REFERENCES users(id),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

**Campos:**
- `id`: Identificador único do agente
- `name`: Nome do agente (será sanitizado para diretório)
- `description`: Descrição do agente
- `instruction`: Instruções/prompt do agente
- `model`: Modelo do Gemini a usar (ex: "gemini-2.0-flash-exp")
- `tools`: Lista de tools disponíveis (ex: ["calculator", "get_current_time"])
- `user_id`: ID do usuário proprietário
- `is_active`: Se o agente está ativo (soft delete)

### Redis - Estrutura de Contexto

**Chave:** `conversation:{user_id}:{session_id}`

**Tipo:** Lista (Redis List)

**Formato:**
```json
[
  {
    "role": "user",
    "content": "Mensagem do usuário",
    "timestamp": "2025-11-06T17:30:00"
  },
  {
    "role": "assistant",
    "content": "Resposta do agente",
    "timestamp": "2025-11-06T17:30:05"
  }
]
```

**TTL:** 24 horas (configurável em `Config.CONVERSATION_TTL`)

**Limite:** Últimas 100 mensagens (configurável em `Config.MAX_CONVERSATION_HISTORY`)

### Redis - Associação Session → User

**Chave:** `session_user:{session_id}`

**Valor:** `{user_id}` (string)

**Propósito:** Permite recuperar `user_id` a partir de `session_id`

---

## 🔄 Fluxo Detalhado: Criação até Conversa

### Diagrama de Sequência

```
Cliente                    API                    PostgreSQL          Redis              ADK
  │                         │                         │                │                 │
  │─── POST /api/agents ───>│                         │                │                 │
  │                         │─── INSERT agent ───────>│                │                 │
  │                         │<─── agent (id=5) ───────│                │                 │
  │<─── 201 Created ────────│                         │                │                 │
  │                         │                         │                │                 │
  │                         │─── Background Task ───────────────────────────────────────>│
  │                         │                         │                │                 │
  │                         │                         │                │                 │
  │─── POST /api/agents/chat ───────────────────────────────────────────────────────────>│
  │                         │                         │                │                 │
  │                         │─── SELECT agent ───────>│                │                 │
  │                         │<─── agent data ────────│                │                 │
  │                         │                         │                │                 │
  │                         │─── LPUSH message ───────────────────────>│                 │
  │                         │                         │                │                 │
  │                         │─── LRANGE history ─────────────────────>│                 │
  │                         │<─── conversation ──────────────────────│                 │
  │                         │                         │                │                 │
  │                         │─── Create Agent ──────────────────────────────────────────>│
  │                         │─── Inject Context ────────────────────────────────────────>│
  │                         │─── Create Runner ─────────────────────────────────────────>│
  │                         │─── run_async() ──────────────────────────────────────────>│
  │                         │<─── events ──────────────────────────────────────────────│
  │                         │                         │                │                 │
  │                         │─── LPUSH response ─────────────────────>│                 │
  │                         │                         │                │                 │
  │<─── 200 OK ─────────────│                         │                │                 │
```

---

## 📝 Pontos Importantes

### 1. Session ID Automático

- Se não fornecido, é gerado automaticamente
- Formato: `session_{12_caracteres_hex}`
- Retornado na resposta para uso futuro

### 2. Contexto Automático

- Contexto é injetado automaticamente quando `session_id` é fornecido
- Não é necessário chamar endpoints separados
- Histórico é recuperado do Redis e injetado na instrução

### 3. Sincronização em Background

- Criação/atualização de agentes não bloqueia a API
- Sincronização acontece após resposta ser enviada
- Se falhar, não afeta a operação principal

### 4. Nomes de Diretórios

- Sempre incluem ID do agente: `{nome}_{id}`
- Evita conflitos quando há agentes com mesmo nome
- Exemplo: `calculadora_5` e `calculadora_8`

### 5. Sanitização de Nomes

- Nomes são sanitizados para serem identificadores Python válidos
- Remove acentos, espaços, caracteres especiais
- Garante compatibilidade com ADK

---

## 🛠️ Endpoints Principais

### Autenticação
- `POST /api/auth/login` - Login e obter token
- `GET /api/auth/me` - Obter usuário atual

### Agentes
- `POST /api/agents` - Criar agente
- `GET /api/agents` - Listar agentes do usuário
- `GET /api/agents/{id}` - Obter agente específico
- `PUT /api/agents/{id}` - Atualizar agente
- `DELETE /api/agents/{id}` - Deletar agente (soft delete)

### Chat
- `POST /api/agents/chat` - Enviar mensagem e receber resposta
- `POST /api/agents/{agent_id}/chat` - Chat com agente específico

### Conversas
- `GET /api/conversations/sessions` - Listar sessões do usuário
- `GET /api/conversations/sessions/{session_id}` - Obter histórico de sessão
- `DELETE /api/conversations/sessions/{session_id}` - Deletar sessão

---

## 🔍 Troubleshooting

### Problema: Agente não aparece no ADK Web

**Solução:**
1. Verificar se agente está ativo: `is_active = true`
2. Verificar se sincronização executou: verificar logs
3. Verificar diretório: `.agents_db/agents/{nome}_{id}/`
4. Forçar sincronização manual se necessário

### Problema: Contexto não está sendo mantido

**Solução:**
1. Verificar se `session_id` está sendo passado
2. Verificar Redis: `redis-cli KEYS conversation:*`
3. Verificar TTL: sessões expiram em 24h
4. Verificar logs de injeção de contexto

### Problema: Erro ao criar agente

**Solução:**
1. Verificar autenticação (token válido)
2. Verificar formato do payload
3. Verificar se nome é válido (sem caracteres especiais)
4. Verificar logs do servidor

---

## 📚 Referências

- [Guia de Criação de Agentes](AGENT_CREATION_GUIDE.md)
- [Guia de Uso do Swagger](GUIA_SWAGGER_CHAT.md)
- [Documentação PostgreSQL Sessions](POSTGRESQL_SESSIONS.md)
- [Documentação Redis Conversations](redis-conversations.md)

---

**Última atualização:** 2025-11-06

