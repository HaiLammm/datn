"""add_job_type_to_job_descriptions

Revision ID: 9a2b1c3d4e5f
Revises: 237e5b73c96b
Create Date: 2026-01-06 17:14:00.000000

Story 9.2.1: Add job_type column for employment type filtering
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '9a2b1c3d4e5f'
down_revision: Union[str, Sequence[str], None] = '237e5b73c96b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add job_type column and index to job_descriptions table."""
    # Add job_type column with check constraint
    op.add_column(
        'job_descriptions',
        sa.Column('job_type', sa.String(length=50), nullable=True)
    )
    
    # Add check constraint for job_type values
    op.create_check_constraint(
        'check_job_type',
        'job_descriptions',
        "job_type IN ('full-time', 'part-time', 'contract', 'internship', 'freelance') OR job_type IS NULL"
    )
    
    # Add index for job_type filtering performance
    op.create_index(
        'idx_job_descriptions_job_type',
        'job_descriptions',
        ['job_type'],
        unique=False
    )
    
    # Add composite index for salary range queries (if not exists)
    # Note: salary_min and salary_max already exist in the table
    op.create_index(
        'idx_job_descriptions_salary',
        'job_descriptions',
        ['salary_min', 'salary_max'],
        unique=False,
        postgresql_where=sa.text('salary_min IS NOT NULL OR salary_max IS NOT NULL')
    )


def downgrade() -> None:
    """Remove job_type column and indexes from job_descriptions table."""
    # Drop indexes first
    op.drop_index('idx_job_descriptions_salary', table_name='job_descriptions')
    op.drop_index('idx_job_descriptions_job_type', table_name='job_descriptions')
    
    # Drop check constraint
    op.drop_constraint('check_job_type', 'job_descriptions', type_='check')
    
    # Drop column
    op.drop_column('job_descriptions', 'job_type')
