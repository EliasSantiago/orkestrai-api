"""Google ADK (Gemini) LLM provider."""

import logging
import os
import base64
from typing import List, Optional, AsyncIterator
from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from google.genai import types
from google import genai
from src.core.llm_provider import LLMProvider, LLMMessage, FilePart
from src.config import Config

logger = logging.getLogger(__name__)


class ADKProvider(LLMProvider):
    """Google ADK provider for Gemini models."""
    
    def __init__(self):
        self.supported_models = [
            "gemini-3-pro-preview",  # Latest preview model
            "gemini-2.5-pro",
            "gemini-2.5-flash",  # Recommended for File Search (RAG)
            "gemini-2.0-flash-exp",
            "gemini-2.0-flash-thinking-exp",
            "gemini-1.5-pro",
            "gemini-1.5-pro-latest",
            "gemini-1.5-flash",
            "gemini-1.5-flash-8b",
            "gemini-1.0-pro",
        ]
    
    def supports_model(self, model: str) -> bool:
        """Check if model is a Gemini model."""
        # Remove provider prefix if present (e.g., "gemini/gemini-3-pro-preview" -> "gemini-3-pro-preview")
        model_name = model.replace("gemini/", "").replace("vertex_ai/", "")
        return model_name.startswith("gemini-") or model_name in self.supported_models
    
    def get_supported_models(self) -> List[str]:
        """Get list of supported Gemini models."""
        return self.supported_models.copy()
    
    async def chat(
        self,
        messages: List[LLMMessage],
        model: str,
        tools: Optional[List] = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """Chat using Google ADK."""
        # Separate system messages from conversation
        instruction = ""
        conversation = []
        
        for msg in messages:
            if msg.role == "system":
                instruction += msg.content + "\n"
            else:
                # Build parts for the message (text + files)
                parts = [types.Part(text=msg.content)]
                
                # Add file parts if present
                if msg.files:
                    for file_part in msg.files:
                        if file_part.type == "image":
                            # Decode base64 image
                            image_data = base64.b64decode(file_part.data)
                            parts.append(types.Part(
                                inline_data=types.Blob(
                                    data=image_data,
                                    mime_type=file_part.mime_type or "image/png"
                                )
                            ))
                        elif file_part.type == "pdf" or file_part.mime_type == "application/pdf":
                            # For PDFs, we need to upload to Gemini first
                            # For now, we'll convert to text or skip
                            logger.warning(f"PDF files not yet fully supported in ADK provider: {file_part.file_name}")
                        else:
                            # For other file types, try to handle as text
                            try:
                                text_content = base64.b64decode(file_part.data).decode('utf-8')
                                parts.append(types.Part(text=f"\n[File: {file_part.file_name}]\n{text_content}"))
                            except Exception as e:
                                logger.warning(f"Could not decode file {file_part.file_name}: {e}")
                
                conversation.append(
                    types.Content(
                        parts=parts,
                        role=msg.role
                    )
                )
        
        # If no system message, use instruction from kwargs or default
        if not instruction:
            instruction = kwargs.get("instruction", "You are a helpful assistant.")
        
        # Create ADK agent
        agent_name = kwargs.get("agent_name", "chat_agent")
        agent_description = kwargs.get("agent_description", "Chat agent")
        
        # Prepare tools list (callable functions)
        adk_tools = list(tools or [])
        
        # Log tools for debugging
        logger.info(f"🔧 ADK Provider - Tools received: {len(adk_tools)} tools")
        if adk_tools:
            tool_names = [getattr(tool, '__name__', str(tool)) for tool in adk_tools]
            logger.info(f"🔧 ADK Provider - Tool names: {tool_names}")
        else:
            logger.warning(f"⚠️ ADK Provider - No tools provided! tools parameter: {tools}")
        
        # Check if File Search is enabled
        # ADK doesn't support File Search directly, so we use Gemini client directly when File Search is enabled
        file_search_stores = kwargs.get("file_search_stores")
        use_file_search = file_search_stores and isinstance(file_search_stores, list) and len(file_search_stores) > 0
        
        if use_file_search:
            # Use Gemini client directly for File Search (ADK doesn't support it)
            logger.info(f"File Search enabled with {len(file_search_stores)} stores - using Gemini client directly")
            
            # CRITICAL: Remove Vertex AI credentials to force direct Gemini API
            # Google genai.Client will use Vertex AI if GOOGLE_APPLICATION_CREDENTIALS is present
            original_vertex_creds = None
            vertex_creds_removed = False
            if "GOOGLE_APPLICATION_CREDENTIALS" in os.environ:
                original_vertex_creds = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
                del os.environ["GOOGLE_APPLICATION_CREDENTIALS"]
                vertex_creds_removed = True
                logger.info("🔧 Temporarily removed GOOGLE_APPLICATION_CREDENTIALS to force direct Gemini API")
            
            # Also remove other Vertex AI environment variables
            vertex_env_vars = ["GOOGLE_CLOUD_PROJECT", "GOOGLE_CLOUD_REGION", "GCLOUD_PROJECT"]
            original_vertex_vars = {}
            for var_name in vertex_env_vars:
                if var_name in os.environ:
                    original_vertex_vars[var_name] = os.environ[var_name]
                    del os.environ[var_name]
            
            try:
                # Create Gemini client with explicit API key to force direct API
                if not Config.GOOGLE_API_KEY:
                    raise ValueError("GOOGLE_API_KEY not configured")
                
                # Configure genai to use direct API
                genai.configure(api_key=Config.GOOGLE_API_KEY)
                client = genai.Client(api_key=Config.GOOGLE_API_KEY)
                
                # Create File Search tool
                file_search_tool = types.Tool(
                    file_search=types.FileSearch(
                        file_search_store_names=file_search_stores
                    )
                )
                
                # Prepare conversation for Gemini API
                # Convert messages to Gemini format
                # Gemini API only accepts "user" and "model" roles (not "assistant")
                gemini_messages = []
                file_search_instruction = None
                for msg in messages:
                    if msg.role == "system":
                        # System messages become the instruction
                        file_search_instruction = msg.content
                    else:
                        # Map "assistant" to "model" (Gemini API requirement)
                        gemini_role = "model" if msg.role == "assistant" else msg.role
                        
                        # Build parts for the message (text + files)
                        parts = [types.Part(text=msg.content)]
                        
                        # Add file parts if present
                        if msg.files:
                            for file_part in msg.files:
                                if file_part.type == "image":
                                    # Decode base64 image
                                    image_data = base64.b64decode(file_part.data)
                                    parts.append(types.Part(
                                        inline_data=types.Blob(
                                            data=image_data,
                                            mime_type=file_part.mime_type or "image/png"
                                        )
                                    ))
                                elif file_part.type == "pdf" or file_part.mime_type == "application/pdf":
                                    logger.warning(f"PDF files not yet fully supported in ADK provider: {file_part.file_name}")
                                else:
                                    try:
                                        text_content = base64.b64decode(file_part.data).decode('utf-8')
                                        parts.append(types.Part(text=f"\n[File: {file_part.file_name}]\n{text_content}"))
                                    except Exception as e:
                                        logger.warning(f"Could not decode file {file_part.file_name}: {e}")
                        
                        gemini_messages.append(
                            types.Content(
                                parts=parts,
                                role=gemini_role
                            )
                        )
                
                # Use instruction from kwargs if no system message
                if not file_search_instruction:
                    file_search_instruction = kwargs.get("instruction", "You are a helpful assistant.")
                
                # Get last user message
                if gemini_messages:
                    last_message = gemini_messages[-1]
                else:
                    raise ValueError("No messages provided")
                
                # Generate content with File Search
                config = types.GenerateContentConfig(
                    tools=[file_search_tool],
                    system_instruction=file_search_instruction
                )
                
                # Normalize model name (remove provider prefix if present)
                model_name = model.replace("gemini/", "").replace("vertex_ai/", "")
                
                # Stream response
                response = client.models.generate_content_stream(
                    model=model_name,
                    contents=gemini_messages,
                    config=config
                )
                
                # Yield text chunks
                for chunk in response:
                    if chunk.text:
                        yield chunk.text
            finally:
                # Restore Vertex AI credentials if they were removed
                if vertex_creds_removed and original_vertex_creds:
                    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = original_vertex_creds
                    logger.info("🔧 Restored GOOGLE_APPLICATION_CREDENTIALS")
                
                # Restore other Vertex AI environment variables
                for var_name, var_value in original_vertex_vars.items():
                    os.environ[var_name] = var_value
            return
        
        # No File Search - use ADK as normal
        # Normalize model name (remove provider prefix if present)
        model_name = model.replace("gemini/", "").replace("vertex_ai/", "")
        
        # CRITICAL: Remove Vertex AI credentials to force direct Gemini API
        # Google ADK Agent will use Vertex AI if GOOGLE_APPLICATION_CREDENTIALS is present
        # We need to remove it temporarily to force direct API (Google AI Studio)
        original_vertex_creds = None
        vertex_creds_removed = False
        if "GOOGLE_APPLICATION_CREDENTIALS" in os.environ:
            original_vertex_creds = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
            del os.environ["GOOGLE_APPLICATION_CREDENTIALS"]
            vertex_creds_removed = True
            logger.info("🔧 Temporarily removed GOOGLE_APPLICATION_CREDENTIALS to force direct Gemini API")
        
        # Also remove other Vertex AI environment variables
        vertex_env_vars = ["GOOGLE_CLOUD_PROJECT", "GOOGLE_CLOUD_REGION", "GCLOUD_PROJECT"]
        original_vertex_vars = {}
        for var_name in vertex_env_vars:
            if var_name in os.environ:
                original_vertex_vars[var_name] = os.environ[var_name]
                del os.environ[var_name]
        
        try:
            logger.info(f"🔧 Creating ADK Agent with model: {model_name} and {len(adk_tools)} tools")
            logger.info(f"   Using direct Gemini API (GOOGLE_API_KEY)")
            
            # Configure genai client explicitly to use direct API
            if not Config.GOOGLE_API_KEY:
                raise ValueError("GOOGLE_API_KEY not configured")
            
            # Initialize genai client with API key to ensure direct API usage
            genai.configure(api_key=Config.GOOGLE_API_KEY)
            
            agent = Agent(
                model=model_name,
                name=agent_name,
                description=agent_description,
                instruction=instruction,
                tools=adk_tools  # Only callable functions here
            )
        logger.info(f"✅ ADK Agent created successfully with tools: {[getattr(t, '__name__', str(t)) for t in adk_tools]}")
        
        # Inject context if available (for conversation history)
        # This is done by the caller in agent_chat_routes.py, but we check here too
        if "inject_context" in kwargs and kwargs["inject_context"]:
            try:
                from src.services.adk_context_hooks import inject_context_into_agent
                session_id = kwargs.get("session_id", "default")
                user_id = kwargs.get("user_id", "default")
                inject_context_into_agent(agent, session_id, user_id)
            except Exception as e:
                print(f"⚠ Warning: Could not inject context: {e}")
        
        # Create runner
        app_name = kwargs.get("app_name", "chat_app")
        runner = InMemoryRunner(agent=agent, app_name=app_name)
        
        # Get user ID and session ID
        user_id = kwargs.get("user_id", "default")
        session_id = kwargs.get("session_id", "default")
        
        # Get last user message or use the last message in conversation
        if conversation:
            last_message = conversation[-1]
        else:
            raise ValueError("No messages provided")
        
        # Ensure session exists
        try:
            session = await runner.session_service.get_session(
                app_name=app_name,
                user_id=str(user_id),
                session_id=session_id
            )
            if not session:
                session = await runner.session_service.create_session(
                    app_name=app_name,
                    user_id=str(user_id),
                    session_id=session_id
                )
        except Exception:
            # Try to create session if it doesn't exist
            try:
                await runner.session_service.create_session(
                    app_name=app_name,
                    user_id=str(user_id),
                    session_id=session_id
                )
            except Exception:
                pass  # Session might already exist
        
        # Run agent (File Search is already configured in Agent)
        # The ADK Runner automatically handles tool calls when tools are provided to the Agent
        async for event in runner.run_async(
            user_id=str(user_id),
            session_id=session_id,
            new_message=last_message
        ):
            # Log event type for debugging
            event_type = type(event).__name__
            logger.debug(f"🔍 ADK Event type: {event_type}, event: {event}")
            
            # Check for tool calls (ADK should handle these automatically, but we log them)
            if hasattr(event, 'function_calls') or hasattr(event, 'tool_calls'):
                logger.info(f"🔧 Tool call detected in event: {event}")
            if hasattr(event, 'function_call'):
                logger.info(f"🔧 Function call detected: {event.function_call}")
            
            # Extract text from events
            if hasattr(event, 'content') and event.content:
                for content in event.content if isinstance(event.content, list) else [event.content]:
                    if hasattr(content, 'parts') and content.parts:
                        for part in content.parts:
                            if hasattr(part, 'text') and part.text:
                                yield part.text
                            elif isinstance(part, str):
                                yield part
                    elif isinstance(content, str):
                        yield content
            
            # Also check if event has text directly
            if hasattr(event, 'text') and event.text:
                yield event.text

