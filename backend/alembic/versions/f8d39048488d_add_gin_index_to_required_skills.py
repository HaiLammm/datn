"""add gin index to required_skills

Revision ID: f8d39048488d
Revises: 9a2b1c3d4e5f
Create Date: 2026-01-06 17:31:30.814991

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f8d39048488d'
down_revision: Union[str, Sequence[str], None] = '9a2b1c3d4e5f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_index('idx_job_descriptions_required_skills_gin', 'job_descriptions', ['required_skills'], postgresql_using='gin')


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('idx_job_descriptions_required_skills_gin', table_name='job_descriptions')
