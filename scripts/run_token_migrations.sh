#!/bin/bash
# Script para executar migrations Python específicas do sistema de tokens
# Este script é idempotente e pode ser executado múltiplas vezes com segurança

set -e

echo "🔐 Migrations do Sistema de Tokens"
echo "===================================="
echo ""

# Cores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Garantir que PYTHONPATH está configurado
export PYTHONPATH=/app:${PYTHONPATH:-}

echo "1️⃣ Verificando tabela de controle de migrations Python..."
echo "-----------------------------------------------------------"

# Criar tabela de controle para migrations Python
python3 << 'EOF'
import sys
sys.path.insert(0, '/app')

from src.database import engine
from sqlalchemy import text

try:
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS python_migrations (
                id SERIAL PRIMARY KEY,
                migration_name VARCHAR(255) UNIQUE NOT NULL,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                success BOOLEAN DEFAULT TRUE,
                error_message TEXT
            )
        """))
        conn.commit()
    print("✓ Tabela de controle criada/verificada")
except Exception as e:
    print(f"✗ Erro ao criar tabela de controle: {e}")
    sys.exit(1)
EOF

if [ $? -ne 0 ]; then
    echo -e "${RED}✗ Erro ao criar tabela de controle${NC}"
    exit 1
fi

echo ""
echo "2️⃣ Aplicando migration: create_token_system_tables.py"
echo "-----------------------------------------------------------"

# Verificar se migration já foi aplicada
ALREADY_APPLIED=$(python3 << 'EOF'
import sys
sys.path.insert(0, '/app')

from src.database import engine
from sqlalchemy import text

try:
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT COUNT(*) FROM python_migrations 
            WHERE migration_name = 'create_token_system_tables' AND success = TRUE
        """))
        count = result.scalar()
        print(count)
except Exception as e:
    print(0)
EOF
)

if [ "$ALREADY_APPLIED" = "1" ]; then
    echo -e "${YELLOW}⊘ Já aplicada (pulando)${NC}"
else
    # Executar migration
    python3 << 'EOF'
import sys
sys.path.insert(0, '/app')

from src.database import engine
from sqlalchemy import text, create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from src.config import Config
from src.models import Plan, User, UserTokenBalance

def run_migration():
    """Run the migration to create token system tables."""
    
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Step 1: Create plans table
        session.execute(text("""
            CREATE TABLE IF NOT EXISTS plans (
                id SERIAL PRIMARY KEY,
                name VARCHAR(50) UNIQUE NOT NULL,
                description TEXT,
                price_month NUMERIC(10, 2) NOT NULL DEFAULT 0.0,
                price_year NUMERIC(10, 2) NOT NULL DEFAULT 0.0,
                monthly_token_limit BIGINT NOT NULL,
                is_active BOOLEAN NOT NULL DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE INDEX IF NOT EXISTS ix_plans_name ON plans(name);
        """))
        session.commit()
        
        # Step 2: Insert default plans with updated token limits
        session.execute(text("""
            INSERT INTO plans (name, description, price_month, price_year, monthly_token_limit, is_active)
            VALUES 
                ('free', 'Plano gratuito com limite básico de tokens', 0.00, 0.00, 2000, true),
                ('pro', 'Plano profissional com limite expandido de tokens', 29.90, 299.00, 1000000, true),
                ('plus', 'Plano premium com alto limite de tokens', 99.90, 999.00, 9000000, true)
            ON CONFLICT (name) DO UPDATE SET
                description = EXCLUDED.description,
                price_month = EXCLUDED.price_month,
                price_year = EXCLUDED.price_year,
                monthly_token_limit = EXCLUDED.monthly_token_limit,
                is_active = EXCLUDED.is_active,
                updated_at = CURRENT_TIMESTAMP;
        """))
        session.commit()
        
        # Step 3: Add plan_id column to users table
        session.execute(text("""
            DO $$ 
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name = 'users' AND column_name = 'plan_id'
                ) THEN
                    ALTER TABLE users ADD COLUMN plan_id INTEGER REFERENCES plans(id) ON DELETE SET NULL;
                    CREATE INDEX IF NOT EXISTS ix_users_plan_id ON users(plan_id);
                END IF;
            END $$;
        """))
        session.commit()
        
        # Step 4: Assign all existing users to free plan
        session.execute(text("""
            UPDATE users 
            SET plan_id = (SELECT id FROM plans WHERE name = 'free' LIMIT 1)
            WHERE plan_id IS NULL;
        """))
        session.commit()
        
        # Step 5: Create user_token_balances table
        session.execute(text("""
            CREATE TABLE IF NOT EXISTS user_token_balances (
                id SERIAL PRIMARY KEY,
                user_id INTEGER UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                tokens_used_this_month BIGINT NOT NULL DEFAULT 0,
                month INTEGER NOT NULL,
                year INTEGER NOT NULL,
                last_reset_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE INDEX IF NOT EXISTS ix_user_token_balances_user_id ON user_token_balances(user_id);
            CREATE INDEX IF NOT EXISTS ix_user_token_balances_month ON user_token_balances(month);
            CREATE INDEX IF NOT EXISTS ix_user_token_balances_year ON user_token_balances(year);
        """))
        session.commit()
        
        # Step 6: Create token_usage_history table
        session.execute(text("""
            CREATE TABLE IF NOT EXISTS token_usage_history (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                model VARCHAR(100) NOT NULL,
                endpoint VARCHAR(255),
                session_id VARCHAR(100),
                prompt_tokens INTEGER NOT NULL DEFAULT 0,
                completion_tokens INTEGER NOT NULL DEFAULT 0,
                total_tokens INTEGER NOT NULL DEFAULT 0,
                cost_usd NUMERIC(10, 6),
                request_metadata JSON,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE INDEX IF NOT EXISTS ix_token_usage_history_user_id ON token_usage_history(user_id);
            CREATE INDEX IF NOT EXISTS ix_token_usage_history_session_id ON token_usage_history(session_id);
            CREATE INDEX IF NOT EXISTS ix_token_usage_history_created_at ON token_usage_history(created_at);
        """))
        session.commit()
        
        # Step 7: Create initial token balance records for existing users
        now = datetime.utcnow()
        current_month = now.month
        current_year = now.year
        
        session.execute(text("""
            INSERT INTO user_token_balances (user_id, tokens_used_this_month, month, year)
            SELECT id, 0, :month, :year
            FROM users
            WHERE id NOT IN (SELECT user_id FROM user_token_balances)
            ON CONFLICT (user_id) DO NOTHING;
        """), {"month": current_month, "year": current_year})
        session.commit()
        
        # Registrar migration como sucesso
        session.execute(text("""
            INSERT INTO python_migrations (migration_name, success)
            VALUES ('create_token_system_tables', TRUE)
            ON CONFLICT (migration_name) DO NOTHING;
        """))
        session.commit()
        
        print("✓ Token system tables created successfully")
        
    except Exception as e:
        session.rollback()
        # Registrar erro
        try:
            session.execute(text("""
                INSERT INTO python_migrations (migration_name, success, error_message)
                VALUES ('create_token_system_tables', FALSE, :error)
                ON CONFLICT (migration_name) DO UPDATE SET
                    success = FALSE,
                    error_message = :error,
                    applied_at = CURRENT_TIMESTAMP;
            """), {"error": str(e)})
            session.commit()
        except:
            pass
        raise e
    finally:
        session.close()

if __name__ == "__main__":
    try:
        run_migration()
    except Exception as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        sys.exit(1)
EOF

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Aplicada com sucesso${NC}"
    else
        echo -e "${RED}✗ Erro ao aplicar migration${NC}"
        exit 1
    fi
fi

echo ""
echo "3️⃣ Aplicando migration: add_auto_assign_free_plan_trigger.py"
echo "-----------------------------------------------------------"

# Verificar se migration já foi aplicada
ALREADY_APPLIED=$(python3 << 'EOF'
import sys
sys.path.insert(0, '/app')

from src.database import engine
from sqlalchemy import text

try:
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT COUNT(*) FROM python_migrations 
            WHERE migration_name = 'add_auto_assign_free_plan_trigger' AND success = TRUE
        """))
        count = result.scalar()
        print(count)
except Exception as e:
    print(0)
EOF
)

if [ "$ALREADY_APPLIED" = "1" ]; then
    echo -e "${YELLOW}⊘ Já aplicada (pulando)${NC}"
else
    # Executar migration
    python3 << 'EOF'
import sys
sys.path.insert(0, '/app')

from src.database import engine
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker

def run_migration():
    """Create trigger to auto-assign free plan to new users."""
    
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Create the trigger function
        session.execute(text("""
            CREATE OR REPLACE FUNCTION assign_free_plan_to_new_user()
            RETURNS TRIGGER AS $$
            BEGIN
                -- If plan_id is NULL, assign the free plan
                IF NEW.plan_id IS NULL THEN
                    NEW.plan_id := (SELECT id FROM plans WHERE name = 'free' LIMIT 1);
                END IF;
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;
        """))
        session.commit()
        
        # Drop trigger if exists and create new one
        session.execute(text("""
            DROP TRIGGER IF EXISTS trigger_assign_free_plan ON users;
            
            CREATE TRIGGER trigger_assign_free_plan
            BEFORE INSERT ON users
            FOR EACH ROW
            EXECUTE FUNCTION assign_free_plan_to_new_user();
        """))
        session.commit()
        
        # Registrar migration como sucesso
        session.execute(text("""
            INSERT INTO python_migrations (migration_name, success)
            VALUES ('add_auto_assign_free_plan_trigger', TRUE)
            ON CONFLICT (migration_name) DO NOTHING;
        """))
        session.commit()
        
        print("✓ Auto-assign free plan trigger created successfully")
        
    except Exception as e:
        session.rollback()
        # Registrar erro
        try:
            session.execute(text("""
                INSERT INTO python_migrations (migration_name, success, error_message)
                VALUES ('add_auto_assign_free_plan_trigger', FALSE, :error)
                ON CONFLICT (migration_name) DO UPDATE SET
                    success = FALSE,
                    error_message = :error,
                    applied_at = CURRENT_TIMESTAMP;
            """), {"error": str(e)})
            session.commit()
        except:
            pass
        raise e
    finally:
        session.close()

if __name__ == "__main__":
    try:
        run_migration()
    except Exception as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        sys.exit(1)
EOF

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Aplicada com sucesso${NC}"
    else
        echo -e "${RED}✗ Erro ao aplicar migration${NC}"
        exit 1
    fi
fi

echo ""
echo "===================================="
echo -e "${GREEN}✅ Todas as migrations Python aplicadas!${NC}"
echo "===================================="

