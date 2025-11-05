"""Service for managing agents."""

from typing import List, Optional
from sqlalchemy.orm import Session
from src.models import Agent, User


class AgentService:
    """Service for agent CRUD operations."""
    
    @staticmethod
    def create_agent(
        db: Session,
        user_id: int,
        name: str,
        description: Optional[str],
        instruction: str,
        model: str = "gemini-2.0-flash-exp",
        tools: Optional[List[str]] = None
    ) -> Agent:
        """Create a new agent for a user."""
        agent = Agent(
            name=name,
            description=description,
            instruction=instruction,
            model=model,
            tools=tools or [],
            user_id=user_id
        )
        db.add(agent)
        db.commit()
        db.refresh(agent)
        return agent
    
    @staticmethod
    def get_agent_by_id(db: Session, agent_id: int, user_id: int) -> Optional[Agent]:
        """Get an agent by ID (only if owned by user)."""
        return db.query(Agent).filter(
            Agent.id == agent_id,
            Agent.user_id == user_id,
            Agent.is_active == True
        ).first()
    
    @staticmethod
    def get_user_agents(db: Session, user_id: int) -> List[Agent]:
        """Get all active agents for a user."""
        return db.query(Agent).filter(
            Agent.user_id == user_id,
            Agent.is_active == True
        ).order_by(Agent.created_at.desc()).all()
    
    @staticmethod
    def update_agent(
        db: Session,
        agent_id: int,
        user_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        instruction: Optional[str] = None,
        model: Optional[str] = None,
        tools: Optional[List[str]] = None
    ) -> Optional[Agent]:
        """Update an agent (only if owned by user)."""
        agent = AgentService.get_agent_by_id(db, agent_id, user_id)
        if not agent:
            return None
        
        if name is not None:
            agent.name = name
        if description is not None:
            agent.description = description
        if instruction is not None:
            agent.instruction = instruction
        if model is not None:
            agent.model = model
        if tools is not None:
            agent.tools = tools
        
        db.commit()
        db.refresh(agent)
        return agent
    
    @staticmethod
    def delete_agent(db: Session, agent_id: int, user_id: int) -> bool:
        """Soft delete an agent (only if owned by user)."""
        agent = AgentService.get_agent_by_id(db, agent_id, user_id)
        if not agent:
            return False
        
        agent.is_active = False
        db.commit()
        return True

