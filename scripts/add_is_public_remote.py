"""Add is_public column to agents table via HTTP."""
import sys
import requests

# Login
response = requests.post(
    'http://localhost:8001/api/auth/login',
    json={'email': 'ignitor.online@gmail.com', 'password': '12040812'},
    timeout=10
)
token = response.json()['access_token']

print("🔧 Executing SQL to add is_public column...")

# Try to create the column via SQL
try:
    from sqlalchemy import create_engine, text
    
    # Get database URL from backend
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from src.config import Config
    
    engine = create_engine(Config.DATABASE_URL)
    with engine.connect() as conn:
        # Check if column exists
        result = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='agents' AND column_name='is_public'
        """))
        
        if result.fetchone():
            print("✅ Column is_public already exists")
        else:
            # Add column
            conn.execute(text("""
                ALTER TABLE agents 
                ADD COLUMN is_public BOOLEAN NOT NULL DEFAULT FALSE
            """))
            conn.commit()
            print("✅ Successfully added is_public column to agents table")
            
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)

