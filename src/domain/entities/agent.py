"""Agent domain entity.

This is a domain entity that represents an Agent in the business logic.
It is independent of persistence details (SQLAlchemy, database, etc.).

Supports multiple agent types:
- llm: LLM agent with tools (default)
- sequential: Workflow agent that executes agents in sequence
- loop: Workflow agent that loops until condition is met
- parallel: Workflow agent that executes agents in parallel
- custom: Custom agent with user-defined logic
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import datetime


@dataclass
class Agent:
    """Agent domain entity."""
    
    id: Optional[int] = None
    name: str = ""
    description: Optional[str] = None
    agent_type: str = "llm"  # llm, sequential, loop, parallel, custom
    
    # LLM Agent fields
    instruction: Optional[str] = None
    model: Optional[str] = "gemini-2.0-flash"
    tools: Optional[List[str]] = None
    use_file_search: bool = False
    
    # Workflow Agent configuration
    workflow_config: Optional[Dict[str, Any]] = None
    
    # Custom Agent configuration
    custom_config: Optional[Dict[str, Any]] = None
    
    # Common fields
    user_id: int = 0
    is_active: bool = True
    is_favorite: bool = False  # Favorite flag for quick access
    icon: Optional[str] = None  # Icon name from lucide-react library
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Initialize default values."""
        if self.tools is None:
            self.tools = []
        if self.workflow_config is None:
            self.workflow_config = {}
        if self.custom_config is None:
            self.custom_config = {}
    
    def __repr__(self):
        return f"<Agent(id={self.id}, name={self.name}, type={self.agent_type}, user_id={self.user_id})>"

