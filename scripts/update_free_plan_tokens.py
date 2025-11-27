#!/usr/bin/env python3
"""
Migration script to update free plan token limit to 10,000 tokens.

This script:
1. Updates the free plan monthly_token_limit to 10000
2. Updates all existing user_token_balances for free plan users (no changes to their usage)
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
    """Run the migration to update free plan token limit."""
    
    # Create engine - use localhost for local execution
    database_url = Config.DATABASE_URL.replace("postgres:5432", "localhost:5432")
    logger.info(f"Connecting to database...")
    engine = create_engine(database_url, echo=True)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        logger.info("Starting free plan token limit update...")
        
        # Step 1: Update free plan token limit
        logger.info("Updating free plan monthly_token_limit to 10000...")
        result = session.execute(text("""
            UPDATE plans 
            SET monthly_token_limit = 10000,
                updated_at = CURRENT_TIMESTAMP
            WHERE name = 'free';
        """))
        session.commit()
        logger.info(f"✓ Free plan updated (affected rows: {result.rowcount})")
        
        # Step 2: Get count of users on free plan
        logger.info("Checking users on free plan...")
        result = session.execute(text("""
            SELECT COUNT(*) as count
            FROM users 
            WHERE plan_id = (SELECT id FROM plans WHERE name = 'free');
        """))
        user_count = result.scalar()
        logger.info(f"✓ {user_count} users are on the free plan")
        
        # Note: We don't modify user_token_balances because:
        # - tokens_used_this_month should remain as is (their actual usage)
        # - The limit check happens dynamically using the plan's monthly_token_limit
        
        logger.info("✅ Free plan token limit update completed successfully!")
        logger.info("   - Free plan limit: 2,000 → 10,000 tokens")
        logger.info(f"   - {user_count} users affected")
        logger.info("   - User token usage history preserved")
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        session.rollback()
        raise
    finally:
        session.close()
        engine.dispose()


if __name__ == "__main__":
    run_migration()

