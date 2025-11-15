"""
Custom ADK server that loads agents from database.

This server starts a FastAPI application that integrates ADK web interface
with agents loaded from PostgreSQL database.
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from src.database import init_db, test_connection
from src.adk_loader import sync_agents_from_db

# Load environment variables
load_dotenv(project_root / '.env')

# Configure Google API key
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
if GOOGLE_API_KEY:
    os.environ['GOOGLE_API_KEY'] = GOOGLE_API_KEY


def main():
    """Main function to start ADK server with database agents."""
    print("=" * 60)
    print("Iniciando ADK Server com Agentes do Banco de Dados")
    print("=" * 60)
    
    # Initialize database
    if test_connection():
        print("✓ Conexão com banco de dados estabelecida")
        init_db()
    else:
        print("⚠ Aviso: Não foi possível conectar ao banco de dados")
        print("  Certifique-se de que o PostgreSQL está rodando: docker-compose up -d")
        print("  Continuando mesmo assim...")
    
    # Sync agents from database
    print("\n📦 Sincronizando agentes do banco de dados...")
    agent_dir = sync_agents_from_db()
    
    # ADK expects: agents/<agent_name>/agent.py
    # Our structure: .agents_db/agents/<agent_name>/agent.py
    # So we need to point to .agents_db/agents (the parent directory)
    agents_parent_dir = agent_dir.parent.resolve()
    
    # Ensure project root is in PYTHONPATH for ADK
    project_root_str = str(project_root.resolve())
    env = os.environ.copy()
    current_pythonpath = env.get("PYTHONPATH", "")
    if project_root_str not in current_pythonpath:
        if current_pythonpath:
            env["PYTHONPATH"] = f"{project_root_str}:{current_pythonpath}"
        else:
            env["PYTHONPATH"] = project_root_str
    
    print("\n" + "=" * 60)
    print("✓ Agentes sincronizados!")
    print(f"  Diretório de agentes: {agent_dir}")
    print(f"  Diretório para ADK: {agents_parent_dir}")
    print(f"  PYTHONPATH: {env.get('PYTHONPATH', 'not set')}")
    print("=" * 60)
    print("\n🚀 Iniciando servidor ADK...")
    print("  Interface Web: http://localhost:8000")
    print("  Pressione Ctrl+C para parar\n")
    
    # Use ADK's web command directly via subprocess
    import subprocess
    
    try:
        subprocess.run([
            "adk", "web",
            str(agents_parent_dir),
            "--host=0.0.0.0",
            "--port=8000"
        ], check=True, env=env)
    except KeyboardInterrupt:
        print("\n\n✓ Servidor ADK encerrado")
    except subprocess.CalledProcessError as e:
        print(f"\n✗ Erro ao iniciar servidor ADK: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

