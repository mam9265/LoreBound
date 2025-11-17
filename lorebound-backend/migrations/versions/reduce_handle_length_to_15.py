"""reduce handle length to 15

Revision ID: reduce_handle_length_to_15
Revises: add_run_fields
Create Date: 2025-01-27

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision = 'reduce_handle_length_to_15'
down_revision = 'add_run_fields'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Reduce handle column length from 50 to 15 characters."""
    # First, truncate any existing handles that are longer than 15 characters
    op.execute(text("""
        UPDATE profiles 
        SET handle = SUBSTRING(handle, 1, 15)
        WHERE LENGTH(handle) > 15
    """))
    
    # Handle any duplicate handles that may have been created by truncation
    # by appending a short numeric suffix to make them unique
    op.execute(text("""
        WITH numbered_duplicates AS (
            SELECT user_id, handle,
                   ROW_NUMBER() OVER (PARTITION BY handle ORDER BY user_id) as rn
            FROM profiles
            WHERE handle IN (
                SELECT handle FROM profiles 
                GROUP BY handle HAVING COUNT(*) > 1
            )
        )
        UPDATE profiles p
        SET handle = CASE 
            WHEN d.rn = 1 THEN p.handle
            ELSE SUBSTRING(p.handle, 1, 13) || '_' || (d.rn - 1)::text
        END
        FROM numbered_duplicates d
        WHERE p.user_id = d.user_id AND d.rn > 1
    """))
    
    # Now alter the column to reduce its length
    op.alter_column('profiles', 'handle',
                    existing_type=sa.String(length=50),
                    type_=sa.String(length=15),
                    existing_nullable=False)


def downgrade() -> None:
    """Restore handle column length to 50 characters."""
    op.alter_column('profiles', 'handle',
                    existing_type=sa.String(length=15),
                    type_=sa.String(length=50),
                    existing_nullable=False)

