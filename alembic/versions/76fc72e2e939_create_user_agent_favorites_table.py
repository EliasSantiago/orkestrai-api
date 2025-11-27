"""create_user_agent_favorites_table

Revision ID: 76fc72e2e939
Revises: 523dbb60ecfe
Create Date: 2025-11-27 20:40:10.842921

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '76fc72e2e939'
down_revision: Union[str, Sequence[str], None] = '523dbb60ecfe'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create user_agent_favorites table."""
    from sqlalchemy import text
    
    op.execute(text("""
        CREATE TABLE IF NOT EXISTS user_agent_favorites (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            agent_id INTEGER NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT uq_user_agent_favorite UNIQUE (user_id, agent_id)
        )
    """))
    
    # Create indexes for better query performance
    op.execute(text("""
        CREATE INDEX IF NOT EXISTS idx_user_agent_favorites_user_id 
        ON user_agent_favorites(user_id)
    """))
    
    op.execute(text("""
        CREATE INDEX IF NOT EXISTS idx_user_agent_favorites_agent_id 
        ON user_agent_favorites(agent_id)
    """))
    
    op.execute(text("""
        CREATE INDEX IF NOT EXISTS idx_user_agent_favorites_created_at 
        ON user_agent_favorites(created_at)
    """))


def downgrade() -> None:
    """Drop user_agent_favorites table."""
    from sqlalchemy import text
    op.execute(text("DROP TABLE IF EXISTS user_agent_favorites"))
