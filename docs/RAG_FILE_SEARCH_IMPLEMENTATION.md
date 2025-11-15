# Implementação de RAG com File Search (Gemini API)

## 🎯 Visão Geral

A API Gemini oferece **File Search** (Pesquisa de Arquivos), uma ferramenta que permite implementar **RAG (Retrieval-Augmented Generation)** diretamente nos seus agentes. Isso permite que os agentes acessem informações de documentos indexados para fornecer respostas mais precisas e contextualizadas.

## ✅ É Possível Implementar?

**SIM!** É totalmente possível implementar RAG na sua aplicação. A implementação funciona assim:

1. **File Search é uma ferramenta nativa do Gemini** - Pode ser passada como `tool` para os agentes
2. **Funciona com modelos Gemini** - Não precisa ser apenas Flash 2.5, mas alguns modelos podem ter melhor suporte
3. **Agentes podem usar RAG** - Os agentes podem usar File Search automaticamente quando configurado

## 📋 Modelos Suportados

Segundo a documentação oficial:
- **Recomendado**: `gemini-2.5-flash` (mencionado na documentação)
- **Outros modelos Gemini**: Provavelmente funcionam, mas podem ter limitações
- **Verificar**: A documentação sugere usar modelos mais recentes para melhor suporte

## 🏗️ Arquitetura da Implementação

### 1. Estrutura de Dados

```
src/
  services/
    file_search/
      __init__.py
      store_manager.py      # Gerenciar File Search Stores
      file_manager.py       # Upload e importação de arquivos
      tool_integration.py  # Integração com agentes
  models.py                 # Adicionar modelo FileSearchStore
  api/
    file_search_routes.py  # Endpoints para gerenciar stores e arquivos
```

### 2. Fluxo de Uso

1. **Usuário cria um File Search Store** (via API)
2. **Usuário faz upload de arquivos** para o store
3. **Usuário configura agente** para usar o store
4. **Agente usa File Search automaticamente** quando necessário

## 🔧 Implementação

### Passo 1: Modelo de Dados

Adicionar ao `src/models.py`:

```python
class FileSearchStore(Base):
    """File Search Store model."""
    __tablename__ = "file_search_stores"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)  # Nome do store no Google
    display_name = Column(String(255), nullable=True)  # Nome de exibição
    google_store_name = Column(String(500), nullable=False)  # Nome completo do Google (projects/.../fileSearchStores/...)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User")
    files = relationship("FileSearchFile", back_populates="store", cascade="all, delete-orphan")

class FileSearchFile(Base):
    """File in a File Search Store."""
    __tablename__ = "file_search_files"
    
    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, ForeignKey("file_search_stores.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)  # Nome do arquivo
    display_name = Column(String(255), nullable=True)  # Nome de exibição
    google_file_name = Column(String(500), nullable=False)  # Nome completo do Google
    file_type = Column(String(100), nullable=True)  # MIME type
    size_bytes = Column(BigInteger, nullable=True)
    status = Column(String(50), default="processing")  # processing, completed, failed
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    store = relationship("FileSearchStore", back_populates="files")
```

### Passo 2: Serviço de Gerenciamento

Criar `src/services/file_search/store_manager.py`:

```python
from google import genai
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class FileSearchStoreManager:
    """Gerencia File Search Stores do Google."""
    
    def __init__(self):
        self.client = genai.Client()
    
    def create_store(self, display_name: str) -> Dict[str, Any]:
        """Cria um novo File Search Store."""
        try:
            store = self.client.file_search_stores.create(
                config={'display_name': display_name}
            )
            return {
                'name': store.name,
                'display_name': display_name,
                'status': 'created'
            }
        except Exception as e:
            logger.error(f"Error creating file search store: {e}")
            raise
    
    def get_store(self, store_name: str) -> Dict[str, Any]:
        """Obtém informações de um store."""
        try:
            store = self.client.file_search_stores.get(store_name)
            return {
                'name': store.name,
                'display_name': getattr(store, 'display_name', None)
            }
        except Exception as e:
            logger.error(f"Error getting file search store: {e}")
            raise
    
    def delete_store(self, store_name: str) -> bool:
        """Deleta um store."""
        try:
            self.client.file_search_stores.delete(store_name)
            return True
        except Exception as e:
            logger.error(f"Error deleting file search store: {e}")
            raise
```

### Passo 3: Integração com Agentes

Modificar `src/core/llm_providers/adk_provider.py`:

```python
async def chat(
    self,
    messages: List[LLMMessage],
    model: str,
    tools: Optional[List] = None,
    file_search_stores: Optional[List[str]] = None,  # NOVO
    **kwargs
) -> AsyncIterator[str]:
    """Chat using Google ADK."""
    # ... código existente ...
    
    # Adicionar File Search como ferramenta se stores forem fornecidos
    adk_tools = list(tools or [])
    
    if file_search_stores:
        from google.genai import types
        file_search_tool = types.Tool(
            file_search=types.FileSearch(
                file_search_store_names=file_search_stores
            )
        )
        adk_tools.append(file_search_tool)
    
    agent = Agent(
        model=model,
        name=agent_name,
        description=agent_description,
        instruction=instruction,
        tools=adk_tools  # Inclui File Search se configurado
    )
    
    # ... resto do código ...
```

### Passo 4: API Endpoints

Criar `src/api/file_search_routes.py`:

```python
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from src.database import get_db
from src.models import FileSearchStore, FileSearchFile
from src.services.file_search.store_manager import FileSearchStoreManager
from src.services.file_search.file_manager import FileSearchFileManager

router = APIRouter(prefix="/api/file-search", tags=["file-search"])

@router.post("/stores")
async def create_store(
    display_name: str,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Cria um novo File Search Store."""
    manager = FileSearchStoreManager()
    store_info = manager.create_store(display_name)
    
    # Salvar no banco
    store = FileSearchStore(
        user_id=user_id,
        name=store_info['name'],
        display_name=display_name,
        google_store_name=store_info['name'],
        is_active=True
    )
    db.add(store)
    db.commit()
    
    return {"store_id": store.id, "name": store.name}

@router.post("/stores/{store_id}/files")
async def upload_file(
    store_id: int,
    file: UploadFile = File(...),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Faz upload de arquivo para um store."""
    # Verificar se store pertence ao usuário
    store = db.query(FileSearchStore).filter(
        FileSearchStore.id == store_id,
        FileSearchStore.user_id == user_id
    ).first()
    
    if not store:
        raise HTTPException(404, "Store not found")
    
    # Upload e importação
    file_manager = FileSearchFileManager()
    file_info = await file_manager.upload_and_import(
        file=file,
        store_name=store.google_store_name
    )
    
    # Salvar no banco
    db_file = FileSearchFile(
        store_id=store_id,
        name=file_info['name'],
        display_name=file_info.get('display_name'),
        google_file_name=file_info['name'],
        file_type=file.content_type,
        size_bytes=file_info.get('size_bytes'),
        status='processing'
    )
    db.add(db_file)
    db.commit()
    
    return {"file_id": db_file.id, "status": "uploaded"}
```

### Passo 5: Configurar Agente com File Search

Modificar `src/api/agent_chat_routes.py`:

```python
# No método chat_with_agent, antes de chamar provider.chat:

# Buscar File Search Stores do usuário associados ao agente
file_search_stores = []
if model_name.startswith("gemini-"):
    # Buscar stores do usuário que estão ativos
    stores = db.query(FileSearchStore).filter(
        FileSearchStore.user_id == user_id,
        FileSearchStore.is_active == True
    ).all()
    
    file_search_stores = [store.google_store_name for store in stores]

# Passar para o provider
async for chunk in provider.chat(
    messages=messages,
    model=model_name,
    tools=tools if tools else None,
    file_search_stores=file_search_stores if file_search_stores else None,  # NOVO
    **provider_kwargs
):
    response_chunks.append(chunk)
```

## 📝 Exemplo de Uso

### 1. Criar Store

```bash
curl -X POST 'http://localhost:8001/api/file-search/stores' \
  -H 'Authorization: Bearer TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{"display_name": "Documentos da Empresa"}'
```

### 2. Upload de Arquivo

```bash
curl -X POST 'http://localhost:8001/api/file-search/stores/1/files' \
  -H 'Authorization: Bearer TOKEN' \
  -F 'file=@documento.pdf'
```

### 3. Usar com Agente

O agente automaticamente usará File Search quando necessário se:
- O modelo for Gemini
- O usuário tiver stores ativos
- O agente precisar buscar informações

## ⚠️ Limitações e Considerações

1. **Modelos Suportados**: 
   - Funciona melhor com modelos mais recentes (Flash 2.5+)
   - Testar com outros modelos Gemini

2. **Limites**:
   - Tamanho máximo por arquivo: 100 MB
   - Tamanho total do store: 1 GB (gratuito) a 1 TB (nível 3)
   - Recomendação: manter stores < 20 GB para melhor performance

3. **Custos**:
   - Embeddings na indexação: $0.15 por 1M tokens
   - Armazenamento: grátis
   - Tokens recuperados: cobrados como tokens de contexto normais

4. **Formatos Suportados**:
   - PDF, DOCX, TXT, MD, HTML, e muitos outros
   - Ver lista completa na documentação

## 🚀 Próximos Passos

1. Implementar os modelos de dados
2. Criar serviços de gerenciamento
3. Criar endpoints da API
4. Integrar com ADK provider
5. Testar com diferentes modelos Gemini
6. Adicionar interface de gerenciamento (opcional)

## 📚 Referências

- [Documentação Oficial - File Search](https://ai.google.dev/gemini-api/docs/file-search)
- [API Reference - File Search Stores](https://ai.google.dev/api/gemini-api-reference)
- [Preços e Limites](https://ai.google.dev/pricing)

