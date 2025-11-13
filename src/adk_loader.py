"""
Loader for ADK agents from database.

This module loads agents from PostgreSQL database and converts them
to ADK Agent objects that can be used by the ADK web interface.
"""

import os
from typing import List, Dict, Optional
from pathlib import Path
from sqlalchemy.orm import Session
from google.adk.agents import Agent
from src.database import SessionLocal
from src.models import Agent as AgentModel
from tools import calculator, get_current_time, tavily_web_search

# Tool mapping from database names to actual functions
# Note: MCP tools are loaded dynamically at runtime via agent_chat_routes.py
# They are not included here as they require user-specific clients
TOOL_MAP = {
    "calculator": calculator,
    "get_current_time": get_current_time,
    "tavily_web_search": tavily_web_search,
}


def get_tools_from_names(tool_names: List[str]) -> List:
    """Convert tool names from database to actual tool functions."""
    tools = []
    for tool_name in tool_names:
        if tool_name in TOOL_MAP:
            tools.append(TOOL_MAP[tool_name])
        else:
            print(f"⚠ Warning: Tool '{tool_name}' not found, skipping")
    return tools


def sanitize_agent_name_for_adk(name: str, agent_id: int) -> str:
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


def load_agent_from_db(db_agent: AgentModel) -> Optional[Agent]:
    """Convert a database Agent model to an ADK Agent object."""
    try:
        # Get tools from database
        tool_names = db_agent.tools or []
        tools = get_tools_from_names(tool_names)
        
        # Sanitize agent name for ADK (must be valid identifier)
        agent_name_sanitized = sanitize_agent_name_for_adk(db_agent.name, db_agent.id)
        
        # Create ADK Agent
        adk_agent = Agent(
            model=db_agent.model,
            name=agent_name_sanitized,
            description=db_agent.description or "",
            instruction=db_agent.instruction,
            tools=tools,
        )
        
        return adk_agent
    except Exception as e:
        print(f"✗ Erro ao carregar agente '{db_agent.name}': {e}")
        return None


def load_all_agents_from_db(db: Session) -> Dict[str, Agent]:
    """Load all active agents from database and return as ADK Agent objects."""
    agents = {}
    
    # Get all active agents from database
    db_agents = db.query(AgentModel).filter(
        AgentModel.is_active == True
    ).all()
    
    if not db_agents:
        print("⚠ Nenhum agente ativo encontrado no banco de dados")
        return agents
    
    print(f"\n📦 Carregando {len(db_agents)} agente(s) do banco de dados...")
    
    for db_agent in db_agents:
        adk_agent = load_agent_from_db(db_agent)
        if adk_agent:
            # Use the agent name as key, or create a unique key
            agent_key = f"agent_{db_agent.id}"  # Use ID to avoid conflicts
            agents[agent_key] = adk_agent
            print(f"  ✓ {db_agent.name} (ID: {db_agent.id})")
    
    return agents


def create_dynamic_agents_module(db_agents: List[AgentModel], output_dir: Path) -> Path:
    """
    Create a dynamic agents module that ADK can load.
    
    This creates a temporary directory structure that ADK expects,
    with agent.py files containing the agents from the database.
    
    ADK expects: agents/<agent_name>/agent.py
    We'll create one directory per agent from database.
    """
    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # ADK expects: agents/<agent_name>/agent.py
    # Create agents directory
    agents_base_dir = output_dir / "agents"
    agents_base_dir.mkdir(parents=True, exist_ok=True)
    
    # Create mapping of active agent IDs to their expected directory names
    active_agent_ids = {db_agent.id for db_agent in db_agents}
    active_agent_dirs = set()
    agent_id_to_dir = {}
    
    for db_agent in db_agents:
        # Sanitize agent name for directory name (same logic as below)
        base_agent_name = db_agent.name.lower().replace(" ", "_").replace("-", "_")
        base_agent_name = "".join(c for c in base_agent_name if c.isalnum() or c == "_")
        if not base_agent_name:
            base_agent_name = f"agent_{db_agent.id}"
        
        # Always use ID to ensure uniqueness
        agent_name = f"{base_agent_name}_{db_agent.id}"
        
        # Store directory name with ID
        active_agent_dirs.add(agent_name)
        agent_id_to_dir[db_agent.id] = agent_name
    
    # Remove directories for agents that no longer exist (deleted/inactive)
    if agents_base_dir.exists():
        import shutil
        for existing_dir in list(agents_base_dir.iterdir()):  # Convert to list to avoid modification during iteration
            if not existing_dir.is_dir():
                continue
                
            dir_name = existing_dir.name
            
            # If we have active agents, remove db_agents directory (it's only for when there are no agents)
            if db_agents and dir_name == "db_agents":
                try:
                    shutil.rmtree(existing_dir)
                    print(f"  🗑️  Removido diretório padrão 'db_agents' (agentes ativos encontrados)")
                except Exception as e:
                    print(f"  ⚠ Warning: Não foi possível remover diretório {dir_name}: {e}")
                continue
            
            # If no active agents, keep only db_agents, remove all others
            if not db_agents:
                if dir_name != "db_agents":
                    try:
                        shutil.rmtree(existing_dir)
                        print(f"  🗑️  Removido diretório (nenhum agente ativo): {dir_name}")
                    except Exception as e:
                        print(f"  ⚠ Warning: Não foi possível remover diretório {dir_name}: {e}")
                continue
            
            # Try to identify which agent this directory belongs to by reading agent.py
            agent_file = existing_dir / "agent.py"
            agent_id_found = None
            
            if agent_file.exists():
                try:
                    content = agent_file.read_text()
                    # Look for agent ID in comment: "# Agent: {name} (ID: {id})"
                    for db_agent in db_agents:
                        if f"Agent: {db_agent.name} (ID: {db_agent.id})" in content:
                            agent_id_found = db_agent.id
                            break
                    
                    # If not found by comment, try to extract from directory name
                    if agent_id_found is None:
                        # Try to extract ID from directory name (e.g., "agent_name_123")
                        parts = dir_name.split("_")
                        for part in reversed(parts):
                            try:
                                potential_id = int(part)
                                if potential_id in active_agent_ids:
                                    agent_id_found = potential_id
                                    break
                            except ValueError:
                                continue
                except Exception as e:
                    print(f"  ⚠ Warning: Erro ao ler {agent_file}: {e}")
            
            # Check if directory name matches any active agent
            if agent_id_found is None:
                # Try matching by directory name (should always include ID now)
                for db_agent in db_agents:
                    expected_dir = agent_id_to_dir.get(db_agent.id)
                    if expected_dir and dir_name == expected_dir:
                        agent_id_found = db_agent.id
                        break
                    # Also check old format without ID for backward compatibility
                    base_name = db_agent.name.lower().replace(" ", "_").replace("-", "_")
                    base_name = "".join(c for c in base_name if c.isalnum() or c == "_")
                    if base_name and dir_name == base_name:
                        agent_id_found = db_agent.id
                        break
            
            # If directory doesn't correspond to any active agent, remove it
            if agent_id_found is None or agent_id_found not in active_agent_ids:
                try:
                    shutil.rmtree(existing_dir)
                    print(f"  🗑️  Removido diretório de agente deletado: {dir_name}")
                except Exception as e:
                    print(f"  ⚠ Warning: Não foi possível remover diretório {dir_name}: {e}")
    
    # Create individual directories for EACH agent so they all appear in ADK dropdown
    # ADK lists each subdirectory in agents/ as a separate agent
    # IMPORTANT: Create a directory for ALL agents, not just from the second one
    if not db_agents:
        # If no agents, create a default directory
        agent_dir = agents_base_dir / "db_agents"
        agent_dir.mkdir(parents=True, exist_ok=True)
        init_file = agent_dir / "__init__.py"
        init_file.write_text("# Auto-generated agents from database\n")
        agent_file = agent_dir / "agent.py"
        
        # Default root_agent if no agents in database
        lines = [
            "# Auto-generated agent from database",
            "# DO NOT EDIT THIS FILE MANUALLY",
            "",
            "import os",
            "import sys",
            "from pathlib import Path",
            "",
            "project_root = Path(__file__).parent.parent.parent.parent.resolve()",
            "project_root_str = str(project_root)",
            "if project_root_str not in sys.path:",
            "    sys.path.insert(0, project_root_str)",
            "",
            "from dotenv import load_dotenv",
            "from google.adk.agents import Agent",
            "",
            "load_dotenv(project_root / '.env')",
            "",
            "GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', '')",
            "if GOOGLE_API_KEY:",
            "    os.environ['GOOGLE_API_KEY'] = GOOGLE_API_KEY",
            "",
            "# Default root agent (no agents in database)",
            "root_agent = Agent(",
            "    model='gemini-2.0-flash-exp',",
            "    name='root_agent',",
            "    description='Default agent - no agents found in database',",
            "    instruction='You are a helpful assistant. Please add agents to the database to use this system.',",
            "    tools=[],",
            ")",
        ]
        agent_file.write_text("\n".join(lines))
        return agent_dir
    
    # Create a directory for EACH agent (including the first one)
    # This ensures all agents appear in the ADK Web dropdown
    created_dirs = []
    # Track used directory names to avoid duplicates
    used_dir_names = set()
    
    for db_agent in db_agents:
        # Sanitize agent name for directory name
        base_agent_name = db_agent.name.lower().replace(" ", "_").replace("-", "_")
        base_agent_name = "".join(c for c in base_agent_name if c.isalnum() or c == "_")
        if not base_agent_name:
            base_agent_name = f"agent_{db_agent.id}"
        
        # Always use agent ID to ensure uniqueness, even for first occurrence
        # This prevents conflicts when multiple agents have the same name
        agent_name = f"{base_agent_name}_{db_agent.id}"
        
        # Check if directory already exists and corresponds to this agent
        existing_dir = agents_base_dir / agent_name
        if existing_dir.exists():
            # Verify it's the correct agent by checking agent.py
            agent_file = existing_dir / "agent.py"
            if agent_file.exists():
                try:
                    content = agent_file.read_text()
                    if f"Agent: {db_agent.name} (ID: {db_agent.id})" in content:
                        # Directory already exists and is correct, reuse it
                        used_dir_names.add(agent_name)
                        created_dirs.append(existing_dir)
                        continue
                except Exception:
                    # If we can't verify, remove and recreate
                    pass
        
        # If directory doesn't exist or is incorrect, create/recreate it
        # If somehow still duplicate (shouldn't happen), add counter
        counter = 1
        original_agent_name = agent_name
        while agent_name in used_dir_names:
            agent_name = f"{original_agent_name}_{counter}"
            counter += 1
        
        used_dir_names.add(agent_name)
        individual_agent_dir = agents_base_dir / agent_name
        # Remove if exists (will be recreated)
        if individual_agent_dir.exists():
            import shutil
            shutil.rmtree(individual_agent_dir)
        individual_agent_dir.mkdir(parents=True, exist_ok=True)
        created_dirs.append(individual_agent_dir)
        
        # Create __init__.py
        individual_init = individual_agent_dir / "__init__.py"
        individual_init.write_text("# Auto-generated agent from database\n")
        
        # Create agent.py with single agent as root_agent
        individual_agent_file = individual_agent_dir / "agent.py"
        
        # Generate content for individual agent
        tool_names = db_agent.tools or []
        tool_list = []
        for tool_name in tool_names:
            if tool_name == "calculator":
                tool_list.append("calculator")
            elif tool_name == "get_current_time":
                tool_list.append("get_current_time")
            elif "_" in tool_name:
                # MCP tools (dynamically loaded, format: provider_toolname)
                tool_list.append(tool_name)
        
        description = (db_agent.description or "").replace("'", "\\'").replace("\n", "\\n")
        instruction = db_agent.instruction.replace("'", "\\'").replace("\n", "\\n")
        model = db_agent.model.replace("'", "\\'")
        
        # Sanitize agent name for ADK (must be valid identifier)
        # Remove accents and special characters
        import unicodedata
        agent_name_sanitized = unicodedata.normalize('NFD', db_agent.name)
        agent_name_sanitized = ''.join(c for c in agent_name_sanitized if unicodedata.category(c) != 'Mn')
        agent_name_sanitized = agent_name_sanitized.lower().replace(" ", "_").replace("-", "_")
        agent_name_sanitized = "".join(c for c in agent_name_sanitized if c.isalnum() or c == "_")
        if not agent_name_sanitized or not (agent_name_sanitized[0].isalpha() or agent_name_sanitized[0] == "_"):
            agent_name_sanitized = f"agent_{agent_name_sanitized}" if agent_name_sanitized else f"agent_{db_agent.id}"
        
        individual_lines = [
            "# Auto-generated agent from database",
            "# DO NOT EDIT THIS FILE MANUALLY",
            "",
            "import os",
            "import sys",
            "from pathlib import Path",
            "",
            "# Add project root to path",
            "project_root = Path(__file__).parent.parent.parent.parent.resolve()",
            "project_root_str = str(project_root)",
            "if project_root_str not in sys.path:",
            "    sys.path.insert(0, project_root_str)",
            "",
            "# Also add to PYTHONPATH environment variable",
            "if 'PYTHONPATH' in os.environ:",
            "    if project_root_str not in os.environ['PYTHONPATH']:",
            "        os.environ['PYTHONPATH'] = f\"{project_root_str}:{os.environ['PYTHONPATH']}\"",
            "else:",
            "    os.environ['PYTHONPATH'] = project_root_str",
            "",
            "# Ensure tools can be imported",
            "try:",
            "    from tools import calculator, get_current_time",
            "    # Note: MCP tools are loaded dynamically at runtime",
            "    # They are not imported here as they require user-specific clients",
            "except ImportError as e:",
            "    import sys",
            "    if project_root_str not in sys.path:",
            "        sys.path.insert(0, project_root_str)",
            "    try:",
            "        import importlib.util",
            "        tools_spec = importlib.util.spec_from_file_location(",
            "            'tools',",
            "            project_root / 'tools' / '__init__.py'",
            "        )",
            "        tools_module = importlib.util.module_from_spec(tools_spec)",
            "        tools_spec.loader.exec_module(tools_module)",
            "        calculator = tools_module.calculator",
            "        get_current_time = tools_module.get_current_time",
            "    except Exception:",
            "        sys.path.insert(0, project_root_str)",
            "        from tools import calculator, get_current_time",
            "",
            "from dotenv import load_dotenv",
            "from google.adk.agents import Agent",
            "",
            "# Load environment variables",
            "load_dotenv(project_root / '.env')",
            "",
            "# Configure Google API key",
            "GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', '')",
            "if GOOGLE_API_KEY:",
            "    os.environ['GOOGLE_API_KEY'] = GOOGLE_API_KEY",
            "",
            "# Import context hooks for automatic Redis integration",
            "try:",
            "    from src.services.adk_context_hooks import inject_context_into_agent",
            "    CONTEXT_ENABLED = True",
            "except ImportError:",
            "    CONTEXT_ENABLED = False",
            "    inject_context_into_agent = None",
            "",
            f"# Agent: {db_agent.name} (ID: {db_agent.id})",
            "root_agent = Agent(",
            f"    model='{model}',",
            f"    name='{agent_name_sanitized}',",
            f"    description='{description}',",
            f"    instruction='''{instruction}''',",
        ]
        
        if tool_list:
            tools_str = ", ".join(tool_list)
            individual_lines.append(f"    tools=[{tools_str}],")
        else:
            individual_lines.append(f"    tools=[],")
        
        individual_lines.append(")")
        individual_lines.append("")
        individual_lines.append("# Inject context into agent if enabled")
        individual_lines.append("if CONTEXT_ENABLED and inject_context_into_agent:")
        individual_lines.append("    try:")
        individual_lines.append("        inject_context_into_agent(root_agent)")
        individual_lines.append("    except Exception as e:")
        individual_lines.append("        print(f'⚠ Warning: Could not inject context into root_agent: {e}')")
        
        individual_agent_file.write_text("\n".join(individual_lines))
    
    # Return the first created directory (or agents_base_dir if none created)
    return created_dirs[0] if created_dirs else agents_base_dir


def sync_agents_from_db(output_dir: Optional[Path] = None) -> Path:
    """
    Sync agents from database to a directory structure that ADK can use.
    
    This function:
    1. Loads all active agents from the database
    2. Creates a temporary directory structure
    3. Generates agent.py files that ADK can load
    
    Returns the path to the generated agents directory.
    """
    if output_dir is None:
        # Use a temporary directory in the project root
        project_root = Path(__file__).parent.parent
        output_dir = project_root / ".agents_db"
    
    # Create database session
    db = SessionLocal()
    try:
        # Get all active agents from database directly
        db_agents = db.query(AgentModel).filter(
            AgentModel.is_active == True
        ).order_by(AgentModel.created_at.desc()).all()
        
        if not db_agents:
            print("⚠ Nenhum agente ativo encontrado no banco de dados")
            print("  Crie agentes usando a API REST em http://localhost:8001/docs")
        
        # Create dynamic agents module
        agent_dir = create_dynamic_agents_module(db_agents, output_dir)
        
        print(f"\n✓ Agentes sincronizados para: {agent_dir}")
        print(f"  Total de agentes: {len(db_agents)}")
        return agent_dir
        
    finally:
        db.close()


if __name__ == "__main__":
    # Test loading agents
    print("=" * 60)
    print("Testando carregamento de agentes do banco")
    print("=" * 60)
    
    agent_dir = sync_agents_from_db()
    print(f"\n✓ Diretório de agentes criado: {agent_dir}")

