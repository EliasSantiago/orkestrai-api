"""update_free_plan_tokens_to_10000

Revision ID: 523dbb60ecfe
Revises: 
Create Date: 2025-11-27 19:32:28.507463

Updates the free plan monthly_token_limit from 2,000 to 10,000 tokens.
This migration also ensures the free plan exists and creates it if necessary.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision: str = '523dbb60ecfe'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Update free plan token limit to 10,000 tokens.
    Also ensures the free plan exists and creates it if necessary.
    """
    # Ensure plans table exists (should already exist, but safe check)
    op.execute(text("""
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
        )
    """))
    
    # Create index if it doesn't exist
    op.execute(text("""
        CREATE INDEX IF NOT EXISTS ix_plans_name ON plans(name)
    """))
    
    # Insert or update free plan with 10,000 tokens
    op.execute(text("""
        INSERT INTO plans (name, description, price_month, price_year, monthly_token_limit, is_active)
        VALUES ('free', 'Plano gratuito com limite básico de tokens', 0.00, 0.00, 10000, true)
        ON CONFLICT (name) DO UPDATE SET
            monthly_token_limit = 10000,
            updated_at = CURRENT_TIMESTAMP
    """))


def downgrade() -> None:
    """
    Revert free plan token limit back to 2,000 tokens.
    """
    op.execute(text("""
        UPDATE plans 
        SET monthly_token_limit = 2000,
            updated_at = CURRENT_TIMESTAMP
        WHERE name = 'free'
    """))
