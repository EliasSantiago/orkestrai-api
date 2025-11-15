"""Agent domain entity.

This is a domain entity that represents an Agent in the business logic.
It is independent of persistence details (SQLAlchemy, database, etc.).
"""

from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime


@dataclass
class Agent:
    """Agent domain entity."""
    
    id: Optional[int] = None
    name: str = ""
    description: Optional[str] = None
    instruction: str = ""
    model: str = "gemini-2.0-flash"
    tools: List[str] = None
    use_file_search: bool = False
    user_id: int = 0
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Initialize default values."""
        if self.tools is None:
            self.tools = []
    
    def __repr__(self):
        return f"<Agent(id={self.id}, name={self.name}, user_id={self.user_id})>"

