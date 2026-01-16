"""add_config_fields_to_interview_sessions_for_sequential_generation

Revision ID: ac7a5ad66388
Revises: ebdc4c9d14da
Create Date: 2026-01-16 10:30:08.747473

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ac7a5ad66388'
down_revision: Union[str, Sequence[str], None] = 'ebdc4c9d14da'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Add configuration fields to interview_sessions for sequential question generation.
    
    These fields cache the interview configuration so we can generate questions on-demand
    without re-querying CV and job data every time.
    """
    # Add CV reference
    op.add_column(
        'interview_sessions',
        sa.Column('cv_id', sa.dialects.postgresql.UUID(as_uuid=True), nullable=True)
    )
    
    # Add job description and title
    op.add_column(
        'interview_sessions',
        sa.Column('job_description', sa.Text(), nullable=True)
    )
    op.add_column(
        'interview_sessions',
        sa.Column('job_title', sa.String(255), nullable=True)
    )
    
    # Add position level
    op.add_column(
        'interview_sessions',
        sa.Column('position_level', sa.String(20), nullable=True)
    )
    
    # Add num_questions with default 10
    op.add_column(
        'interview_sessions',
        sa.Column('num_questions', sa.Integer(), nullable=False, server_default='10')
    )
    
    # Add focus_areas as JSONB array
    op.add_column(
        'interview_sessions',
        sa.Column('focus_areas', sa.dialects.postgresql.JSONB(), nullable=True)
    )


def downgrade() -> None:
    """Remove configuration fields from interview_sessions."""
    op.drop_column('interview_sessions', 'focus_areas')
    op.drop_column('interview_sessions', 'num_questions')
    op.drop_column('interview_sessions', 'position_level')
    op.drop_column('interview_sessions', 'job_title')
    op.drop_column('interview_sessions', 'job_description')
    op.drop_column('interview_sessions', 'cv_id')
