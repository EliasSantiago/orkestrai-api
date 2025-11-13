"""SQLAlchemy implementation of AgentRepository."""

from typing import List, Optional
from sqlalchemy.orm import Session
from src.domain.repositories.agent_repository import AgentRepository
from src.domain.entities.agent import Agent
from src.models import Agent as AgentModel


class SQLAlchemyAgentRepository(AgentRepository):
    """SQLAlchemy implementation of AgentRepository."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def _to_entity(self, model: AgentModel) -> Agent:
        """Convert SQLAlchemy model to domain entity."""
        return Agent(
            id=model.id,
            name=model.name,
            description=model.description,
            instruction=model.instruction,
            model=model.model,
            tools=model.tools or [],
            use_file_search=model.use_file_search,
            user_id=model.user_id,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at
        )
    
    def _to_model(self, entity: Agent) -> AgentModel:
        """Convert domain entity to SQLAlchemy model."""
        if entity.id:
            # Update existing
            model = self.db.query(AgentModel).filter(
                AgentModel.id == entity.id
            ).first()
            if model:
                model.name = entity.name
                model.description = entity.description
                model.instruction = entity.instruction
                model.model = entity.model
                model.tools = entity.tools
                model.use_file_search = entity.use_file_search
                return model
        
        # Create new
        return AgentModel(
            name=entity.name,
            description=entity.description,
            instruction=entity.instruction,
            model=entity.model,
            tools=entity.tools,
            use_file_search=entity.use_file_search,
            user_id=entity.user_id,
            is_active=entity.is_active
        )
    
    def create(self, agent: Agent) -> Agent:
        """Create a new agent."""
        model = self._to_model(agent)
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return self._to_entity(model)
    
    def get_by_id(self, agent_id: int, user_id: int) -> Optional[Agent]:
        """Get agent by ID (only if owned by user)."""
        model = self.db.query(AgentModel).filter(
            AgentModel.id == agent_id,
            AgentModel.user_id == user_id,
            AgentModel.is_active == True
        ).first()
        return self._to_entity(model) if model else None
    
    def get_by_user(self, user_id: int) -> List[Agent]:
        """Get all active agents for a user."""
        models = self.db.query(AgentModel).filter(
            AgentModel.user_id == user_id,
            AgentModel.is_active == True
        ).order_by(AgentModel.created_at.desc()).all()
        return [self._to_entity(model) for model in models]
    
    def update(self, agent: Agent) -> Optional[Agent]:
        """Update an agent."""
        model = self.db.query(AgentModel).filter(
            AgentModel.id == agent.id,
            AgentModel.user_id == agent.user_id
        ).first()
        if not model:
            return None
        
        model.name = agent.name
        model.description = agent.description
        model.instruction = agent.instruction
        model.model = agent.model
        model.tools = agent.tools
        model.use_file_search = agent.use_file_search
        
        self.db.commit()
        self.db.refresh(model)
        return self._to_entity(model)
    
    def delete(self, agent_id: int, user_id: int) -> bool:
        """Soft delete an agent (only if owned by user)."""
        model = self.db.query(AgentModel).filter(
            AgentModel.id == agent_id,
            AgentModel.user_id == user_id,
            AgentModel.is_active == True
        ).first()
        if not model:
            return False
        
        model.is_active = False
        self.db.commit()
        return True

