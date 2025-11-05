"""Migration script to rename username column to name."""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import text
from src.database import engine, test_connection
from src.config import Config


def migrate_username_to_name():
    """Migrate username column to name in users table."""
    print("=" * 60)
    print("Migração: username -> name")
    print("=" * 60)
    
    # Test connection
    if not test_connection():
        print("✗ Erro: Não foi possível conectar ao banco de dados")
        print(f"  Verifique a conexão: {Config.DATABASE_URL}")
        return False
    
    print("✓ Conexão estabelecida")
    
    try:
        with engine.connect() as conn:
            # Check if username column exists
            check_query = text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='users' AND column_name='username'
            """)
            result = conn.execute(check_query)
            username_exists = result.fetchone() is not None
            
            # Check if name column already exists
            check_name_query = text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='users' AND column_name='name'
            """)
            result = conn.execute(check_name_query)
            name_exists = result.fetchone() is not None
            
            if name_exists:
                print("✓ Coluna 'name' já existe")
                if username_exists:
                    print("⚠ Coluna 'username' ainda existe. Removendo...")
                    # Drop username column if it exists
                    drop_query = text("ALTER TABLE users DROP COLUMN IF EXISTS username")
                    conn.execute(drop_query)
                    conn.commit()
                    print("✓ Coluna 'username' removida")
                return True
            
            if username_exists:
                print("Renomeando coluna 'username' para 'name'...")
                # Rename column
                rename_query = text("ALTER TABLE users RENAME COLUMN username TO name")
                conn.execute(rename_query)
                conn.commit()
                print("✓ Coluna renomeada com sucesso")
            else:
                print("⚠ Coluna 'username' não encontrada")
                if not name_exists:
                    print("Criando coluna 'name'...")
                    # Add name column
                    add_query = text("ALTER TABLE users ADD COLUMN name VARCHAR(100)")
                    conn.execute(add_query)
                    conn.commit()
                    print("✓ Coluna 'name' criada")
                    print("⚠ ATENÇÃO: Você precisará preencher os valores de 'name' manualmente")
        
        print("\n" + "=" * 60)
        print("✓ Migração concluída com sucesso!")
        print("=" * 60)
        return True
    
    except Exception as e:
        print(f"\n✗ Erro durante a migração: {e}")
        return False


if __name__ == "__main__":
    migrate_username_to_name()

