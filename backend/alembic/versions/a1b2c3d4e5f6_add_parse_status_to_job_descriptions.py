"""add_parse_status_to_job_descriptions

Revision ID: a1b2c3d4e5f6
Revises: 609a832b1945
Create Date: 2025-12-18 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '609a832b1945'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add parse_status column to job_descriptions table."""
    # Add parse_status column with default value 'pending'
    op.add_column(
        'job_descriptions',
        sa.Column('parse_status', sa.String(length=20), nullable=False, server_default='pending')
    )
    
    # Create index on parse_status for efficient filtering
    op.create_index(
        'ix_job_descriptions_parse_status',
        'job_descriptions',
        ['parse_status'],
        unique=False
    )
    
    # Add check constraint for valid parse_status values
    op.create_check_constraint(
        'check_parse_status',
        'job_descriptions',
        "parse_status IN ('pending', 'processing', 'completed', 'failed')"
    )


def downgrade() -> None:
    """Remove parse_status column from job_descriptions table."""
    # Drop check constraint
    op.drop_constraint('check_parse_status', 'job_descriptions', type_='check')
    
    # Drop index
    op.drop_index('ix_job_descriptions_parse_status', table_name='job_descriptions')
    
    # Drop column
    op.drop_column('job_descriptions', 'parse_status')
