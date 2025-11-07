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


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


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


# Agent schemas
class AgentCreate(BaseModel):
    name: str
    description: Optional[str] = None
    instruction: str
    model: str = "gemini-2.0-flash-exp"
    tools: Optional[List[str]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Assistente Completo",
                "description": "Agente versátil que pode realizar cálculos e informar a hora",
                "instruction": "Você é um assistente útil e versátil. Você pode:\n1. Realizar cálculos matemáticos usando a ferramenta 'calculator'\n2. Informar a hora atual em qualquer timezone usando a ferramenta 'get_current_time'\n\nSeja amigável, prestativo e use português brasileiro. Sempre explique o que está fazendo.",
                "model": "gemini-2.0-flash",
                "tools": [
                    "calculator",
                    "get_current_time"
                ]
            }
        }


class AgentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    instruction: Optional[str] = None
    model: Optional[str] = None
    tools: Optional[List[str]] = None


class AgentResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    instruction: str
    model: str
    tools: List[str]
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


class MessageCreate(BaseModel):
    content: str
    metadata: Optional[dict] = None


class ConversationHistory(BaseModel):
    session_id: str
    messages: List[Message]


class SessionInfo(BaseModel):
    session_id: str
    message_count: int
    last_activity: Optional[str] = None
    ttl: Optional[int] = None

