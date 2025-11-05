# Sistema de Conversas com Redis

## ✅ Funcionalidades Implementadas

### 1. Redis no Docker Compose
- Serviço Redis adicionado ao `docker-compose.yml`
- Porta 6379 exposta
- Persistência de dados habilitada
- Health check configurado

### 2. Sistema de Conversas
- **Armazenamento**: Contexto de conversas por sessão no Redis
- **Isolamento**: Cada usuário tem suas próprias sessões
- **TTL**: Conversas expiram após 24 horas (configurável)
- **Histórico**: Até 100 mensagens por sessão (configurável)

### 3. API REST para Conversas
Endpoints disponíveis em `/api/conversations`:

- `GET /api/conversations/sessions` - Lista todas as sessões do usuário
- `GET /api/conversations/sessions/{session_id}` - Histórico de uma sessão
- `GET /api/conversations/sessions/{session_id}/info` - Informações da sessão
- `POST /api/conversations/sessions/{session_id}/messages` - Adicionar mensagem
- `DELETE /api/conversations/sessions/{session_id}` - Deletar sessão
- `DELETE /api/conversations/sessions` - Deletar todas as sessões do usuário

### 4. Integração com ADK
Endpoints em `/api/adk`:

- `POST /api/adk/sessions/{session_id}/associate` - Associar sessão ADK com usuário
- `POST /api/adk/sessions/{session_id}/messages` - Salvar mensagem do ADK

## 🔧 Configuração

### Variáveis de Ambiente

Adicione ao `.env` (opcional, valores padrão já definidos):

```env
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
CONVERSATION_TTL=86400          # 24 horas em segundos
MAX_CONVERSATION_HISTORY=100    # Máximo de mensagens por sessão
```

### Iniciar Serviços

```bash
# Iniciar PostgreSQL e Redis
docker-compose up -d

# Verificar se estão rodando
docker-compose ps
```

## 📝 Estrutura de Dados no Redis

### Chaves

1. **Histórico de Conversa**:
   ```
   conversation:user:{user_id}:session:{session_id}
   ```
   - Tipo: List (Redis LIST)
   - Contém: Mensagens JSON em formato `{role, content, timestamp, metadata}`
   - TTL: 24 horas (configurável)

2. **Sessões do Usuário**:
   ```
   sessions:user:{user_id}
   ```
   - Tipo: Set (Redis SET)
   - Contém: Lista de session_ids do usuário
   - TTL: 24 horas

3. **Mapeamento Sessão → Usuário**:
   ```
   session:user_id:{session_id}
   ```
   - Tipo: String
   - Valor: user_id
   - TTL: 24 horas

### Formato das Mensagens

```json
{
  "role": "user|assistant|system",
  "content": "Texto da mensagem",
  "timestamp": "2025-11-04T23:00:00.000000",
  "metadata": {
    "agent_id": 1,
    "model": "gemini-2.0-flash-exp"
  }
}
```

## 🚀 Como Usar

### 1. Iniciar Serviços

```bash
# Iniciar Redis e PostgreSQL
docker-compose up -d

# Instalar dependências (se ainda não instalou)
pip install -r requirements.txt
```

### 2. Criar Agente (via API)

```bash
# 1. Login
POST http://localhost:8001/api/auth/login
{
  "email": "usuario@example.com",
  "password": "senha"
}

# 2. Criar agente (já usa user_id automaticamente)
POST http://localhost:8001/api/agents
Authorization: Bearer {token}
{
  "name": "Meu Agente",
  "instruction": "...",
  "model": "gemini-2.0-flash-exp",
  "tools": ["calculator"]
}
```

### 3. Usar Agente no ADK

```bash
# 1. Iniciar ADK Web
./start_adk_web.sh

# 2. Acessar http://localhost:8000
# 3. Criar uma nova sessão
# 4. Associar sessão com usuário (via API)
POST http://localhost:8001/api/adk/sessions/{session_id}/associate
Authorization: Bearer {token}
```

### 4. Salvar Mensagens

As mensagens podem ser salvas manualmente via API:

```bash
# Salvar mensagem do usuário
POST http://localhost:8001/api/adk/sessions/{session_id}/messages
Authorization: Bearer {token}
{
  "role": "user",
  "content": "Olá, como você está?"
}

# Salvar resposta do assistente
POST http://localhost:8001/api/adk/sessions/{session_id}/messages
Authorization: Bearer {token}
{
  "role": "assistant",
  "content": "Estou bem, obrigado!"
}
```

### 5. Recuperar Histórico

```bash
# Obter histórico de uma sessão
GET http://localhost:8001/api/conversations/sessions/{session_id}
Authorization: Bearer {token}

# Listar todas as sessões do usuário
GET http://localhost:8001/api/conversations/sessions
Authorization: Bearer {token}
```

## 🔍 Verificação da Tabela Agents

A tabela `agents` **já possui** a coluna `user_id`:

```python
# src/models.py
class Agent(Base):
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    owner = relationship("User", back_populates="agents")
```

Todos os endpoints de agents já garantem que:
- ✅ Apenas o dono do agente pode acessá-lo
- ✅ `user_id` é automaticamente definido ao criar agente
- ✅ Filtros por `user_id` em todas as consultas

## 📊 Exemplo de Uso Completo

```python
# 1. Criar agente (via API)
POST /api/agents
{
  "name": "Assistente",
  "instruction": "Você é um assistente...",
  "model": "gemini-2.0-flash-exp"
}
# user_id é automaticamente definido pelo token JWT

# 2. Usar agente no ADK
# - Iniciar sessão no ADK Web
# - Associar sessão: POST /api/adk/sessions/{session_id}/associate

# 3. Conversar
# - Mensagens são salvas automaticamente (se integrado)
# - Ou manualmente via POST /api/adk/sessions/{session_id}/messages

# 4. Recuperar contexto
GET /api/conversations/sessions/{session_id}
# Retorna histórico completo da conversa
```

## 🔄 Integração Automática (Futuro)

Para integração automática com o ADK, você pode:

1. **Hook no ADK**: Interceptar mensagens antes/depois do processamento
2. **Middleware**: Adicionar middleware no servidor ADK
3. **API Callbacks**: Configurar o ADK para chamar webhooks

Atualmente, as mensagens devem ser salvas manualmente via API ou você pode implementar hooks personalizados.

## ⚙️ Configurações Avançadas

### Ajustar TTL das Conversas

```env
CONVERSATION_TTL=172800  # 48 horas
```

### Limitar Histórico

```env
MAX_CONVERSATION_HISTORY=50  # Apenas últimas 50 mensagens
```

### Múltiplos Bancos Redis

```env
REDIS_DB=0  # Banco 0 (padrão)
REDIS_DB=1  # Banco 1 (para outro propósito)
```

## 🐛 Troubleshooting

### Redis não conecta

```bash
# Verificar se Redis está rodando
docker-compose ps

# Verificar logs
docker-compose logs redis

# Testar conexão
redis-cli -h localhost -p 6379 ping
```

### Mensagens não são salvas

1. Verifique se Redis está conectado
2. Verifique se `user_id` está no token JWT
3. Verifique se a sessão foi associada ao usuário
4. Verifique logs do servidor

### Histórico não aparece

1. Verifique se as mensagens foram salvas
2. Verifique se está usando o `session_id` correto
3. Verifique se o `user_id` corresponde ao token

## 📚 Documentação de API

Acesse `http://localhost:8001/docs` para ver a documentação completa da API com exemplos interativos.

