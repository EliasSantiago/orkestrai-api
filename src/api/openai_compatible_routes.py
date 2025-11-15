"""
OpenAI-compatible API routes for external clients (e.g., LobeChat).

This module provides OpenAI-compatible endpoints that allow external clients
like LobeChat, LibreChat, Open WebUI, etc. to use our LiteLLM-powered backend
as if it were the OpenAI API.

Endpoints:
- GET /v1/models - List available models
- POST /v1/chat/completions - Chat completions (streaming and non-streaming)
"""

import logging
import time
import uuid
import json
from typing import List, Optional, Literal, Union
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from src.core.llm_factory import LLMFactory
from src.core.llm_provider import LLMMessage
from src.api.dependencies import get_current_user_id

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1", tags=["openai-compatible"])


# ============================================================================
# Request/Response Models (OpenAI-compatible)
# ============================================================================

class ChatMessage(BaseModel):
    """Chat message in OpenAI format."""
    role: Literal["system", "user", "assistant", "function"]
    content: str
    name: Optional[str] = None


class ChatCompletionRequest(BaseModel):
    """OpenAI chat completion request."""
    model: str = Field(..., description="Model to use (format: provider/model-name)")
    messages: List[ChatMessage]
    temperature: Optional[float] = Field(default=0.7, ge=0, le=2)
    top_p: Optional[float] = Field(default=1.0, ge=0, le=1)
    n: Optional[int] = Field(default=1, ge=1, le=10)
    stream: Optional[bool] = False
    max_tokens: Optional[int] = Field(default=None, ge=1)
    presence_penalty: Optional[float] = Field(default=0, ge=-2, le=2)
    frequency_penalty: Optional[float] = Field(default=0, ge=-2, le=2)
    user: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "model": "gemini/gemini-2.0-flash-exp",
                    "messages": [
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": "Hello, how are you?"}
                    ],
                    "temperature": 0.7,
                    "stream": True
                },
                {
                    "model": "openai/gpt-4o",
                    "messages": [
                        {"role": "user", "content": "What is the capital of France?"}
                    ],
                    "stream": False
                }
            ]
        }


class ChatCompletionChoice(BaseModel):
    """OpenAI chat completion choice."""
    index: int
    message: ChatMessage
    finish_reason: Optional[str] = None


class ChatCompletionUsage(BaseModel):
    """OpenAI chat completion usage."""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class ChatCompletionResponse(BaseModel):
    """OpenAI chat completion response."""
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[ChatCompletionChoice]
    usage: ChatCompletionUsage


class ChatCompletionChunk(BaseModel):
    """OpenAI chat completion chunk (for streaming)."""
    id: str
    object: str = "chat.completion.chunk"
    created: int
    model: str
    choices: List[dict]


class Model(BaseModel):
    """OpenAI model object."""
    id: str
    object: str = "model"
    created: int
    owned_by: str


class ModelList(BaseModel):
    """OpenAI model list response."""
    object: str = "list"
    data: List[Model]


# ============================================================================
# Helper Functions
# ============================================================================

def convert_to_llm_messages(messages: List[ChatMessage]) -> List[LLMMessage]:
    """Convert OpenAI messages to LLMMessage format."""
    return [
        LLMMessage(role=msg.role, content=msg.content)
        for msg in messages
    ]


# ============================================================================
# Endpoints
# ============================================================================

@router.get("/models", response_model=ModelList)
async def list_models(
    user_id: int = Depends(get_current_user_id)
):
    """
    List available models (OpenAI-compatible).
    
    This endpoint lists all models available through LiteLLM.
    Compatible with OpenAI API format.
    
    Requires JWT authentication (same as other API endpoints).
    """
    
    # Get all supported models from LiteLLM
    all_models = LLMFactory.get_all_supported_models()
    
    # Convert to OpenAI format
    models = []
    created_time = int(time.time())
    
    for provider_name, model_list in all_models.items():
        for model_id in model_list:
            models.append(Model(
                id=model_id,
                created=created_time,
                owned_by=provider_name.lower()
            ))
    
    return ModelList(data=models)


@router.post("/chat/completions")
async def create_chat_completion(
    request: ChatCompletionRequest,
    user_id: int = Depends(get_current_user_id)
):
    """
    Create chat completion (OpenAI-compatible).
    
    Supports both streaming and non-streaming responses.
    Compatible with OpenAI API format.
    
    Requires JWT authentication (same as other API endpoints).
    Use the access token from POST /api/auth/login as Bearer token.
    """
    
    # Get provider for the requested model
    provider = LLMFactory.get_provider(request.model)
    if not provider:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Model '{request.model}' is not supported. Use GET /v1/models to see available models."
        )
    
    # Convert messages to LLMMessage format
    llm_messages = convert_to_llm_messages(request.messages)
    
    # Generate unique ID for this completion
    completion_id = f"chatcmpl-{uuid.uuid4().hex[:24]}"
    created_time = int(time.time())
    
    # Streaming response
    if request.stream:
        async def generate_stream():
            """Generate streaming response in OpenAI format."""
            try:
                # Stream from LiteLLM
                full_content = ""
                async for chunk in provider.chat(
                    messages=llm_messages,
                    model=request.model,
                    temperature=request.temperature,
                    max_tokens=request.max_tokens,
                    top_p=request.top_p,
                    frequency_penalty=request.frequency_penalty,
                    presence_penalty=request.presence_penalty
                ):
                    full_content += chunk
                    
                    # Create OpenAI-compatible chunk
                    response_chunk = {
                        "id": completion_id,
                        "object": "chat.completion.chunk",
                        "created": created_time,
                        "model": request.model,
                        "choices": [
                            {
                                "index": 0,
                                "delta": {
                                    "content": chunk
                                },
                                "finish_reason": None
                            }
                        ]
                    }
                    
                    # Send as SSE (Server-Sent Events) with proper JSON formatting
                    yield f"data: {json.dumps(response_chunk)}\n\n".encode("utf-8")
                
                # Send final chunk with finish_reason
                final_chunk = {
                    "id": completion_id,
                    "object": "chat.completion.chunk",
                    "created": created_time,
                    "model": request.model,
                    "choices": [
                        {
                            "index": 0,
                            "delta": {},
                            "finish_reason": "stop"
                        }
                    ]
                }
                yield f"data: {json.dumps(final_chunk)}\n\n".encode("utf-8")
                yield b"data: [DONE]\n\n"
                
            except Exception as e:
                logger.error(f"Error in streaming completion: {str(e)}")
                error_chunk = {
                    "error": {
                        "message": str(e),
                        "type": "server_error"
                    }
                }
                yield f"data: {json.dumps(error_chunk)}\n\n".encode("utf-8")
        
        return StreamingResponse(
            generate_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            }
        )
    
    # Non-streaming response
    else:
        try:
            # Collect full response
            full_content = ""
            async for chunk in provider.chat(
                messages=llm_messages,
                model=request.model,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                top_p=request.top_p,
                frequency_penalty=request.frequency_penalty,
                presence_penalty=request.presence_penalty
            ):
                full_content += chunk
            
            # Estimate token usage (rough estimate)
            prompt_tokens = sum(len(msg.content.split()) for msg in request.messages)
            completion_tokens = len(full_content.split())
            total_tokens = prompt_tokens + completion_tokens
            
            # Create OpenAI-compatible response
            response = ChatCompletionResponse(
                id=completion_id,
                created=created_time,
                model=request.model,
                choices=[
                    ChatCompletionChoice(
                        index=0,
                        message=ChatMessage(
                            role="assistant",
                            content=full_content
                        ),
                        finish_reason="stop"
                    )
                ],
                usage=ChatCompletionUsage(
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    total_tokens=total_tokens
                )
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error in chat completion: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error generating completion: {str(e)}"
            )

