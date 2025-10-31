"""add run fields for gameplay

Revision ID: add_run_fields
Revises: 326c0b57e543
Create Date: 2025-10-26

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_run_fields'
down_revision = '326c0b57e543'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add new columns to runs table
    op.add_column('runs', sa.Column('floor', sa.Integer(), nullable=False, server_default='1'))
    op.add_column('runs', sa.Column('status', sa.String(length=20), nullable=False, server_default='in_progress'))
    op.add_column('runs', sa.Column('session_token', sa.Text(), nullable=True))
    op.add_column('runs', sa.Column('total_score', sa.Integer(), nullable=True))
    
    # Add index on status
    op.create_index('idx_runs_status', 'runs', ['status'], unique=False)
    
    # Remove server defaults after initial data migration
    op.alter_column('runs', 'floor', server_default=None)
    op.alter_column('runs', 'status', server_default=None)


def downgrade() -> None:
    # Drop index
    op.drop_index('idx_runs_status', table_name='runs')
    
    # Drop columns
    op.drop_column('runs', 'total_score')
    op.drop_column('runs', 'session_token')
    op.drop_column('runs', 'status')
    op.drop_column('runs', 'floor')

