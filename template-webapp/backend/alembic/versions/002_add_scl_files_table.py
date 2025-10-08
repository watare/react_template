"""add scl_files table

Revision ID: 002
Revises: 001
Create Date: 2025-10-08 18:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create scl_files table
    op.create_table(
        'scl_files',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('filename', sa.String(length=255), nullable=False),
        sa.Column('original_filename', sa.String(length=255), nullable=False),
        sa.Column('file_size', sa.BigInteger(), nullable=False),
        sa.Column('scl_path', sa.String(length=512), nullable=False),
        sa.Column('rdf_path', sa.String(length=512), nullable=True),
        sa.Column('validated_scl_path', sa.String(length=512), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='uploaded'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('is_validated', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('validation_passed', sa.Boolean(), nullable=True),
        sa.Column('validation_message', sa.Text(), nullable=True),
        sa.Column('triple_count', sa.Integer(), nullable=True),
        sa.Column('fuseki_dataset', sa.String(length=255), nullable=True),
        sa.Column('uploaded_by', sa.Integer(), nullable=False),
        sa.Column('uploaded_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('converted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['uploaded_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_scl_files_filename'), 'scl_files', ['filename'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_scl_files_filename'), table_name='scl_files')
    op.drop_table('scl_files')
