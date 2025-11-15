"""Google ADK (Gemini) LLM provider."""

import logging
import os
from typing import List, Optional, AsyncIterator
from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from google.genai import types
from google import genai
from src.core.llm_provider import LLMProvider, LLMMessage
from src.config import Config

logger = logging.getLogger(__name__)


class ADKProvider(LLMProvider):
    """Google ADK provider for Gemini models."""
    
    def __init__(self):
        self.supported_models = [
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
        return model.startswith("gemini-") or model in self.supported_models
    
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
                conversation.append(
                    types.Content(
                        parts=[types.Part(text=msg.content)],
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
        
        # Check if File Search is enabled
        # ADK doesn't support File Search directly, so we use Gemini client directly when File Search is enabled
        file_search_stores = kwargs.get("file_search_stores")
        use_file_search = file_search_stores and isinstance(file_search_stores, list) and len(file_search_stores) > 0
        
        if use_file_search:
            # Use Gemini client directly for File Search (ADK doesn't support it)
            logger.info(f"File Search enabled with {len(file_search_stores)} stores - using Gemini client directly")
            
            # Create Gemini client
            if not Config.GOOGLE_API_KEY:
                raise ValueError("GOOGLE_API_KEY not configured")
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
                    gemini_messages.append(
                        types.Content(
                            parts=[types.Part(text=msg.content)],
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
            
            # Stream response
            response = client.models.generate_content_stream(
                model=model,
                contents=gemini_messages,
                config=config
            )
            
            # Yield text chunks
            for chunk in response:
                if chunk.text:
                    yield chunk.text
            return
        
        # No File Search - use ADK as normal
        agent = Agent(
            model=model,
            name=agent_name,
            description=agent_description,
            instruction=instruction,
            tools=adk_tools  # Only callable functions here
        )
        
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
        async for event in runner.run_async(
            user_id=str(user_id),
            session_id=session_id,
            new_message=last_message
        ):
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

