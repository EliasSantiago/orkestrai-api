# Controle de RAG por Agente

## 🎯 Visão Geral

Agora você pode **controlar quais agentes têm acesso aos seus documentos** (File Search / RAG). Por padrão, **nenhum agente tem acesso** - você precisa habilitar explicitamente.

## 🔒 Segurança por Padrão (Opt-Out)

**Padrão:** `use_file_search = False`

- ✅ **Segurança**: Por padrão, agentes **NÃO** têm acesso aos documentos
- ✅ **Controle**: Você decide explicitamente quais agentes podem usar RAG
- ✅ **Privacidade**: Documentos não são acessados sem sua permissão explícita

## 📋 Como Funciona

### 1. Criar Agente SEM RAG (Padrão)

```json
{
  "name": "Assistente Geral",
  "description": "Agente para conversas gerais",
  "instruction": "Você é um assistente útil.",
  "model": "gemini-2.5-flash",
  "tools": [],
  "use_file_search": false  // ou omitir (padrão é false)
}
```

**Resultado:** Agente **NÃO** terá acesso aos documentos, mesmo que você tenha File Search Stores.

### 2. Criar Agente COM RAG

```json
{
  "name": "Assistente com RAG",
  "description": "Agente que responde baseado nos documentos",
  "instruction": "Use os documentos para responder perguntas.",
  "model": "gemini-2.5-flash",
  "tools": [],
  "use_file_search": true  // ✅ Habilita RAG
}
```

**Resultado:** Agente **TERÁ** acesso aos seus File Search Stores ativos.

### 3. Atualizar Agente para Habilitar/Desabilitar RAG

```bash
curl -X 'PUT' \
  'http://localhost:8001/api/agents/1' \
  -H 'Authorization: Bearer TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "use_file_search": true
  }'
```

## 🔍 Verificação no Código

O sistema verifica `agent_model.use_file_search` antes de adicionar File Search:

```python
# Em agent_chat_routes.py
if agent_model.use_file_search:
    # Busca File Search Stores e adiciona ao agente
    file_search_stores = [store.google_store_name for store in stores]
    # Adiciona File Search tool ao agente
else:
    # RAG desabilitado - não adiciona File Search
```

## 📊 Exemplo Completo

### Criar Agente com RAG

```bash
curl -X 'POST' \
  'http://localhost:8001/api/agents' \
  -H 'Authorization: Bearer TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "Assistente Documental",
    "description": "Responde perguntas baseado nos documentos",
    "instruction": "Você é um assistente especializado em responder perguntas baseado nos documentos fornecidos. Use as informações dos arquivos para dar respostas precisas. Sempre cite a fonte quando usar informações dos documentos.",
    "model": "gemini-2.5-flash",
    "tools": [],
    "use_file_search": true
  }'
```

### Criar Agente sem RAG

```bash
curl -X 'POST' \
  'http://localhost:8001/api/agents' \
  -H 'Authorization: Bearer TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "Assistente Geral",
    "description": "Agente para conversas gerais",
    "instruction": "Você é um assistente útil e prestativo.",
    "model": "gemini-2.5-flash",
    "tools": [],
    "use_file_search": false
  }'
```

## 🗄️ Migração do Banco de Dados

Execute a migração para adicionar a coluna:

```bash
psql -U agentuser -d agentsdb -f migrations/add_use_file_search_to_agents.sql
```

Ou manualmente:

```sql
ALTER TABLE agents 
ADD COLUMN use_file_search BOOLEAN NOT NULL DEFAULT FALSE;
```

## ✅ Vantagens desta Abordagem

1. **Segurança**: Opt-out por padrão - nenhum agente acessa documentos sem permissão
2. **Controle Granular**: Cada agente pode ter sua própria configuração
3. **Flexibilidade**: Pode habilitar/desabilitar a qualquer momento
4. **Conformidade**: Alinhado com boas práticas de privacidade de dados

## 📝 Notas Importantes

- **Apenas modelos Gemini**: RAG funciona apenas com modelos Gemini
- **Stores devem estar ativos**: Apenas stores com `is_active=True` são usados
- **Arquivos devem estar processados**: Aguarde status `completed` antes de usar
- **Mudanças são imediatas**: Atualizar `use_file_search` afeta a próxima conversa

