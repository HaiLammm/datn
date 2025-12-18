"""add_parse_error_to_job_descriptions

Revision ID: 1d4c0f3930a3
Revises: a1b2c3d4e5f6
Create Date: 2025-12-18 09:13:57.389047

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1d4c0f3930a3'
down_revision: Union[str, Sequence[str], None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add parse_error column to job_descriptions table."""
    op.add_column('job_descriptions', sa.Column('parse_error', sa.Text(), nullable=True))


def downgrade() -> None:
    """Remove parse_error column from job_descriptions table."""
    op.drop_column('job_descriptions', 'parse_error')
