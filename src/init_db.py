"""Initialize database with tables."""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.database import init_db, test_connection
from src.config import Config

if __name__ == "__main__":
    print("=" * 60)
    print("Inicializando banco de dados...")
    print("=" * 60)
    
    # Test connection
    if not test_connection():
        print("✗ Erro: Não foi possível conectar ao banco de dados")
        print(f"  Verifique a conexão: {Config.DATABASE_URL}")
        print("  Certifique-se de que o PostgreSQL está rodando:")
        print("    docker-compose up -d")
        exit(1)
    
    print("✓ Conexão estabelecida com sucesso")
    
    # Initialize tables
    try:
        init_db()
        print("✓ Tabelas criadas com sucesso")
        print("\nTabelas criadas:")
        print("  - users")
        print("  - agents")
        print("  - password_reset_tokens")
        print("  - mcp_connections")
        print("  - conversation_sessions")
        print("  - conversation_messages")
    except Exception as e:
        print(f"✗ Erro ao criar tabelas: {e}")
        exit(1)
    
    print("\n" + "=" * 60)
    print("Banco de dados inicializado com sucesso!")
    print("=" * 60)

