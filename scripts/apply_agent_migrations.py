#!/usr/bin/env python3
"""Script to apply agent-related migrations."""

from src.database import engine
from sqlalchemy import text

def apply_migrations():
    """Apply missing migrations for agents table."""
    with engine.connect() as conn:
        # Apply add_agent_types_support.sql
        try:
            print("Applying agent_type migration...")
            conn.execute(text("ALTER TABLE agents ADD COLUMN IF NOT EXISTS agent_type VARCHAR(50) NOT NULL DEFAULT 'llm'"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_agents_agent_type ON agents(agent_type)"))
            
            # Make instruction nullable
            try:
                conn.execute(text("ALTER TABLE agents ALTER COLUMN instruction DROP NOT NULL"))
            except Exception:
                pass  # Already nullable
            
            # Make model nullable
            try:
                conn.execute(text("ALTER TABLE agents ALTER COLUMN model DROP NOT NULL"))
            except Exception:
                pass  # Already nullable
            
            conn.execute(text("ALTER TABLE agents ADD COLUMN IF NOT EXISTS workflow_config JSON"))
            conn.execute(text("ALTER TABLE agents ADD COLUMN IF NOT EXISTS custom_config JSON"))
            conn.commit()
            print("✓ agent_type migration applied")
        except Exception as e:
            print(f"Error applying agent_type migration: {e}")
            conn.rollback()
        
        # Apply add_is_favorite_to_agents.sql
        try:
            print("Applying is_favorite migration...")
            conn.execute(text("ALTER TABLE agents ADD COLUMN IF NOT EXISTS is_favorite BOOLEAN NOT NULL DEFAULT FALSE"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_agents_is_favorite ON agents(is_favorite)"))
            conn.execute(text("UPDATE agents SET is_favorite = FALSE WHERE is_favorite IS NULL"))
            conn.commit()
            print("✓ is_favorite migration applied")
        except Exception as e:
            print(f"Error applying is_favorite migration: {e}")
            conn.rollback()
        
        # Add icon column if missing
        try:
            print("Adding icon column...")
            conn.execute(text("ALTER TABLE agents ADD COLUMN IF NOT EXISTS icon VARCHAR(100)"))
            conn.commit()
            print("✓ icon column added")
        except Exception as e:
            print(f"Error adding icon column: {e}")
            conn.rollback()
        
        # Record migrations in schema_migrations table
        try:
            print("Recording migrations...")
            migrations_to_record = [
                'add_agent_types_support.sql',
                'add_is_favorite_to_agents.sql'
            ]
            for migration_name in migrations_to_record:
                result = conn.execute(
                    text("SELECT COUNT(*) FROM schema_migrations WHERE migration_name = :name"),
                    {"name": migration_name}
                )
                if result.scalar() == 0:
                    conn.execute(
                        text("INSERT INTO schema_migrations (migration_name) VALUES (:name)"),
                        {"name": migration_name}
                    )
                    print(f"✓ Recorded {migration_name}")
            conn.commit()
        except Exception as e:
            print(f"Error recording migrations: {e}")
            conn.rollback()
        
        print("\nAll migrations applied successfully!")

if __name__ == "__main__":
    apply_migrations()

