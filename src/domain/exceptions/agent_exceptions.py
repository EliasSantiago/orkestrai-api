"""Domain exceptions for agents."""


class AgentException(Exception):
    """Base exception for agent-related errors."""
    pass


class AgentNotFoundError(AgentException):
    """Raised when agent is not found."""
    
    def __init__(self, agent_id: int):
        self.agent_id = agent_id
        super().__init__(f"Agent with ID {agent_id} not found")


class InvalidModelError(AgentException):
    """Raised when model is not supported."""
    
    def __init__(self, model: str, available_models: dict = None):
        self.model = model
        self.available_models = available_models or {}
        message = f"Model '{model}' is not supported"
        if available_models:
            message += f". Available models: {available_models}"
        super().__init__(message)


class FileSearchModelMismatchError(AgentException):
    """Raised when model is incompatible with file search."""
    
    def __init__(self, model: str, required_model: str = "gemini-2.5-flash, gemini-3-pro-preview, gemini-3-pro, or gemini-2.5-pro"):
        self.model = model
        self.required_model = required_model
        super().__init__(
            f"File Search (RAG) is only supported with Gemini models that support RAG: {required_model}. "
            f"Current model: '{model}'. "
            f"Please use a supported Gemini model when enabling File Search."
        )


class UnsupportedModelError(AgentException):
    """Raised when model is not supported by any provider."""
    
    def __init__(self, model: str, available_models: dict = None):
        self.model = model
        self.available_models = available_models or {}
        message = f"Model '{model}' is not supported by any provider"
        if available_models:
            message += f". Available models: {available_models}"
        super().__init__(message)

