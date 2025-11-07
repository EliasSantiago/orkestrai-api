# 📊 Implementação de Sessões no PostgreSQL

## Comparação: Redis vs PostgreSQL

### Complexidade de Implementação

| Aspecto | Redis (Atual) | PostgreSQL |
|---------|---------------|------------|
| **Complexidade** | ⭐⭐ Baixa | ⭐⭐⭐ Média |
| **Latência** | ⚡ < 1ms | ⏱️ 5-20ms |
| **Persistência** | ⚠️ Volátil (TTL) | ✅ Permanente |
| **Consultas** | ⚠️ Limitadas | ✅ SQL Completo |
| **Escalabilidade** | ✅ Excelente | ✅ Boa |
| **Manutenção** | ✅ Simples | ⚠️ Requer limpeza |

## Estrutura de Tabelas no PostgreSQL

### 1. Tabela `sessions`

```sql
CREATE TABLE sessions (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) UNIQUE NOT NULL,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    agent_id INTEGER REFERENCES agents(id) ON DELETE SET NULL,
    title VARCHAR(500),  -- Título da conversa (opcional)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,  -- Para limpeza automática
    metadata JSONB,  -- Metadados adicionais
    
    INDEX idx_sessions_user_id (user_id),
    INDEX idx_sessions_session_id (session_id),
    INDEX idx_sessions_expires_at (expires_at)
);
```

### 2. Tabela `messages`

```sql
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL REFERENCES sessions(session_id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL,  -- 'user', 'assistant', 'system'
    content TEXT NOT NULL,
    metadata JSONB,  -- agent_id, model, tokens, etc.
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_messages_session_id (session_id),
    INDEX idx_messages_user_id (user_id),
    INDEX idx_messages_created_at (created_at)
);
```

## Implementação em Python (SQLAlchemy)

### Modelos (`src/models.py`)

```python
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime, timedelta
from src.database import Base

class Session(Base):
    """Session model for conversations."""
    
    __tablename__ = "sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), unique=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id", ondelete="SET NULL"), nullable=True)
    title = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    metadata = Column(JSONB, nullable=True)
    
    # Relationships
    user = relationship("User", backref="sessions")
    agent = relationship("Agent", backref="sessions")
    messages = relationship("Message", back_populates="session", cascade="all, delete-orphan", order_by="Message.created_at")
    
    __table_args__ = (
        Index('idx_sessions_expires_at', 'expires_at'),
    )


class Message(Base):
    """Message model for conversation history."""
    
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), ForeignKey("sessions.session_id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String(50), nullable=False)  # 'user', 'assistant', 'system'
    content = Column(Text, nullable=False)
    metadata = Column(JSONB, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    session = relationship("Session", back_populates="messages")
    user = relationship("User", backref="messages")
```

### Serviço (`src/services/postgresql_conversation_service.py`)

```python
from typing import List, Dict, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from datetime import datetime, timedelta
from src.models import Session as SessionModel, Message as MessageModel
from src.config import Config


class PostgreSQLConversationService:
    """Service for managing conversations in PostgreSQL."""
    
    @staticmethod
    def create_session(
        db: Session,
        session_id: str,
        user_id: int,
        agent_id: Optional[int] = None,
        title: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> SessionModel:
        """Create a new session."""
        expires_at = datetime.utcnow() + timedelta(seconds=Config.CONVERSATION_TTL)
        
        session = SessionModel(
            session_id=session_id,
            user_id=user_id,
            agent_id=agent_id,
            title=title,
            expires_at=expires_at,
            metadata=metadata
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        return session
    
    @staticmethod
    def get_or_create_session(
        db: Session,
        session_id: str,
        user_id: int,
        agent_id: Optional[int] = None
    ) -> SessionModel:
        """Get existing session or create new one."""
        session = db.query(SessionModel).filter(
            SessionModel.session_id == session_id,
            SessionModel.user_id == user_id
        ).first()
        
        if not session:
            session = PostgreSQLConversationService.create_session(
                db, session_id, user_id, agent_id
            )
        else:
            # Update expires_at on access
            session.expires_at = datetime.utcnow() + timedelta(seconds=Config.CONVERSATION_TTL)
            session.updated_at = datetime.utcnow()
            db.commit()
        
        return session
    
    @staticmethod
    def add_message(
        db: Session,
        session_id: str,
        user_id: int,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> MessageModel:
        """Add a message to a session."""
        # Ensure session exists
        session = PostgreSQLConversationService.get_or_create_session(
            db, session_id, user_id
        )
        
        message = MessageModel(
            session_id=session_id,
            user_id=user_id,
            role=role,
            content=content,
            metadata=metadata
        )
        db.add(message)
        
        # Limit history size
        message_count = db.query(MessageModel).filter(
            MessageModel.session_id == session_id
        ).count()
        
        if message_count > Config.MAX_CONVERSATION_HISTORY:
            # Delete oldest messages
            oldest_messages = db.query(MessageModel).filter(
                MessageModel.session_id == session_id
            ).order_by(MessageModel.created_at).limit(
                message_count - Config.MAX_CONVERSATION_HISTORY
            ).all()
            for msg in oldest_messages:
                db.delete(msg)
        
        db.commit()
        db.refresh(message)
        return message
    
    @staticmethod
    def get_conversation_history(
        db: Session,
        session_id: str,
        user_id: int,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get conversation history for a session."""
        query = db.query(MessageModel).filter(
            MessageModel.session_id == session_id,
            MessageModel.user_id == user_id
        ).order_by(MessageModel.created_at)
        
        if limit:
            query = query.limit(limit)
        
        messages = query.all()
        
        return [
            {
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.created_at.isoformat(),
                "metadata": msg.metadata or {}
            }
            for msg in messages
        ]
    
    @staticmethod
    def get_user_sessions(db: Session, user_id: int) -> List[str]:
        """Get all session IDs for a user."""
        sessions = db.query(SessionModel).filter(
            SessionModel.user_id == user_id
        ).order_by(desc(SessionModel.updated_at)).all()
        
        return [s.session_id for s in sessions]
    
    @staticmethod
    def clear_session(db: Session, session_id: str, user_id: int) -> bool:
        """Clear a specific session."""
        session = db.query(SessionModel).filter(
            SessionModel.session_id == session_id,
            SessionModel.user_id == user_id
        ).first()
        
        if session:
            db.delete(session)
            db.commit()
            return True
        return False
    
    @staticmethod
    def cleanup_expired_sessions(db: Session) -> int:
        """Clean up expired sessions (should run as cron job)."""
        deleted = db.query(SessionModel).filter(
            SessionModel.expires_at < datetime.utcnow()
        ).delete()
        db.commit()
        return deleted
```

## Migração de Redis para PostgreSQL

### Passos

1. **Criar tabelas**:
   ```bash
   python -c "from src.database import init_db; from src.models import Session, Message; init_db()"
   ```

2. **Migrar dados existentes** (se houver):
   ```python
   # Script de migração
   from src.redis_client import get_redis_client
   from src.services.postgresql_conversation_service import PostgreSQLConversationService
   from src.database import SessionLocal
   
   redis_client = get_redis_client()
   db = SessionLocal()
   
   # Migrar sessões do Redis para PostgreSQL
   # ... código de migração
   ```

3. **Atualizar serviços**:
   - Substituir `ConversationService` por `PostgreSQLConversationService`
   - Atualizar rotas para usar o novo serviço

## Job de Limpeza Automática

### Script (`scripts/cleanup_sessions.py`)

```python
"""Cleanup expired sessions."""
from src.database import SessionLocal
from src.services.postgresql_conversation_service import PostgreSQLConversationService

def cleanup():
    db = SessionLocal()
    try:
        deleted = PostgreSQLConversationService.cleanup_expired_sessions(db)
        print(f"Deleted {deleted} expired sessions")
    finally:
        db.close()

if __name__ == "__main__":
    cleanup()
```

### Cron Job

```bash
# Adicionar ao crontab (executar a cada hora)
0 * * * * cd /path/to/app && python scripts/cleanup_sessions.py
```

## Performance: PostgreSQL vs Redis

### Benchmarks Esperados

| Operação | Redis | PostgreSQL |
|----------|-------|------------|
| **Adicionar mensagem** | < 1ms | 5-15ms |
| **Buscar histórico** | < 1ms | 10-30ms |
| **Listar sessões** | < 1ms | 20-50ms |
| **Limpar sessão** | < 1ms | 10-20ms |

### Otimizações PostgreSQL

1. **Índices adequados** (já incluídos)
2. **Connection pooling** (SQLAlchemy já faz)
3. **Paginação** para históricos grandes
4. **Particionamento** de tabelas (se necessário)

## Recomendação

### Use PostgreSQL se:
- ✅ Precisa de persistência permanente
- ✅ Quer fazer análises/relatórios
- ✅ Precisa de relacionamentos com outras tabelas
- ✅ Latência de 10-30ms é aceitável

### Use Redis se:
- ✅ Precisa de latência ultra-baixa (< 1ms)
- ✅ Sessões temporárias são OK
- ✅ Não precisa de consultas complexas
- ✅ Quer simplicidade operacional

## Híbrido (Melhor dos Dois Mundos)

Você pode usar **ambos**:
- **Redis**: Cache rápido para sessões ativas
- **PostgreSQL**: Persistência permanente para histórico completo

```python
# Exemplo de estratégia híbrida
def add_message(session_id, user_id, role, content):
    # 1. Salvar no Redis (rápido)
    redis_client.add_message(...)
    
    # 2. Salvar no PostgreSQL (permanente) - async
    async_save_to_postgresql(...)
```

