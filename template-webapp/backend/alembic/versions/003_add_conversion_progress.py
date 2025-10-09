"""add conversion progress tracking

Revision ID: 003
Revises: 002
Create Date: 2025-10-08 23:57:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add progress tracking columns to scl_files
    op.add_column('scl_files', sa.Column('conversion_stage', sa.String(length=50), nullable=True))
    op.add_column('scl_files', sa.Column('progress_percent', sa.Integer(), nullable=True, server_default='0'))
    op.add_column('scl_files', sa.Column('stage_message', sa.String(length=255), nullable=True))
    op.add_column('scl_files', sa.Column('estimated_minutes', sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column('scl_files', 'estimated_minutes')
    op.drop_column('scl_files', 'stage_message')
    op.drop_column('scl_files', 'progress_percent')
    op.drop_column('scl_files', 'conversion_stage')
