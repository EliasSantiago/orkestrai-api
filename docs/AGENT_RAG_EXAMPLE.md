# Criando um Agente com RAG (File Search)

## 🎯 Visão Geral

O RAG (Retrieval-Augmented Generation) já está **automaticamente habilitado** para agentes que usam modelos Gemini quando você tem File Search Stores ativos.

## ✅ Pré-requisitos

1. ✅ Ter pelo menos um **File Search Store** criado
2. ✅ Ter pelo menos um **arquivo** enviado para o store
3. ✅ Usar um **modelo Gemini** (recomendado: `gemini-2.5-flash`)

## 🚀 Como Criar um Agente com RAG

### 1. Criar o Agente

**Endpoint:** `POST /api/agents`

**Payload:**
```json
{
  "name": "Assistente com RAG",
  "description": "Agente que responde perguntas baseado nos documentos enviados",
  "instruction": "Você é um assistente especializado em responder perguntas baseado nos documentos fornecidos. Use as informações dos arquivos para dar respostas precisas e detalhadas. Sempre cite a fonte quando usar informações dos documentos.",
  "model": "gemini-2.5-flash",
  "tools": []
}
```

**Nota:** Você **NÃO precisa** passar nenhuma ferramenta no campo `tools`. O RAG é adicionado **automaticamente** pelo sistema.

### 2. Como Funciona

Quando você conversa com o agente:

1. **Sistema verifica** se você tem File Search Stores ativos
2. **Sistema adiciona automaticamente** a ferramenta File Search ao agente
3. **Agente usa RAG** para buscar informações nos seus documentos
4. **Agente responde** baseado nos documentos encontrados

### 3. Exemplo de Conversa

**Request:**
```bash
curl -X 'POST' \
  'http://localhost:8001/api/agents/chat' \
  -H 'Authorization: Bearer SEU_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "agent_id": 1,
    "message": "O que diz o documento sobre inteligência artificial?",
    "session_id": "sua-session-id"
  }'
```

**Resposta:**
O agente vai:
1. Buscar nos seus documentos usando File Search
2. Encontrar informações relevantes
3. Responder baseado no conteúdo encontrado
4. Citar as fontes quando apropriado

## 🔧 Configuração Automática

O sistema **automaticamente**:

1. **Busca File Search Stores ativos** do usuário
2. **Adiciona File Search tool** ao agente Gemini
3. **Passa os nomes dos stores** para o Google ADK

Código relevante em `src/api/agent_chat_routes.py`:

```python
# Get File Search Stores for the user (for RAG)
file_search_stores = []
try:
    from src.models import FileSearchStore
    stores = db.query(FileSearchStore).filter(
        FileSearchStore.user_id == user_id,
        FileSearchStore.is_active == True
    ).all()
    file_search_stores = [store.google_store_name for store in stores]
    if file_search_stores:
        logger.info(f"Found {len(file_search_stores)} active File Search Stores for user {user_id}")
except Exception as e:
    logger.warning(f"Could not load File Search Stores: {e}")

# Add to provider kwargs
provider_kwargs.update({
    "file_search_stores": file_search_stores if file_search_stores else None,
})
```

## 📋 Checklist

- [ ] Criar File Search Store
- [ ] Fazer upload de arquivos para o store
- [ ] Criar agente com modelo Gemini (`gemini-2.5-flash`)
- [ ] Conversar com o agente - RAG será usado automaticamente!

## ⚠️ Importante

- **Não precisa passar ferramentas**: O RAG é adicionado automaticamente
- **Apenas modelos Gemini**: RAG funciona apenas com modelos Gemini
- **Stores devem estar ativos**: Apenas stores com `is_active=True` são usados
- **Arquivos devem estar processados**: Aguarde o status `completed` antes de usar

## 🎓 Exemplo Completo

### 1. Criar Store
```bash
curl -X 'POST' \
  'http://localhost:8001/api/file-search/stores' \
  -H 'Authorization: Bearer TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{"display_name": "Documentos da Empresa"}'
```

### 2. Upload de Arquivo
```bash
curl -X 'POST' \
  'http://localhost:8001/api/file-search/stores/1/files' \
  -H 'Authorization: Bearer TOKEN' \
  -F 'file=@documento.pdf' \
  -F 'display_name=Manual da Empresa'
```

### 3. Criar Agente
```bash
curl -X 'POST' \
  'http://localhost:8001/api/agents' \
  -H 'Authorization: Bearer TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "Assistente RAG",
    "description": "Responde baseado nos documentos",
    "instruction": "Use os documentos para responder perguntas.",
    "model": "gemini-2.5-flash",
    "tools": []
  }'
```

### 4. Conversar
```bash
curl -X 'POST' \
  'http://localhost:8001/api/agents/chat' \
  -H 'Authorization: Bearer TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "agent_id": 1,
    "message": "O que diz o manual sobre políticas?",
    "session_id": "sua-session-id"
  }'
```

## 🎉 Pronto!

O agente vai automaticamente usar RAG para buscar informações nos seus documentos e responder baseado neles!

