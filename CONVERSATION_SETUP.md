# Setup de Conversas com Redis

## ✅ Implementação Completa

### 1. Redis Adicionado ao Docker Compose ✅
- Serviço Redis configurado
- Porta 6379 exposta
- Persistência habilitada

### 2. Sistema de Conversas ✅
- Cliente Redis implementado (`src/redis_client.py`)
- Serviço de conversas (`src/conversation_service.py`)
- Middleware para ADK (`src/adk_conversation_middleware.py`)

### 3. API REST para Conversas ✅
- Endpoints em `/api/conversations`
- Endpoints de integração em `/api/adk`
- Schemas Pydantic criados

### 4. Tabela Agents ✅
- **A coluna `user_id` já existe** na tabela `agents`
- Todos os endpoints já garantem que apenas o dono acessa seus agentes
- `user_id` é definido automaticamente ao criar agente via API

## 🚀 Como Iniciar

### 1. Instalar Dependências

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Iniciar Serviços

```bash
# Iniciar PostgreSQL e Redis
./start_services.sh

# Ou manualmente
docker-compose up -d
```

### 3. Verificar Serviços

```bash
docker-compose ps
```

Deve mostrar:
- `agents_postgres` (PostgreSQL) - Running
- `agents_redis` (Redis) - Running

## 📝 Como Funciona

### Estrutura de Dados

**Redis Keys:**
```
conversation:user:{user_id}:session:{session_id}  # Lista de mensagens
sessions:user:{user_id}                            # Set de session_ids
session:user_id:{session_id}                      # Mapeamento sessão → usuário
```

**Formato das Mensagens:**
```json
{
  "role": "user|assistant",
  "content": "Texto da mensagem",
  "timestamp": "2025-11-04T23:00:00",
  "metadata": {}
}
```

### Fluxo de Uso

1. **Criar Agente** (via API):
   ```bash
   POST /api/agents
   # user_id é automaticamente definido do token JWT
   ```

2. **Usar no ADK**:
   - Criar sessão no ADK Web
   - Associar sessão: `POST /api/adk/sessions/{session_id}/associate`

3. **Salvar Mensagens**:
   - Manualmente: `POST /api/adk/sessions/{session_id}/messages`
   - Ou implementar hooks no ADK

4. **Recuperar Histórico**:
   ```bash
   GET /api/conversations/sessions/{session_id}
   ```

## 🔧 Configuração

### Variáveis de Ambiente (`.env`)

```env
# Redis (opcional - valores padrão já definidos)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Conversas (opcional)
CONVERSATION_TTL=86400          # 24 horas
MAX_CONVERSATION_HISTORY=100    # Máximo de mensagens
```

## 📚 Endpoints Disponíveis

### Conversas (`/api/conversations`)
- `GET /sessions` - Listar sessões do usuário
- `GET /sessions/{session_id}` - Histórico de uma sessão
- `GET /sessions/{session_id}/info` - Info da sessão
- `POST /sessions/{session_id}/messages` - Adicionar mensagem
- `DELETE /sessions/{session_id}` - Deletar sessão
- `DELETE /sessions` - Deletar todas as sessões

### Integração ADK (`/api/adk`)
- `POST /sessions/{session_id}/associate` - Associar sessão com usuário
- `POST /sessions/{session_id}/messages` - Salvar mensagem do ADK

## ✅ Verificações

1. **Tabela Agents**: `user_id` já existe ✅
2. **Endpoints**: Todos garantem isolamento por usuário ✅
3. **Redis**: Configurado e pronto para uso ✅
4. **API**: Endpoints de conversas criados ✅

## 📖 Documentação Completa

Consulte `REDIS_CONVERSATIONS.md` para documentação detalhada.

