#!/usr/bin/env python3
"""
Migration script to create a trigger that automatically assigns new users to the free plan.

This ensures all new users get the free plan by default if no plan is specified.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import logging

from src.config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_migration():
    """Create trigger to auto-assign free plan to new users."""
    
    # Create engine - use localhost for local execution
    database_url = Config.DATABASE_URL.replace("postgres:5432", "localhost:5432")
    logger.info(f"Connecting to database...")
    engine = create_engine(database_url, echo=True)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        logger.info("Creating trigger to auto-assign free plan to new users...")
        
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
        logger.info("✓ Trigger function created")
        
        # Drop trigger if exists and create new one
        session.execute(text("""
            DROP TRIGGER IF EXISTS trigger_assign_free_plan ON users;
            
            CREATE TRIGGER trigger_assign_free_plan
            BEFORE INSERT ON users
            FOR EACH ROW
            EXECUTE FUNCTION assign_free_plan_to_new_user();
        """))
        session.commit()
        logger.info("✓ Trigger created on users table")
        
        logger.info("✅ Auto-assign free plan trigger created successfully!")
        logger.info("   - New users will automatically be assigned to the free plan")
        logger.info("   - Free plan provides 2,000 tokens per month")
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        session.rollback()
        raise
    finally:
        session.close()
        engine.dispose()


if __name__ == "__main__":
    run_migration()

