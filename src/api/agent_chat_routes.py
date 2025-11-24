"""Agent execution API routes for chat/interaction."""

import logging
import base64
from typing import Optional, AsyncGenerator, List
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form, Request
from fastapi.responses import StreamingResponse
from fastapi import Request as FastAPIRequest
from src.adk_conversation_middleware import get_adk_middleware
from src.api.dependencies import get_current_user_id
from src.api.di import get_chat_with_agent_use_case, get_get_agent_use_case, get_get_user_agents_use_case
from src.application.use_cases.agents import ChatWithAgentUseCase, GetAgentUseCase, GetUserAgentsUseCase
from src.domain.exceptions import AgentNotFoundError, UnsupportedModelError, InvalidModelError
from src.infrastructure.database.entity_mapper import agent_entity_to_model
from src.services.default_agent_loader import load_default_agent
from src.core.llm_provider import FilePart
from src.services.file_converters import FileConverterService
from pydantic import BaseModel
import json

logger = logging.getLogger(__name__)

# Initialize file converter service
file_converter_service = FileConverterService()


def generate_session_id() -> str:
    """
    Generate a session ID using UUID format.
    
    Format: UUID v4 (standard format)
    Example: cc9e7f12-0413-49bc-91dd-7a5f6f2500da
    
    Returns:
        Session ID string in UUID format (without prefix)
    """
    import uuid
    return str(uuid.uuid4())

router = APIRouter(prefix="/api/agents", tags=["agents"])


def sanitize_agent_name(name: str, agent_id: int) -> str:
    """
    Sanitize agent name to be a valid Python identifier for ADK.
    
    ADK requires agent names to be valid identifiers:
    - Start with letter or underscore
    - Only contain letters, digits, and underscores
    """
    import unicodedata
    
    # Remove accents and special characters
    sanitized = unicodedata.normalize('NFD', name)
    sanitized = ''.join(c for c in sanitized if unicodedata.category(c) != 'Mn')
    
    # Convert to lowercase and replace spaces/hyphens with underscores
    sanitized = sanitized.lower().replace(" ", "_").replace("-", "_")
    
    # Keep only alphanumeric and underscores
    sanitized = "".join(c for c in sanitized if c.isalnum() or c == "_")
    
    # Ensure it starts with letter or underscore
    if not sanitized or not (sanitized[0].isalpha() or sanitized[0] == "_"):
        sanitized = f"agent_{sanitized}" if sanitized else f"agent_{agent_id}"
    
    return sanitized


class ChatRequest(BaseModel):
    """Request model for agent chat."""
    message: str
    agent_id: Optional[int] = None  # Optional: uses first agent if not provided
    session_id: Optional[str] = None  # Optional: auto-generated if not provided
    model: Optional[str] = None  # Optional: override agent's model (e.g., "openai/gpt-4o-mini", "gemini/gemini-2.0-flash-exp")
    files: Optional[List[dict]] = None  # Optional: list of file metadata (for JSON requests)
    
    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "message": "Faça um resumo das principais notícias sobre IA desta semana",
                    "agent_id": 1,
                    "session_id": "",
                    "model": None
                },
                {
                    "message": "Qual a previsão do tempo para São Paulo hoje?",
                    "agent_id": 2,
                    "session_id": "cc9e7f12-0413-49bc-91dd-7a5f6f2500da"
                },
                {
                    "message": "Extraia os dados principais desta página: https://exemplo.com",
                    "agent_id": 3,
                    "session_id": "",
                    "model": "openai/gpt-4o"
                },
                {
                    "message": "Olá, como você pode me ajudar?",
                    "agent_id": 1
                }
            ]
        }


async def process_uploaded_files(files: List[UploadFile]) -> List[FilePart]:
    """
    Process uploaded files and convert them to FilePart objects.
    Files are converted to text when possible (PDF, DOCX, XLSX, CSV, images via OCR, videos via transcription).
    
    Args:
        files: List of uploaded files
        
    Returns:
        List of FilePart objects with converted text or original data
    """
    processed_files = []
    
    logger.info(f"📎 Processing {len(files)} uploaded files...")
    
    for file in files:
        if not file.filename:
            logger.warning(f"⚠️ Skipping file without filename")
            continue
            
        # Read file content
        content = await file.read()
        logger.info(f"📄 File: {file.filename}, Size: {len(content)} bytes, Type: {file.content_type}")
        
        # Determine file type and MIME type
        mime_type = file.content_type or "application/octet-stream"
        
        # Try to convert file to text
        conversion_result = await file_converter_service.convert_to_text(
            file_content=content,
            file_name=file.filename,
            mime_type=mime_type
        )
        
        if conversion_result.success:
            # File was successfully converted to text
            logger.info(f"✅ Converted {file.filename} to text ({len(conversion_result.text)} chars)")
            
            # Create FilePart with converted text
            # Encode text as base64 for consistency
            text_data = conversion_result.text
            base64_text = base64.b64encode(text_data.encode('utf-8')).decode('utf-8')
            
            file_part = FilePart(
                type="text",  # Mark as text since it's been converted
                data=base64_text,
                mime_type="text/plain",  # Converted to plain text
                file_name=file.filename
            )
            
            # Add metadata about conversion
            if conversion_result.metadata:
                logger.info(f"  📊 Conversion metadata: {conversion_result.metadata}")
            
            processed_files.append(file_part)
        else:
            # Conversion failed - check if it's an image that can be sent directly
            if mime_type.startswith("image/"):
                logger.info(f"⚠️ OCR failed for {file.filename}, sending as image: {conversion_result.error}")
                # Send image directly (models can process images)
                base64_data = base64.b64encode(content).decode('utf-8')
                file_part = FilePart(
                    type="image",
                    data=base64_data,
                    mime_type=mime_type,
                    file_name=file.filename
                )
                processed_files.append(file_part)
            else:
                # For other file types, include error message in text
                logger.warning(f"⚠️ Could not convert {file.filename}: {conversion_result.error}")
                error_text = f"[File: {file.filename}]\n[Error: {conversion_result.error}]\n[Note: This file could not be converted to text. Please provide a text version or ensure the file format is supported.]"
                base64_text = base64.b64encode(error_text.encode('utf-8')).decode('utf-8')
                
                file_part = FilePart(
                    type="text",
                    data=base64_text,
                    mime_type="text/plain",
                    file_name=file.filename
                )
                processed_files.append(file_part)
    
    logger.info(f"📎 Total processed files: {len(processed_files)}")
    return processed_files


class ChatResponse(BaseModel):
    """Response model for agent chat."""
    response: str
    agent_id: int
    agent_name: str
    session_id: Optional[str] = None
    model_used: Optional[str] = None  # Which model was used for this response


@router.post("/chat", response_model=ChatResponse)
async def chat_with_agent(
    request: ChatRequest,
    user_id: int = Depends(get_current_user_id),
    chat_use_case: ChatWithAgentUseCase = Depends(get_chat_with_agent_use_case),
    get_agent_use_case: GetAgentUseCase = Depends(get_get_agent_use_case),
    get_user_agents_use_case: GetUserAgentsUseCase = Depends(get_get_user_agents_use_case)
):
    """
    Chat with an agent.
    
    This endpoint allows you to send messages to a specific agent and get responses.
    It automatically handles conversation context if session_id is provided.
    If session_id is not provided, a new one is generated automatically.
    If agent_id is not provided, uses the default chat agent from file.
    
    **Required Fields:**
    - `message`: The message to send to the agent
    
    **Optional Fields:**
    - `agent_id`: The ID of the agent to chat with (uses default agent from file if not provided)
    - `session_id`: Session ID for conversation continuity (auto-generated if not provided)
    - `model`: Override the agent's default model (e.g., "gpt-4o-mini", "gemini/gemini-2.5-flash", "claude-3-5-sonnet-latest")
    
    **Example Request Body:**
    ```json
    {
      "message": "Olá, como você pode me ajudar?",
      "agent_id": 1,
      "session_id": "cc9e7f12-0413-49bc-91dd-7a5f6f2500da",
      "model": "gpt-4o-mini"
    }
    ```
    
    **Model Override:**
    If you specify a `model` in the request, it will override the agent's default model for this conversation.
    This is useful when:
    - The default model is overloaded (503 error)
    - You want to test different models with the same agent
    - You need a faster/cheaper model for simple queries
    """
    # Determine agent - use default agent from file if not provided
    agent_id = request.agent_id
    default_agent_entity = None
    
    if agent_id is None:
        # Always try to load default agent from file first
        default_agent_entity = load_default_agent()
        if not default_agent_entity:
            # If default agent fails to load, this is a critical error
            # Log detailed error information
            import traceback
            error_details = traceback.format_exc()
            logger.error("Failed to load default agent from file")
            logger.error(f"Error details: {error_details}")
            
            # Try user's first agent as fallback only if available
            try:
                agents = get_user_agents_use_case.execute(user_id)
                if agents:
                    agent_id = agents[0].id
                    logger.warning(f"Using user's first agent (ID: {agent_id}) as fallback - default agent unavailable")
                else:
                    # No default agent and no user agents - this is an error
                    logger.error("No default agent found and user has no agents")
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=[{"msg": "Default agent not available. Please check server logs for details."}],
                        headers={"X-Error-Type": "default_agent_unavailable"}
                    )
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Error getting user agents: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=[{"msg": "Default agent not available and failed to load user agents. Please check server logs."}],
                    headers={"X-Error-Type": "agent_load_failed"}
                )
    
    # Generate session_id if not provided
    session_id = request.session_id or generate_session_id()
    
    # Associate session with user if not already associated
    middleware = get_adk_middleware()
    if not middleware.get_user_id_from_session(session_id):
        middleware.set_user_id_for_session(session_id, user_id)
    
    try:
        # Get agent info for response
        if default_agent_entity:
            # Using default agent from file
            agent_entity = default_agent_entity
            agent_name = agent_entity.name
            agent_id_for_response = 0  # Use 0 to indicate default agent
        else:
            # Using agent from database
            agent_entity = get_agent_use_case.execute(agent_id, user_id)
            agent_model = agent_entity_to_model(agent_entity)
            agent_name = agent_model.name
            agent_id_for_response = agent_model.id
        
        # Determine model name
        model_name = request.model or agent_entity.model or "gemini-2.5-flash"
        
        # Log which model will be used for this chat request
        logger.info(f"🤖 Chat Request - User ID: {user_id}, Agent: {agent_name} (ID: {agent_id_for_response}), Model: {model_name}, Session: {session_id}")
        print(f"\n{'='*80}")
        print(f"💬 CHAT REQUEST")
        print(f"{'='*80}")
        print(f"👤 User ID: {user_id}")
        print(f"🤖 Agent: {agent_name} (ID: {agent_id_for_response})")
        print(f"🧠 LLM Model: {model_name}")
        print(f"💬 Message: {request.message[:100]}{'...' if len(request.message) > 100 else ''}")
        print(f"🆔 Session ID: {session_id}")
        print(f"{'='*80}\n")
        
        # Execute chat use case with default agent entity if using default agent
        if default_agent_entity:
            # Pass the agent entity directly to chat use case
            response = await chat_use_case.execute_with_agent(
                user_id=user_id,
                agent=default_agent_entity,
                message=request.message,
                session_id=session_id,
                model_override=request.model
            )
        else:
            # Execute chat use case (handles all the complex logic)
            response = await chat_use_case.execute(
                user_id=user_id,
                agent_id=agent_id,
                message=request.message,
                session_id=session_id,
                model_override=request.model
            )
        
        # Get actual model used (may differ from requested if fallback was used)
        actual_model_used = getattr(chat_use_case, '_last_model_used', None) or model_name
        
        # Log successful response
        response_length = len(response) if response else 0
        if actual_model_used != model_name:
            logger.info(f"✅ Chat Response - Model usado: {actual_model_used} (solicitado: {model_name}), Response length: {response_length} chars")
            print(f"✅ Resposta enviada ao usuário - Modelo usado: {actual_model_used} (solicitado: {model_name}), Tamanho: {response_length} caracteres\n")
        else:
            logger.info(f"✅ Chat Response - Model: {model_name}, Response length: {response_length} chars")
            print(f"✅ Resposta enviada ao usuário - Modelo: {model_name}, Tamanho: {response_length} caracteres\n")
        
        return ChatResponse(
            response=response,
            agent_id=agent_id_for_response,
            agent_name=agent_name,
            session_id=session_id,
            model_used=actual_model_used
        )
        
    except (AgentNotFoundError, InvalidModelError, UnsupportedModelError):
        raise
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error executing agent: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=[{"msg": f"Error executing agent: {str(e)}"}]
        )


@router.post("/chat/stream")
async def chat_with_agent_stream(
    request: ChatRequest,
    user_id: int = Depends(get_current_user_id),
    chat_use_case: ChatWithAgentUseCase = Depends(get_chat_with_agent_use_case),
    get_agent_use_case: GetAgentUseCase = Depends(get_get_agent_use_case),
    get_user_agents_use_case: GetUserAgentsUseCase = Depends(get_get_user_agents_use_case)
):
    """
    Chat with an agent using streaming responses (JSON format).
    
    This endpoint streams the response in real-time as it's generated.
    For file uploads, use /chat/stream/multipart endpoint.
    """
    async def generate() -> AsyncGenerator[str, None]:
        """Generate response chunks."""
        try:
            # Determine agent - use default agent from file if not provided
            agent_id = request.agent_id
            default_agent_entity = None
            
            if agent_id is None:
                # Try to load default agent from file
                try:
                    default_agent_entity = load_default_agent()
                    agent_id = default_agent_entity.id or 0
                    agent_name = default_agent_entity.name
                    agent_id_for_response = None
                except Exception as e:
                    logger.warning(f"Could not load default agent from file: {e}")
                    agents = get_user_agents_use_case.execute(user_id)
                    if not agents:
                        raise HTTPException(
                            status_code=status.HTTP_404_NOT_FOUND,
                            detail="No agents found. Please create an agent first or ensure default agent file is available."
                        )
                    agent_id = agents[0].id
                    agent_name = agents[0].name
                    agent_id_for_response = agent_id
            else:
                agent = get_agent_use_case.execute(agent_id, user_id)
                if not agent:
                    raise AgentNotFoundError(agent_id)
                agent_name = agent.name
                agent_id_for_response = agent_id
            
            session_id = request.session_id or generate_session_id()
            
            if default_agent_entity:
                model_name = request.model or default_agent_entity.model
            else:
                from src.models import Agent
                agent_model = get_agent_use_case.execute(agent_id, user_id)
                model_name = request.model or agent_model.model
            
            # Process uploaded files
            file_parts = None
            if request.files:
                logger.info(f"📎 JSON request with {len(request.files)} file metadata objects")
                file_parts = [FilePart(**f) for f in request.files]
                logger.info(f"✅ Converted {len(file_parts)} file metadata to FilePart objects")
            
            logger.info(f"🚀 Chat Stream Request - User: {user_id}, Agent: {agent_id} ({agent_name}), Model: {model_name}, Files: {len(file_parts) if file_parts else 0}")
            
            if default_agent_entity:
                async for chunk in chat_use_case.execute_with_agent_stream(
                    user_id=user_id,
                    agent=default_agent_entity,
                    message=request.message,
                    session_id=session_id,
                    model_override=request.model,
                    files=file_parts
                ):
                    yield chunk
            else:
                async for chunk in chat_use_case.execute_stream(
                    user_id=user_id,
                    agent_id=agent_id,
                    message=request.message,
                    session_id=session_id,
                    model_override=request.model,
                    files=file_parts
                ):
                    yield chunk
                
        except (AgentNotFoundError, InvalidModelError, UnsupportedModelError) as e:
            error_msg = f"Error: {str(e)}"
            logger.error(error_msg)
            yield error_msg
        except HTTPException as e:
            error_msg = f"Error: {e.detail}"
            logger.error(error_msg)
            yield error_msg
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            logger.error(f"Error executing agent stream: {e}", exc_info=True)
            yield error_msg
    
    return StreamingResponse(generate(), media_type="text/plain")


@router.post("/chat/stream/multipart")
async def chat_with_agent_stream_multipart(
    message: str = Form(...),
    agent_id: Optional[int] = Form(None),
    session_id: Optional[str] = Form(None),
    model: Optional[str] = Form(None),
    files: Optional[List[UploadFile]] = File(None),
    user_id: int = Depends(get_current_user_id),
    chat_use_case: ChatWithAgentUseCase = Depends(get_chat_with_agent_use_case),
    get_agent_use_case: GetAgentUseCase = Depends(get_get_agent_use_case),
    get_user_agents_use_case: GetUserAgentsUseCase = Depends(get_get_user_agents_use_case)
):
    """
    Chat with an agent using streaming responses (multipart/form-data for file uploads).
    
    **Multipart Request (with files):**
    - `message`: Text message (required)
    - `agent_id`: Agent ID (optional)
    - `session_id`: Session ID (optional)
    - `model`: Model override (optional)
    - `files`: Up to 5 files (optional) - images, PDFs, text files
    
    **File Support:**
    - Images: PNG, JPEG, GIF, WebP
    - Documents: PDF, TXT, DOCX
    - Maximum 5 files per request
    """
    # Log entrada da requisição
    print(f"\n{'='*80}")
    print(f"🚀 MULTIPART REQUEST RECEIVED")
    print(f"{'='*80}")
    print(f"User ID: {user_id}")
    print(f"Message: {message[:100]}...")
    print(f"Model: {model}")
    print(f"Agent ID: {agent_id}")
    print(f"Files: {len(files) if files else 0}")
    logger.info(f"🚀 MULTIPART REQUEST - User: {user_id}, Message: {message[:50]}..., Files: {len(files) if files else 0}")
    
    # Process uploaded files
    file_parts = None
    if files:
        print(f"📎 Processing {len(files)} file(s)...")
        logger.info(f"📎 Multipart request received with {len(files)} files")
        if len(files) > 5:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum 5 files allowed per request"
            )
        file_parts = await process_uploaded_files(files)
        print(f"✅ Processed {len(file_parts)} file(s) - FileParts created")
        logger.info(f"✅ Processed {len(file_parts)} files for multipart request")
        
        # Log detalhes dos arquivos processados
        for i, fp in enumerate(file_parts):
            try:
                if fp.type == "text" or fp.mime_type == "text/plain":
                    decoded = base64.b64decode(fp.data).decode('utf-8')
                    print(f"  File {i+1}: {fp.file_name} - {len(decoded)} chars text")
                    print(f"    Preview: {decoded[:200]}...")
                else:
                    print(f"  File {i+1}: {fp.file_name} - {fp.type} ({len(fp.data)} chars base64)")
            except Exception as e:
                print(f"  File {i+1}: {fp.file_name} - Error decoding: {e}")
    else:
        print("📎 No files in request")
        logger.info("📎 Multipart request received without files")
    
    async def generate() -> AsyncGenerator[str, None]:
        """Generate response chunks."""
        try:
            # Determine agent - use default agent from file if not provided
            agent_id_param = agent_id
            default_agent_entity = None
            
            if agent_id_param is None:
                try:
                    default_agent_entity = load_default_agent()
                    agent_id_param = default_agent_entity.id or 0
                    agent_name = default_agent_entity.name
                except Exception as e:
                    logger.warning(f"Could not load default agent from file: {e}")
                    agents = get_user_agents_use_case.execute(user_id)
                    if not agents:
                        raise HTTPException(
                            status_code=status.HTTP_404_NOT_FOUND,
                            detail="No agents found. Please create an agent first or ensure default agent file is available."
                        )
                    agent_id_param = agents[0].id
                    agent_name = agents[0].name
            else:
                agent = get_agent_use_case.execute(agent_id_param, user_id)
                if not agent:
                    raise AgentNotFoundError(agent_id_param)
                agent_name = agent.name
            
            session_id_param = session_id or generate_session_id()
            
            if default_agent_entity:
                model_name = model or default_agent_entity.model
            else:
                from src.models import Agent
                agent_model = get_agent_use_case.execute(agent_id_param, user_id)
                model_name = model or agent_model.model
            
            print(f"\n🚀 SENDING TO LLM:")
            print(f"  Agent: {agent_id_param} ({agent_name})")
            print(f"  Model: {model_name}")
            print(f"  Message: {message[:100]}...")
            print(f"  Files: {len(file_parts) if file_parts else 0}")
            logger.info(f"🚀 Chat Stream Multipart Request - User: {user_id}, Agent: {agent_id_param} ({agent_name}), Model: {model_name}, Files: {len(file_parts) if file_parts else 0}")
            
            # Log detalhes dos file_parts antes de enviar
            if file_parts:
                print(f"\n📎 FileParts being sent to LLM:")
                for i, fp in enumerate(file_parts):
                    print(f"  FilePart {i+1}:")
                    print(f"    Name: {fp.file_name}")
                    print(f"    Type: {fp.type}")
                    print(f"    MIME: {fp.mime_type}")
                    try:
                        if fp.type == "text" or fp.mime_type == "text/plain":
                            decoded = base64.b64decode(fp.data).decode('utf-8')
                            print(f"    Text length: {len(decoded)} chars")
                            print(f"    Preview: {decoded[:300]}...")
                        else:
                            print(f"    Data length: {len(fp.data)} chars (base64)")
                    except Exception as e:
                        print(f"    Error decoding: {e}")
            
            if default_agent_entity:
                print(f"\n📤 Calling execute_with_agent_stream with files...")
                async for chunk in chat_use_case.execute_with_agent_stream(
                    user_id=user_id,
                    agent=default_agent_entity,
                    message=message,
                    session_id=session_id_param,
                    model_override=model,
                    files=file_parts
                ):
                    yield chunk
            else:
                print(f"\n📤 Calling execute_stream with files...")
                async for chunk in chat_use_case.execute_stream(
                    user_id=user_id,
                    agent_id=agent_id_param,
                    message=message,
                    session_id=session_id_param,
                    model_override=model,
                    files=file_parts
                ):
                    yield chunk
                
        except (AgentNotFoundError, InvalidModelError, UnsupportedModelError) as e:
            error_msg = f"Error: {str(e)}"
            logger.error(error_msg)
            yield error_msg
        except HTTPException as e:
            error_msg = f"Error: {e.detail}"
            logger.error(error_msg)
            yield error_msg
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            logger.error(f"Error executing agent stream: {e}", exc_info=True)
            yield error_msg
    
    return StreamingResponse(generate(), media_type="text/plain")

