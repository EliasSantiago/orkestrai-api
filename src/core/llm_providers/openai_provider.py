"""OpenAI LLM provider."""

import os
import inspect
from typing import List, Optional, AsyncIterator, Dict, Any
from openai import AsyncOpenAI
import httpx
from src.core.llm_provider import LLMProvider, LLMMessage
from src.config import Config


class OpenAIProvider(LLMProvider):
    """OpenAI provider for GPT models."""
    
    def __init__(self):
        api_key = Config.OPENAI_API_KEY
        if not api_key:
            raise ValueError("OPENAI_API_KEY not configured in environment")
        
        # Configure HTTP client with SSL verification setting
        http_client = None
        if not Config.VERIFY_SSL:
            import warnings
            warnings.warn(
                "⚠️ SSL verification is disabled. This is insecure and should only be used in development!",
                UserWarning
            )
            http_client = httpx.AsyncClient(verify=False)
        
        self.client = AsyncOpenAI(
            api_key=api_key,
            http_client=http_client
        )
        self.supported_models = [
            "gpt-4o",
            "gpt-4o-mini",
            "gpt-4-turbo",
            "gpt-4-turbo-preview",
            "gpt-4",
            "gpt-3.5-turbo",
            "o1-preview",
            "o1-mini",
        ]
    
    def supports_model(self, model: str) -> bool:
        """
        Check if model is an OpenAI model.
        
        Note: We check for specific OpenAI model patterns to avoid conflicts
        with on-premise models that might start with "gpt-".
        """
        # Check if it's in the known OpenAI models list
        if model in self.supported_models:
            return True
        
        # Check for OpenAI-specific patterns
        # Be more specific to avoid matching on-premise models like "gpt-oss:20b"
        if model.startswith("gpt-4") or model.startswith("gpt-3.5") or model.startswith("o1-"):
            return True
        
        # For other "gpt-" patterns, check for on-premise indicators
        if model.startswith("gpt-"):
            # Reject patterns that indicate on-premise models:
            # - "gpt-oss:20b" (has colon) - on-premise indicator
            # - "gpt-custom:" (has colon) - on-premise indicator
            if ":" in model:
                # Models with colon are likely on-premise (e.g., "gpt-oss:20b")
                return False
            
            # Accept standard OpenAI format (gpt-4o, gpt-4o-mini, etc.)
            # These have dashes but no colons
            return True
        
        return False
    
    def get_supported_models(self) -> List[str]:
        """Get list of supported OpenAI models."""
        return self.supported_models.copy()
    
    def _convert_tools_to_openai_format(self, tools: List) -> List[Dict[str, Any]]:
        """
        Convert Python functions to OpenAI function calling format.
        
        Args:
            tools: List of Python function objects
            
        Returns:
            List of OpenAI tool definitions with complete schemas
        """
        openai_tools = []
        
        for tool in tools:
            if not callable(tool):
                continue
                
            # Get function name
            func_name = getattr(tool, '__name__', 'unknown')
            
            # Get description from docstring
            docstring = inspect.getdoc(tool) or ""
            # Extract first line or paragraph as description
            description = docstring.split('\n\n')[0].strip() if docstring else f"Tool: {func_name}"
            
            # Get function signature
            sig = inspect.signature(tool)
            parameters = {}
            required = []
            
            for param_name, param in sig.parameters.items():
                # Skip user_id as it's injected automatically
                if param_name == 'user_id':
                    continue
                    
                param_info = {
                    "type": "string"  # Default type
                }
                
                # Try to infer type from annotation
                if param.annotation != inspect.Parameter.empty:
                    ann_str = str(param.annotation)
                    if 'int' in ann_str or 'Integer' in ann_str:
                        param_info["type"] = "integer"
                    elif 'float' in ann_str or 'Float' in ann_str:
                        param_info["type"] = "number"
                    elif 'bool' in ann_str or 'Boolean' in ann_str:
                        param_info["type"] = "boolean"
                    elif 'list' in ann_str.lower() or 'List' in ann_str or 'Array' in ann_str:
                        param_info["type"] = "array"
                        # OpenAI requires 'items' for array types
                        # Default to string items, but can be overridden
                        param_info["items"] = {"type": "string"}
                        # Try to infer item type from annotation (e.g., List[Dict] -> object)
                        if 'Dict' in ann_str or 'dict' in ann_str.lower():
                            param_info["items"] = {"type": "object"}
                        elif 'int' in ann_str:
                            param_info["items"] = {"type": "integer"}
                    elif 'dict' in ann_str.lower() or 'Dict' in ann_str or 'object' in ann_str.lower():
                        param_info["type"] = "object"
                        # OpenAI requires 'properties' for object types, but we'll leave it flexible
                        # The model can accept any object structure
                        param_info["additionalProperties"] = True
                
                # Get description from docstring if available
                if docstring:
                    # Look for Args section
                    if "Args:" in docstring or "Arguments:" in docstring:
                        lines = docstring.split('\n')
                        in_args_section = False
                        for i, line in enumerate(lines):
                            line_stripped = line.strip()
                            if line_stripped.startswith("Args:") or line_stripped.startswith("Arguments:"):
                                in_args_section = True
                                continue
                            if in_args_section:
                                # Check if this line describes our parameter
                                if line_stripped.startswith(f"{param_name}:") or line_stripped.startswith(f"{param_name} "):
                                    # Extract description after colon
                                    if ':' in line_stripped:
                                        desc = line_stripped.split(':', 1)[1].strip()
                                        if desc:
                                            param_info["description"] = desc
                                            break
                                    # Or check next line if current line is just the parameter name
                                    elif i + 1 < len(lines):
                                        next_line = lines[i + 1].strip()
                                        if next_line and not next_line.startswith(('Args:', 'Returns:', 'Example:')):
                                            param_info["description"] = next_line
                                            break
                            # Stop if we hit Returns or Example section
                            if line_stripped.startswith(("Returns:", "Example:", "Raises:")):
                                break
                
                # If no description found, create a default one
                if "description" not in param_info:
                    param_info["description"] = f"Parameter {param_name}"
                
                parameters[param_name] = param_info
                
                # Check if parameter is required
                if param.default == inspect.Parameter.empty:
                    required.append(param_name)
            
            # Build OpenAI function schema
            function_schema = {
                "name": func_name,
                "description": description,
                "parameters": {
                    "type": "object",
                    "properties": parameters,
                }
            }
            
            if required:
                function_schema["parameters"]["required"] = required
            
            openai_tools.append({
                "type": "function",
                "function": function_schema
            })
        
        return openai_tools
    
    async def chat(
        self,
        messages: List[LLMMessage],
        model: str,
        tools: Optional[List] = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """Chat using OpenAI API."""
        # Convert messages to OpenAI format
        openai_messages = []
        for msg in messages:
            # OpenAI doesn't have a separate system role in the messages array
            # System messages should be included as role="system"
            openai_messages.append({
                "role": msg.role,
                "content": msg.content
            })
        
        # Prepare tools if provided
        openai_tools = None
        if tools:
            openai_tools = self._convert_tools_to_openai_format(tools)
        
        # Create stream
        try:
            # Build tool map for execution
            tool_map = {}
            if tools:
                for tool in tools:
                    if callable(tool):
                        tool_map[getattr(tool, '__name__', 'unknown')] = tool
            
            # Use non-streaming for function calling to properly handle tool calls
            # OpenAI streaming doesn't work well with function calling
            if openai_tools:
                # First, make a non-streaming call to handle function calling
                response = await self.client.chat.completions.create(
                    model=model,
                    messages=openai_messages,
                    tools=openai_tools,
                    temperature=kwargs.get("temperature", 0.7),
                    max_tokens=kwargs.get("max_tokens", None),
                )
                
                # Handle function calling loop
                max_iterations = 5  # Prevent infinite loops
                iteration = 0
                
                while iteration < max_iterations:
                    choice = response.choices[0]
                    message = choice.message
                    
                    # Check if model wants to call a function
                    if message.tool_calls:
                        # Add assistant message with tool calls
                        openai_messages.append({
                            "role": "assistant",
                            "content": message.content,
                            "tool_calls": [
                                {
                                    "id": tc.id,
                                    "type": tc.type,
                                    "function": {
                                        "name": tc.function.name,
                                        "arguments": tc.function.arguments
                                    }
                                }
                                for tc in message.tool_calls
                            ]
                        })
                        
                        # Execute tool calls
                        for tool_call in message.tool_calls:
                            func_name = tool_call.function.name
                            func_args_str = tool_call.function.arguments
                            
                            # Find and execute the tool
                            if func_name in tool_map:
                                import json
                                import logging
                                logger = logging.getLogger(__name__)
                                try:
                                    func_args = json.loads(func_args_str)
                                    tool_func = tool_map[func_name]
                                    logger.info(f"Executing tool {func_name} with args: {func_args}")
                                    
                                    # Execute tool in a way that handles async context
                                    import concurrent.futures
                                    import threading
                                    
                                    tool_result = None
                                    tool_exception = None
                                    
                                    def execute_tool():
                                        nonlocal tool_result, tool_exception
                                        try:
                                            logger.info(f"Executing tool {func_name} with args: {func_args}")
                                            tool_result = tool_func(**func_args)
                                            logger.info(f"Tool {func_name} completed successfully")
                                        except Exception as e:
                                            logger.error(f"Tool {func_name} raised exception: {type(e).__name__}: {e}")
                                            tool_exception = e
                                    
                                    # Execute in thread to avoid async context issues
                                    thread = threading.Thread(target=execute_tool)
                                    thread.start()
                                    thread.join(timeout=30)
                                    
                                    if tool_exception:
                                        logger.error(f"Tool {func_name} failed with exception: {tool_exception}")
                                        raise tool_exception
                                    if thread.is_alive():
                                        logger.error(f"Tool {func_name} timed out after 30 seconds")
                                        raise TimeoutError("Tool execution timed out after 30 seconds")
                                    
                                    logger.info(f"Tool {func_name} result: {tool_result}")
                                    # Convert result to string if needed
                                    if isinstance(tool_result, dict):
                                        import json
                                        tool_result_str = json.dumps(tool_result, ensure_ascii=False, indent=2)
                                    else:
                                        tool_result_str = str(tool_result)
                                    
                                    # Add tool result to messages
                                    openai_messages.append({
                                        "role": "tool",
                                        "tool_call_id": tool_call.id,
                                        "content": tool_result_str
                                    })
                                except Exception as e:
                                    import traceback
                                    error_details = traceback.format_exc()
                                    logger.error(f"Error executing tool {func_name}: {e}\n{error_details}")
                                    
                                    # Add error as tool result with more details
                                    error_msg = str(e)
                                    error_type = type(e).__name__
                                    
                                    # Provide more specific error messages
                                    if "asyncio" in error_msg.lower() or "event loop" in error_msg.lower():
                                        error_msg = "Erro ao executar operação assíncrona. Por favor, tente novamente."
                                    elif "connection" in error_msg.lower() or "connect" in error_msg.lower():
                                        error_msg = f"Erro de conexão: {error_msg}. Verifique sua conexão com o serviço MCP."
                                    elif "401" in error_msg or "unauthorized" in error_msg.lower():
                                        error_msg = "Erro de autenticação. Verifique se sua conexão MCP está ativa."
                                    elif "404" in error_msg or "not found" in error_msg.lower():
                                        error_msg = f"Recurso não encontrado: {error_msg}"
                                    elif "400" in error_msg or "bad request" in error_msg.lower():
                                        error_msg = f"Erro na requisição: {error_msg}. Verifique os parâmetros fornecidos."
                                    
                                    # Include full error details in logs, but user-friendly message in response
                                    error_response = {
                                        "status": "error",
                                        "error": error_msg,
                                        "error_type": error_type,
                                        "tool": func_name
                                    }
                                    
                                    openai_messages.append({
                                        "role": "tool",
                                        "tool_call_id": tool_call.id,
                                        "content": json.dumps(error_response, ensure_ascii=False)
                                    })
                            else:
                                # Tool not found
                                import json
                                openai_messages.append({
                                    "role": "tool",
                                    "tool_call_id": tool_call.id,
                                    "content": json.dumps({"status": "error", "error": f"Tool {func_name} not found"}, ensure_ascii=False)
                                })
                        
                        # Make another call with tool results
                        iteration += 1
                        response = await self.client.chat.completions.create(
                            model=model,
                            messages=openai_messages,
                            tools=openai_tools,
                            temperature=kwargs.get("temperature", 0.7),
                            max_tokens=kwargs.get("max_tokens", None),
                        )
                    else:
                        # No more tool calls, yield the final response
                        if message.content:
                            # Yield content character by character to simulate streaming
                            for char in message.content:
                                yield char
                        break
            else:
                # No tools, use streaming
                stream = await self.client.chat.completions.create(
                    model=model,
                    messages=openai_messages,
                    stream=True,
                    temperature=kwargs.get("temperature", 0.7),
                    max_tokens=kwargs.get("max_tokens", None),
                )
                
                async for chunk in stream:
                    if chunk.choices and len(chunk.choices) > 0:
                        delta = chunk.choices[0].delta
                        if delta and delta.content:
                            yield delta.content
        except Exception as e:
            error_type = type(e).__name__
            error_message = str(e)
            
            # Handle specific error types with user-friendly messages
            if "CERTIFICATE_VERIFY_FAILED" in error_message or "certificate verify failed" in error_message.lower():
                raise Exception(
                    "Erro de certificado SSL ao conectar à API OpenAI. "
                    "Isso geralmente ocorre em ambientes corporativos com certificados autoassinados. "
                    "Para resolver, adicione no .env: VERIFY_SSL=false "
                    "(⚠️ ATENÇÃO: Isso desabilita verificação SSL e é inseguro - use apenas em desenvolvimento)"
                )
            elif "Connection error" in error_message or "ConnectError" in error_type:
                raise Exception(
                    "Erro de conexão com a API OpenAI. "
                    "Verifique sua conexão com a internet e se a API OpenAI está acessível. "
                    "Se estiver atrás de um proxy corporativo, pode ser necessário configurar variáveis de ambiente HTTP_PROXY/HTTPS_PROXY."
                )
            elif "API key" in error_message.lower() or "authentication" in error_message.lower():
                raise Exception(
                    "Erro de autenticação com a API OpenAI. "
                    "Verifique se a OPENAI_API_KEY está configurada corretamente no arquivo .env"
                )
            elif "rate limit" in error_message.lower() or "429" in error_message:
                raise Exception(
                    "Limite de requisições da API OpenAI atingido. "
                    "Por favor, aguarde alguns momentos e tente novamente."
                )
            else:
                # Generic error with more context
                raise Exception(
                    f"Erro ao comunicar com a API OpenAI: {error_message}. "
                    "Verifique sua configuração e conexão com a internet."
                )

