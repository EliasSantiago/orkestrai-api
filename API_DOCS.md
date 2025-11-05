# Documentação da API

API REST para gerenciamento de usuários e agentes.

## 🚀 Iniciar a API

```bash
./start_api.sh
```

A API estará disponível em:
- **API**: http://localhost:8001
- **Documentação Interativa**: http://localhost:8001/docs
- **Documentação Alternativa**: http://localhost:8001/redoc

## 📋 Endpoints

### Autenticação

#### POST `/api/auth/register`
Registrar um novo usuário.

**Request Body:**
```json
{
  "name": "João Silva",
  "email": "joao@example.com",
  "password": "senha123",
  "password_confirm": "senha123"
}
```

**Validações:**
- `password` e `password_confirm` devem ser iguais
- `name` deve ser único
- `email` deve ser único e válido

**Response:**
```json
{
  "id": 1,
  "name": "João Silva",
  "email": "joao@example.com",
  "is_active": true
}
```

#### POST `/api/auth/login`
Fazer login e obter token de acesso.

**Request Body (JSON):**
```json
{
  "email": "joao@example.com",
  "password": "senha123"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

#### GET `/api/auth/me`
Obter informações do usuário atual (requer autenticação).

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "id": 1,
  "name": "João Silva",
  "email": "joao@example.com",
  "is_active": true
}
```

### Agentes

Todos os endpoints de agentes requerem autenticação.

**Headers necessários:**
```
Authorization: Bearer <token>
```

#### POST `/api/agents`
Criar um novo agente.

**Request Body:**
```json
{
  "name": "Meu Agente",
  "description": "Descrição do agente",
  "instruction": "Você é um assistente útil...",
  "model": "gemini-2.0-flash-exp",
  "tools": ["calculator", "get_current_time"]
}
```

**Campos do Agent (conforme ADK):**
- `name` (string, obrigatório): Nome do agente
- `description` (string, opcional): Descrição do agente
- `instruction` (string, obrigatório): Instruções para o agente (system prompt)
- `model` (string, padrão: "gemini-2.0-flash-exp"): Modelo LLM a usar
- `tools` (array de strings, opcional): Lista de **nomes** de ferramentas disponíveis

**Tools Disponíveis:**
- `"calculator"` - Calculadora matemática
- `"get_current_time"` - Informações de data/hora

**⚠️ Importante sobre Tools:**
- Passe apenas o **nome da função** como string no array
- Exemplo correto: `["calculator", "get_current_time"]`
- Não precisa passar objetos ou funções completas

**Consulte `AGENT_CREATION_GUIDE.md` para exemplos completos de payloads.**

**Response:**
```json
{
  "id": 1,
  "name": "Meu Agente",
  "description": "Descrição do agente",
  "instruction": "Você é um assistente útil...",
  "model": "gemini-2.0-flash-exp",
  "tools": ["calculator", "get_current_time"],
  "user_id": 1,
  "created_at": "2024-11-04T00:00:00",
  "updated_at": "2024-11-04T00:00:00"
}
```

#### GET `/api/agents`
Listar todos os agentes do usuário atual.

**Response:**
```json
[
  {
    "id": 1,
    "name": "Meu Agente",
    "description": "...",
    "instruction": "...",
    "model": "gemini-2.0-flash-exp",
    "tools": ["calculator"],
    "user_id": 1,
    "created_at": "2024-11-04T00:00:00",
    "updated_at": "2024-11-04T00:00:00"
  }
]
```

#### GET `/api/agents/{agent_id}`
Obter um agente específico por ID.

#### PUT `/api/agents/{agent_id}`
Atualizar um agente.

**Request Body:**
```json
{
  "name": "Nome Atualizado",
  "description": "Nova descrição",
  "instruction": "Novas instruções",
  "model": "gemini-1.5-pro",
  "tools": ["calculator", "get_current_time"]
}
```

#### DELETE `/api/agents/{agent_id}`
Deletar um agente (soft delete).

## 🗄️ Estrutura do Banco de Dados

### Tabela `users`
- `id` (PK): ID do usuário
- `name`: Nome do usuário (único)
- `email`: Email (único)
- `hashed_password`: Senha criptografada
- `is_active`: Status ativo/inativo
- `created_at`: Data de criação
- `updated_at`: Data de atualização

### Tabela `agents`
- `id` (PK): ID do agente
- `name`: Nome do agente
- `description`: Descrição do agente
- `instruction`: Instruções para o agente (conforme ADK)
- `model`: Modelo LLM (conforme ADK)
- `tools`: Lista de ferramentas (JSON array)
- `user_id` (FK): ID do usuário dono
- `is_active`: Status ativo/inativo
- `created_at`: Data de criação
- `updated_at`: Data de atualização

## 🔐 Autenticação

A API usa JWT (JSON Web Tokens) para autenticação.

1. Faça login em `/api/auth/login` para obter um token
2. Use o token no header `Authorization: Bearer <token>` em todas as requisições protegidas
3. No Swagger UI, clique em "Authorize" e cole apenas o token (sem "Bearer")
4. O token expira em 30 dias

### Como usar no Swagger UI

1. Faça login em `/api/auth/login` para obter o token
2. Clique no botão "Authorize" no topo da página
3. Cole apenas o token (sem a palavra "Bearer")
4. Clique em "Authorize" e depois "Close"
5. Agora todas as requisições protegidas usarão o token automaticamente

## 📝 Exemplo de Uso

### 1. Registrar usuário
```bash
curl -X POST "http://localhost:8001/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test@example.com",
    "password": "senha123",
    "password_confirm": "senha123"
  }'
```

### 2. Fazer login
```bash
curl -X POST "http://localhost:8001/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "senha123"
  }'
```

**Nota:** O login agora usa email e senha via JSON.

### 3. Criar agente
```bash
curl -X POST "http://localhost:8001/api/agents" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Calculadora",
    "description": "Agente especializado em cálculos matemáticos",
    "instruction": "Você é um assistente especializado em cálculos matemáticos. Quando receber uma expressão matemática, use a ferramenta calculator para calcular o resultado. Apresente o resultado de forma clara e use português brasileiro.",
    "model": "gemini-2.0-flash-exp",
    "tools": ["calculator"]
  }'
```

**Exemplo com múltiplas tools:**
```bash
curl -X POST "http://localhost:8001/api/agents" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Assistente Completo",
    "description": "Pode fazer cálculos e informar a hora",
    "instruction": "Você é um assistente versátil. Use calculator para cálculos e get_current_time para informações de horário. Seja prestativo e use português brasileiro.",
    "model": "gemini-2.0-flash-exp",
    "tools": ["calculator", "get_current_time"]
  }'
```

### 4. Listar agentes
```bash
curl -X GET "http://localhost:8001/api/agents" \
  -H "Authorization: Bearer <token>"
```

## 🛠️ Ferramentas Disponíveis

As ferramentas que podem ser usadas nos agentes:
- `calculator`: Calculadora matemática
- `get_current_time`: Informações de data/hora

## ⚙️ Inicializar Banco de Dados

Antes de usar a API, inicialize o banco de dados:

```bash
# Certifique-se de que o PostgreSQL está rodando
docker-compose up -d

# Inicialize as tabelas
./init_database.sh
```

