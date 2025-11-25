"""Add is_public column to agents table."""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import text
from src.database import SessionLocal, engine

def main():
    """Add is_public column to agents table."""
    db = SessionLocal()
    
    try:
        print("🔧 Adding is_public column to agents table...")
        
        # Check if column already exists
        result = db.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='agents' AND column_name='is_public'
        """))
        
        if result.fetchone():
            print("✅ Column is_public already exists")
            return
        
        # Add column
        db.execute(text("""
            ALTER TABLE agents 
            ADD COLUMN is_public BOOLEAN NOT NULL DEFAULT FALSE
        """))
        
        db.commit()
        print("✅ Successfully added is_public column to agents table")
        print("ℹ️  Default value: FALSE (all existing agents are private)")
        
    except Exception as e:
        print(f"❌ Error adding column: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()

