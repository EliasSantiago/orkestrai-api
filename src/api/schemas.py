"""Pydantic schemas for API requests and responses."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, model_validator, field_serializer


# User schemas
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    password_confirm: str
    
    @model_validator(mode='after')
    def passwords_match(self):
        """Validate that password and password_confirm match."""
        if self.password != self.password_confirm:
            raise ValueError("Passwords do not match")
        return self
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "João Silva",
                "email": "joao.silva@exemplo.com",
                "password": "SenhaSegura123!",
                "password_confirm": "SenhaSegura123!"
            }
        }


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    is_active: bool
    
    class Config:
        from_attributes = True


# Auth schemas
class Token(BaseModel):
    access_token: str
    token_type: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "joao.silva@exemplo.com",
                "password": "SenhaSegura123!"
            }
        }


class ForgotPasswordRequest(BaseModel):
    email: EmailStr
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "joao.silva@exemplo.com"
            }
        }


class ResetPasswordRequest(BaseModel):
    token: str
    email: EmailStr
    new_password: str
    password_confirm: str
    
    @model_validator(mode='after')
    def passwords_match(self):
        """Validate that new_password and password_confirm match."""
        if self.new_password != self.password_confirm:
            raise ValueError("Passwords do not match")
        return self
    
    class Config:
        json_schema_extra = {
            "example": {
                "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "email": "joao.silva@exemplo.com",
                "new_password": "NovaSenhaSegura123!",
                "password_confirm": "NovaSenhaSegura123!"
            }
        }


# Agent schemas
class AgentCreate(BaseModel):
    name: str
    description: Optional[str] = None
    instruction: str
    model: str = "gemini/gemini-2.0-flash-exp"
    tools: Optional[List[str]] = None
    use_file_search: Optional[bool] = False  # Enable RAG (File Search) for this agent
    
    @model_validator(mode='after')
    def validate_file_search_model(self):
        """Validate that file search only works with gemini-2.5-flash."""
        if self.use_file_search and self.model != "gemini/gemini-2.5-flash":
            raise ValueError(
                f"File Search (RAG) is only supported with model 'gemini/gemini-2.5-flash'. "
                f"Current model: '{self.model}'. "
                f"Please use 'gemini/gemini-2.5-flash' when enabling File Search."
            )
        return self
    
    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "name": "Analista de Notícias IA - Tavily MCP",
                    "description": "Agente especializado em buscar e analisar notícias sobre IA usando Tavily MCP",
                    "instruction": "Você é um analista de notícias especializado em Inteligência Artificial.\n\nFERRAMENTAS:\n1. get_current_time: Obter data/hora atual\n2. tavily_tavily-search: Buscar informações na web\n3. tavily_tavily-extract: Extrair dados de páginas\n\nPROCESSO:\n1. Use get_current_time PRIMEIRO\n2. Use tavily_tavily-search para buscar notícias\n3. Analise e forneça resumo estruturado\n4. SEMPRE cite as fontes (URLs)\n5. Responda em português brasileiro",
                    "model": "gemini/gemini-2.0-flash-exp",
                    "tools": [
                        "get_current_time",
                        "tavily_tavily-search",
                        "tavily_tavily-extract"
                    ],
                    "use_file_search": False
                },
                {
                    "name": "Assistente Simples - OpenAI",
                    "description": "Assistente conversacional básico usando GPT-4",
                    "instruction": "Você é um assistente útil e amigável. Responda de forma clara e objetiva em português brasileiro.",
                    "model": "openai/gpt-4o",
                    "tools": [],
                    "use_file_search": False
                },
                {
                    "name": "Assistente com RAG - Gemini",
                    "description": "Assistente com busca em arquivos (File Search/RAG)",
                    "instruction": "Você é um assistente que pode buscar informações em documentos. Use o File Search para encontrar informações relevantes nos documentos do usuário.",
                    "model": "gemini/gemini-2.5-flash",
                    "tools": [],
                    "use_file_search": True
                },
                {
                    "name": "Pesquisador Web Simples",
                    "description": "Agente focado em busca web",
                    "instruction": "Use get_current_time para contexto temporal e tavily_tavily-search para buscar informações atualizadas. Sempre cite as fontes.",
                    "model": "gemini/gemini-2.0-flash-exp",
                    "tools": [
                        "get_current_time",
                        "tavily_tavily-search"
                    ],
                    "use_file_search": False
                },
                {
                    "name": "Extrator de Dados Web",
                    "description": "Especializado em extrair dados de páginas web",
                    "instruction": "Use tavily_tavily-extract para extrair dados estruturados de URLs fornecidas. Organize os dados de forma clara.",
                    "model": "openai/gpt-4o-mini",
                    "tools": [
                        "tavily_tavily-extract"
                    ],
                    "use_file_search": False
                }
            ]
        }


class AgentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    instruction: Optional[str] = None
    model: Optional[str] = None
    tools: Optional[List[str]] = None
    use_file_search: Optional[bool] = None  # Enable/disable RAG (File Search) for this agent
    
    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "name": "Analista de Notícias IA - Atualizado",
                    "description": "Agente atualizado com novas ferramentas",
                    "tools": [
                        "get_current_time",
                        "tavily_tavily-search",
                        "tavily_tavily-extract",
                        "tavily_tavily-map"
                    ]
                },
                {
                    "model": "openai/gpt-4o",
                    "instruction": "Nova instrução atualizada para o assistente."
                },
                {
                    "tools": [
                        "tavily_tavily-search"
                    ],
                    "use_file_search": False
                },
                {
                    "use_file_search": True,
                    "model": "gemini/gemini-2.5-flash"
                }
            ]
        }


class AgentResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    instruction: str
    model: str
    tools: List[str]
    use_file_search: bool  # Whether agent uses File Search (RAG)
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    @field_serializer('created_at', 'updated_at')
    def serialize_datetime(self, dt: datetime) -> str:
        """Serialize datetime to ISO format string."""
        if isinstance(dt, datetime):
            return dt.isoformat()
        return str(dt)
    
    class Config:
        from_attributes = True


# Conversation schemas
class Message(BaseModel):
    role: str
    content: str
    timestamp: Optional[str] = None
    metadata: Optional[dict] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "role": "user",
                "content": "Olá, como você está?",
                "timestamp": "2025-11-12T14:30:00",
                "metadata": {"ip": "127.0.0.1"}
            }
        }


class MessageCreate(BaseModel):
    content: str
    metadata: Optional[dict] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "content": "Olá, preciso de ajuda com Python",
                "metadata": {"source": "web"}
            }
        }


class ConversationHistory(BaseModel):
    session_id: str
    messages: List[Message]


class SessionInfo(BaseModel):
    session_id: str
    message_count: int
    last_activity: Optional[str] = None
    ttl: Optional[int] = None

