#!/usr/bin/env python3
"""
Migration script to create token system tables and populate initial data.

This script:
1. Creates the plans table with free, pro, and plus plans
2. Adds plan_id column to users table
3. Creates user_token_balances table
4. Creates token_usage_history table
5. Assigns all existing users to the free plan
6. Creates initial token balance records for existing users
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import logging

from src.config import Config
from src.database import Base
from src.models import Plan, User, UserTokenBalance

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_migration():
    """Run the migration to create token system tables."""
    
    # Create engine
    engine = create_engine(Config.DATABASE_URL, echo=True)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        logger.info("Starting token system migration...")
        
        # Step 1: Create plans table
        logger.info("Creating plans table...")
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
        logger.info("✓ Plans table created")
        
        # Step 2: Insert default plans
        logger.info("Inserting default plans...")
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
        logger.info("✓ Default plans inserted")
        
        # Step 3: Add plan_id column to users table
        logger.info("Adding plan_id column to users table...")
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
        logger.info("✓ plan_id column added to users table")
        
        # Step 4: Assign all existing users to free plan
        logger.info("Assigning existing users to free plan...")
        result = session.execute(text("""
            UPDATE users 
            SET plan_id = (SELECT id FROM plans WHERE name = 'free' LIMIT 1)
            WHERE plan_id IS NULL;
        """))
        session.commit()
        logger.info(f"✓ {result.rowcount} users assigned to free plan")
        
        # Step 5: Create user_token_balances table
        logger.info("Creating user_token_balances table...")
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
        logger.info("✓ user_token_balances table created")
        
        # Step 6: Create token_usage_history table
        logger.info("Creating token_usage_history table...")
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
        logger.info("✓ token_usage_history table created")
        
        # Step 7: Create initial token balance records for existing users
        logger.info("Creating initial token balance records...")
        now = datetime.utcnow()
        current_month = now.month
        current_year = now.year
        
        result = session.execute(text("""
            INSERT INTO user_token_balances (user_id, tokens_used_this_month, month, year)
            SELECT id, 0, :month, :year
            FROM users
            WHERE id NOT IN (SELECT user_id FROM user_token_balances)
            ON CONFLICT (user_id) DO NOTHING;
        """), {"month": current_month, "year": current_year})
        session.commit()
        logger.info(f"✓ {result.rowcount} token balance records created")
        
        logger.info("✅ Token system migration completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        session.rollback()
        raise
    finally:
        session.close()
        engine.dispose()


if __name__ == "__main__":
    run_migration()

