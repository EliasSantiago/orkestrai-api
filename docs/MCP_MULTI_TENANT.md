# 🔐 MCP Multi-Tenant Setup - Cada Usuário com Seu Próprio Notion

Este documento explica o sistema multi-tenant do MCP, onde cada usuário pode conectar sua própria conta do Notion.

## 🎯 Visão Geral

O sistema agora suporta **multi-tenancy** para integrações MCP:
- ✅ Cada usuário conecta sua própria conta do Notion
- ✅ Credenciais criptografadas e armazenadas por usuário
- ✅ Agentes de cada usuário só acessam o Notion daquele usuário
- ✅ Isolamento completo entre usuários

## 🏗️ Arquitetura

### Modelo de Dados

A tabela `mcp_connections` armazena as credenciais de cada usuário:

```python
class MCPConnection(Base):
    user_id: int              # ID do usuário
    provider: str             # "notion", "github", etc.
    encrypted_credentials: str # Credenciais criptografadas
    is_active: bool           # Se a conexão está ativa
    connected_at: datetime    # Quando foi conectado
    last_used_at: datetime    # Último uso
    metadata: dict            # Metadados
```

### Criptografia

As credenciais são criptografadas usando **Fernet** (AES 128):
- Chave de criptografia: `MCP_ENCRYPTION_KEY` (variável de ambiente)
- Geração automática em desenvolvimento (com aviso)
- **OBRIGATÓRIA** em produção

### Gerenciamento de Clientes

O `UserMCPClientManager` gerencia clientes MCP por usuário:
- Cache de clientes conectados
- Carregamento sob demanda do banco de dados
- Desconexão automática

## 📋 Configuração

### 1. Variável de Ambiente

Adicione no `.env`:

```bash
# Chave de criptografia para credenciais MCP (OBRIGATÓRIA em produção)
MCP_ENCRYPTION_KEY=your_fernet_key_here
```

Para gerar uma chave:
```python
from cryptography.fernet import Fernet
key = Fernet.generate_key()
print(key.decode())  # Use este valor no .env
```

### 2. Migração do Banco de Dados

Execute a migração para criar a tabela:

```bash
# Se usar Alembic
alembic revision --autogenerate -m "Add MCP connections table"
alembic upgrade head

# Ou execute manualmente o SQL
```

SQL manual:
```sql
CREATE TABLE mcp_connections (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    provider VARCHAR(50) NOT NULL,
    encrypted_credentials TEXT NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    connected_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_used_at TIMESTAMP,
    expires_at TIMESTAMP,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_mcp_connections_user_provider ON mcp_connections(user_id, provider);
CREATE INDEX idx_mcp_connections_provider ON mcp_connections(provider);
```

## 🔌 API Endpoints

### Conectar Notion

```bash
POST /api/mcp/notion/connect
Authorization: Bearer <token>

{
  "api_key": "secret_..."
}
```

### Verificar Status

```bash
GET /api/mcp/notion/status
Authorization: Bearer <token>
```

### Desconectar Notion

```bash
DELETE /api/mcp/notion/disconnect
Authorization: Bearer <token>
```

### Listar Conexões

```bash
GET /api/mcp/connections
Authorization: Bearer <token>
```

## 🛠️ Uso nos Agentes

### 1. Usuário Conecta Notion

```bash
curl -X POST "http://localhost:8001/api/mcp/notion/connect" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"api_key": "secret_..."}'
```

### 2. Criar Agente com Ferramentas Notion

```bash
POST /api/agents
{
  "name": "Assistente Notion",
  "tools": [
    "notion_read_page",
    "notion_search_pages",
    "notion_create_page",
    "notion_update_page",
    "notion_append_blocks",
    "notion_get_database",
    "notion_query_database"
  ]
}
```

### 3. Usar o Agente

O agente automaticamente usa a conexão Notion do usuário que fez a requisição.

```bash
POST /api/agents/chat
{
  "agent_id": 1,
  "message": "Busque páginas sobre reuniões no meu Notion"
}
```

## 🔒 Segurança

### Boas Práticas

1. **Criptografia**: Sempre use `MCP_ENCRYPTION_KEY` em produção
2. **Isolamento**: Cada usuário só acessa suas próprias credenciais
3. **Validação**: Tokens são validados antes de cada uso
4. **Logs**: Todas as operações são logadas (sem credenciais)

### Recomendações

- ✅ Use HTTPS em produção
- ✅ Rotacione `MCP_ENCRYPTION_KEY` periodicamente
- ✅ Monitore tentativas de acesso não autorizado
- ✅ Implemente rate limiting por usuário
- ✅ Valide permissões do Notion antes de usar

## 📊 Ferramentas Disponíveis

### Páginas
- `notion_read_page` - Ler página
- `notion_read_page_content` - Ler conteúdo completo
- `notion_search_pages` - Buscar páginas
- `notion_create_page` - Criar página
- `notion_update_page` - Atualizar página
- `notion_archive_page` - Arquivar página
- `notion_restore_page` - Restaurar página

### Blocos
- `notion_get_block` - Obter bloco
- `notion_get_block_children` - Obter blocos filhos
- `notion_update_block` - Atualizar bloco
- `notion_delete_block` - Deletar bloco
- `notion_append_blocks` - Adicionar blocos

### Bancos de Dados
- `notion_get_database` - Obter banco
- `notion_create_database` - Criar banco
- `notion_update_database` - Atualizar banco
- `notion_query_database` - Consultar banco

### Usuários
- `notion_list_users` - Listar usuários
- `notion_get_user` - Obter usuário
- `notion_get_bot_user` - Obter bot user

### Comentários
- `notion_create_comment` - Criar comentário
- `notion_list_comments` - Listar comentários

## 🔍 Troubleshooting

### Erro: "Notion not connected"

**Causa**: Usuário não conectou sua conta Notion.

**Solução**: 
1. Conecte usando `POST /api/mcp/notion/connect`
2. Verifique se a API key está correta

### Erro: "MCP_ENCRYPTION_KEY not set"

**Causa**: Chave de criptografia não configurada.

**Solução**: Adicione `MCP_ENCRYPTION_KEY` no `.env`

### Erro: "Failed to decrypt credentials"

**Causa**: Chave de criptografia mudou ou credenciais corrompidas.

**Solução**: 
1. Reconecte a conta Notion
2. Verifique se `MCP_ENCRYPTION_KEY` está correto

### Agente não encontra Notion

**Causa**: Usuário não conectou Notion OU agente não tem ferramentas Notion.

**Solução**:
1. Verifique conexão: `GET /api/mcp/notion/status`
2. Verifique se agente tem ferramentas Notion na lista `tools`

## 📚 Próximos Passos

1. **Adicionar mais providers**: GitHub, Slack, etc.
2. **OAuth 2.0**: Implementar fluxo OAuth para Notion (mais seguro)
3. **Webhooks**: Receber notificações do Notion
4. **Analytics**: Monitorar uso por usuário

## 🏢 Padrão Empresarial

Este sistema segue as melhores práticas de empresas como:
- **Slack**: Cada workspace tem suas próprias credenciais
- **Zapier**: Isolamento completo entre contas
- **Microsoft Teams**: Multi-tenant com criptografia

**Características implementadas:**
- ✅ Criptografia de credenciais
- ✅ Isolamento por usuário
- ✅ Cache eficiente
- ✅ Logs e auditoria
- ✅ Validação de permissões

