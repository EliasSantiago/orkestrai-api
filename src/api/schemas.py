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
    avatar_url: Optional[str] = None
    preferences: Optional[dict] = None
    
    class Config:
        from_attributes = True


# User Preferences schemas
class UserPreferences(BaseModel):
    """User preferences (theme, language, layout, etc)."""
    theme: Optional[str] = "auto"  # "light", "dark", "auto"
    language: Optional[str] = "en"  # "en", "pt-BR", "es", etc
    layout: Optional[str] = "default"  # "default", "compact", "comfortable"
    notifications: Optional[bool] = True
    sidebar_expanded: Optional[bool] = True
    message_sound: Optional[bool] = False
    font_size: Optional[str] = "medium"  # "small", "medium", "large"
    
    # Allow extra fields for future preferences
    class Config:
        extra = "allow"
        json_schema_extra = {
            "example": {
                "theme": "dark",
                "language": "pt-BR",
                "layout": "compact",
                "notifications": True,
                "sidebar_expanded": False,
                "message_sound": True,
                "font_size": "medium"
            }
        }


class UserPreferencesUpdate(BaseModel):
    """Update user preferences (partial update allowed)."""
    theme: Optional[str] = None
    language: Optional[str] = None
    layout: Optional[str] = None
    notifications: Optional[bool] = None
    sidebar_expanded: Optional[bool] = None
    message_sound: Optional[bool] = None
    font_size: Optional[str] = None
    
    # Allow extra fields for future preferences
    class Config:
        extra = "allow"
        json_schema_extra = {
            "example": {
                "theme": "dark",
                "language": "pt-BR"
            }
        }


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
    agent_type: str = "llm"  # llm, sequential, loop, parallel, custom
    
    # LLM Agent fields
    instruction: Optional[str] = None
    model: Optional[str] = "gemini/gemini-2.0-flash-exp"
    tools: Optional[List[str]] = None
    use_file_search: Optional[bool] = False  # Enable RAG (File Search) for this agent
    
    # Workflow Agent configuration
    workflow_config: Optional[dict] = None
    
    # Custom Agent configuration
    custom_config: Optional[dict] = None
    
    # Common fields
    is_favorite: Optional[bool] = False  # Mark as favorite for quick access
    is_public: Optional[bool] = False  # If True, agent is visible to all users
    icon: Optional[str] = None  # Icon name from lucide-react library
    
    @model_validator(mode='after')
    def validate_agent(self):
        """Validate agent configuration based on type."""
        # Validate agent_type
        valid_types = ["llm", "sequential", "loop", "parallel", "custom"]
        if self.agent_type not in valid_types:
            raise ValueError(f"Invalid agent_type. Must be one of: {', '.join(valid_types)}")
        
        # LLM agent validation
        if self.agent_type == "llm":
            if not self.instruction:
                raise ValueError("LLM agents require 'instruction' field")
            if not self.model:
                raise ValueError("LLM agents require 'model' field")
            
            # Validate file search with Gemini models that support RAG
            if self.use_file_search:
                # Extract model name without provider prefix (e.g., 'gemini/gemini-3-pro-preview' -> 'gemini-3-pro-preview')
                model_name = self.model.split('/')[-1] if '/' in self.model else self.model
                
                # Models that support RAG: Gemini 2.5 Flash, Gemini 3 Pro, Gemini 3 Pro Preview, and other Gemini models
                gemini_rag_models = [
                    'gemini-2.5-flash',
                    'gemini-3-pro',
                    'gemini-3-pro-preview',
                    'gemini-2.5-pro',  # Also supports RAG
                ]
                
                # Check if it's a Gemini model and supports RAG
                is_gemini_model = self.model.startswith('gemini/') or model_name.startswith('gemini-')
                supports_rag = any(model_name.endswith(rag_model) or model_name == rag_model for rag_model in gemini_rag_models)
                
                if not (is_gemini_model and supports_rag):
                    raise ValueError(
                        f"File Search (RAG) is only supported with Gemini models that support RAG. "
                        f"Current model: '{self.model}'. "
                        f"Please use a Gemini model that supports RAG (e.g., gemini-2.5-flash, gemini-3-pro-preview, gemini-3-pro)."
                    )
        
        # Sequential workflow validation
        elif self.agent_type == "sequential":
            if not self.workflow_config or "agents" not in self.workflow_config:
                raise ValueError("Sequential agents require 'workflow_config' with 'agents' list")
            if not isinstance(self.workflow_config["agents"], list):
                raise ValueError("workflow_config.agents must be a list")
            if len(self.workflow_config["agents"]) < 2:
                raise ValueError("Sequential agents require at least 2 agents in the workflow")
        
        # Loop workflow validation
        elif self.agent_type == "loop":
            if not self.workflow_config or "agent" not in self.workflow_config:
                raise ValueError("Loop agents require 'workflow_config' with 'agent' field")
        
        # Parallel workflow validation
        elif self.agent_type == "parallel":
            if not self.workflow_config or "agents" not in self.workflow_config:
                raise ValueError("Parallel agents require 'workflow_config' with 'agents' list")
            if not isinstance(self.workflow_config["agents"], list):
                raise ValueError("workflow_config.agents must be a list")
            if len(self.workflow_config["agents"]) < 2:
                raise ValueError("Parallel agents require at least 2 agents")
        
        # Custom agent validation
        elif self.agent_type == "custom":
            if not self.custom_config:
                raise ValueError("Custom agents require 'custom_config'")
        
        return self
    
    class Config:
        json_schema_extra = {
            "examples": [
                # LLM Agent Examples
                {
                    "name": "Analista de Notícias IA - Tavily MCP",
                    "description": "Agente LLM especializado em buscar e analisar notícias sobre IA usando Tavily MCP",
                    "agent_type": "llm",
                    "instruction": "Você é um analista de notícias especializado em Inteligência Artificial.\n\nFERRAMENTAS:\n1. get_current_time: Obter data/hora atual\n2. tavily_tavily-search: Buscar informações na web\n3. tavily_tavily-extract: Extrair dados de páginas\n\nPROCESSO:\n1. Use get_current_time PRIMEIRO\n2. Use tavily_tavily-search para buscar notícias\n3. Analise e forneça resumo estruturado\n4. SEMPRE cite as fontes (URLs)\n5. Responda em português brasileiro",
                    "model": "gemini/gemini-2.0-flash-exp",
                    "tools": [
                        "get_current_time",
                        "tavily_tavily-search",
                        "tavily_tavily-extract"
                    ],
                    "use_file_search": False,
                    "is_favorite": False
                },
                {
                    "name": "Assistente com RAG - Gemini",
                    "description": "Agente LLM com busca em arquivos (File Search/RAG)",
                    "agent_type": "llm",
                    "instruction": "Você é um assistente que pode buscar informações em documentos. Use o File Search para encontrar informações relevantes nos documentos do usuário. Responda de forma clara e cite trechos relevantes dos documentos.",
                    "model": "gemini/gemini-2.5-flash",
                    "tools": [],
                    "use_file_search": True,
                    "is_favorite": False
                },
                # Sequential Workflow Agent Example
                {
                    "name": "Pipeline de Pesquisa e Análise",
                    "description": "Workflow sequencial: Pesquisa → Análise → Resumo",
                    "agent_type": "sequential",
                    "workflow_config": {
                        "agents": [
                            "pesquisador_web",
                            "analisador_dados",
                            "gerador_resumo"
                        ],
                        "description": "Executa agentes em sequência: primeiro pesquisa dados, depois analisa e por fim gera um resumo"
                    },
                    "is_favorite": False
                },
                # Loop Workflow Agent Example
                {
                    "name": "Revisor Iterativo",
                    "description": "Loop: Revisa texto até atingir qualidade desejada",
                    "agent_type": "loop",
                    "workflow_config": {
                        "agent": "editor_texto",
                        "condition": "quality_score >= 0.9",
                        "max_iterations": 5,
                        "description": "Executa o agente editor_texto em loop até a qualidade atingir 0.9 ou completar 5 iterações"
                    },
                    "is_favorite": False
                },
                # Parallel Workflow Agent Example
                {
                    "name": "Análise Paralela Multi-Fonte",
                    "description": "Parallel: Analisa múltiplas fontes simultaneamente",
                    "agent_type": "parallel",
                    "workflow_config": {
                        "agents": [
                            "analisador_noticias",
                            "analisador_redes_sociais",
                            "analisador_academico"
                        ],
                        "description": "Executa múltiplos agentes em paralelo e retorna os resultados de todos"
                    },
                    "is_favorite": False
                },
                # Custom Agent Example
                {
                    "name": "Processador de Dados Customizado",
                    "description": "Agente custom com lógica personalizada em Python",
                    "agent_type": "custom",
                    "custom_config": {
                        "runtime": "python",
                        "entry_point": "process",
                        "code": "def process(context):\n    # Lógica customizada aqui\n    data = context.get('input')\n    result = transform_data(data)\n    return {'output': result}",
                        "description": "Agente customizado que processa dados com lógica específica do usuário"
                    },
                    "is_favorite": False
                }
            ]
        }


class AgentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    agent_type: Optional[str] = None  # Cannot change after creation typically, but included for completeness
    
    # LLM Agent fields
    instruction: Optional[str] = None
    model: Optional[str] = None
    tools: Optional[List[str]] = None
    use_file_search: Optional[bool] = None  # Enable/disable RAG (File Search) for this agent
    
    # Workflow Agent configuration
    workflow_config: Optional[dict] = None
    
    # Custom Agent configuration
    custom_config: Optional[dict] = None
    
    # Common fields
    is_favorite: Optional[bool] = None  # Mark/unmark as favorite
    is_public: Optional[bool] = None  # Make agent public/private
    icon: Optional[str] = None  # Icon name from lucide-react library
    
    class Config:
        json_schema_extra = {
            "examples": [
                # Update LLM agent
                {
                    "name": "Analista de Notícias IA - Atualizado",
                    "description": "Agente atualizado com novas ferramentas",
                    "tools": [
                        "get_current_time",
                        "tavily_tavily-search",
                        "tavily_tavily-extract"
                    ]
                },
                # Update model and instruction
                {
                    "model": "openai/gpt-4o",
                    "instruction": "Nova instrução atualizada para o assistente."
                },
                # Enable RAG
                {
                    "use_file_search": True,
                    "model": "gemini/gemini-2.5-flash"
                },
                # Mark as favorite
                {
                    "is_favorite": True
                },
                # Update workflow config
                {
                    "workflow_config": {
                        "agents": [
                            "agent1",
                            "agent2",
                            "agent3",
                            "agent4"
                        ]
                    }
                }
            ]
        }


class AgentResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    agent_type: str  # llm, sequential, loop, parallel, custom
    
    # LLM Agent fields
    instruction: Optional[str]
    model: Optional[str]
    tools: Optional[List[str]]
    use_file_search: bool  # Whether agent uses File Search (RAG)
    
    # Workflow Agent configuration
    workflow_config: Optional[dict]
    
    # Custom Agent configuration
    custom_config: Optional[dict]
    
    # Common fields
    is_favorite: bool  # Favorite flag for quick access
    is_public: bool  # If True, agent is visible to all users
    icon: Optional[str]  # Icon name from lucide-react library
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
    id: Optional[str] = None  # Message ID (UUID or database ID)
    role: str
    content: str
    timestamp: Optional[str] = None  # ISO 8601 format
    createdAt: Optional[int] = None  # Unix timestamp in milliseconds
    updatedAt: Optional[int] = None  # Unix timestamp in milliseconds
    metadata: Optional[dict] = None
    model: Optional[str] = None  # Model used for assistant messages
    provider: Optional[str] = None  # Provider used (openai, gemini, etc.)
    parentId: Optional[str] = None  # Parent message ID for threading
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "msg-uuid-1",
                "role": "user",
                "content": "Olá, como você está?",
                "timestamp": "2025-11-12T14:30:00Z",
                "createdAt": 1705327800000,
                "updatedAt": 1705327800000,
                "metadata": {"ip": "127.0.0.1"},
                "parentId": None
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
    agent_id: Optional[int] = None

