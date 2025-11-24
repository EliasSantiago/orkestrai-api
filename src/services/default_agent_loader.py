"""
Service to load the default chat agent from file.

This service loads the default agent from agents/default_chat_agent/agent.py
and converts it to a domain Agent entity.
"""

import sys
import importlib.util
from pathlib import Path
from typing import Optional
from src.domain.entities.agent import Agent

# Get project root
project_root = Path(__file__).parent.parent.parent.resolve()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


def load_default_agent() -> Optional[Agent]:
    """
    Load the default chat agent from file.
    
    Returns:
        Agent entity if found, None otherwise
    """
    import logging
    logger = logging.getLogger(__name__)
    
    # Path to the agent file
    agent_file_path = project_root / 'agents' / 'default_chat_agent' / 'agent.py'
    
    try:
        # Check if file exists
        if not agent_file_path.exists():
            logger.error(f"Default agent file not found: {agent_file_path}")
            return None
        
        # Use importlib to load the module dynamically
        spec = importlib.util.spec_from_file_location(
            "default_chat_agent.agent",
            agent_file_path
        )
        
        if spec is None or spec.loader is None:
            logger.error(f"Failed to create spec for agent file: {agent_file_path}")
            return None
        
        # Load the module
        agent_module = importlib.util.module_from_spec(spec)
        
        # Add project root to sys.path before loading (in case the module needs it)
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))
        
        # Execute the module
        spec.loader.exec_module(agent_module)
        
        # Get the root_agent from the module
        if not hasattr(agent_module, 'root_agent'):
            logger.error(f"Module {agent_file_path} does not have 'root_agent' attribute")
            return None
        
        root_agent = agent_module.root_agent
        
        logger.info(f"Successfully loaded default agent: {root_agent.name}")
        
        # Convert ADK Agent to domain Agent entity
        # Use friendly name for display, but ADK agent name must be valid identifier
        return Agent(
            id=None,  # Default agent doesn't have a database ID
            name='Chat Geral',  # Friendly display name (not the ADK agent name)
            description=getattr(root_agent, 'description', None) or 'Agente de chat geral disponível para todos os usuários',
            instruction=root_agent.instruction or 'Você é um assistente de IA útil e prestativo.',
            model=root_agent.model or 'gemini-2.5-flash',
            tools=[],  # Default agent doesn't use tools
            use_file_search=False,
            user_id=0,  # System user ID (not in database)
            is_active=True
        )
    except ImportError as e:
        # Log detailed import error
        logger.error(f"Failed to import default agent from file: {e}")
        logger.error(f"Project root: {project_root}")
        logger.error(f"Agent file path: {agent_file_path}")
        logger.error(f"File exists: {agent_file_path.exists()}")
        import traceback
        logger.error(traceback.format_exc())
        return None
    except Exception as e:
        # Log error but don't fail - return None to allow fallback
        logger.error(f"Failed to load default agent from file: {e}")
        logger.error(f"Agent file path: {agent_file_path}")
        import traceback
        logger.error(traceback.format_exc())
        return None

