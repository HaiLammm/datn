"""add is_public to cvs

Revision ID: ca9cda281bb7
Revises: f7a3b2c1d4e5
Create Date: 2025-12-18 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ca9cda281bb7'
down_revision: Union[str, Sequence[str], None] = '1d4c0f3930a3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add is_public column to cvs table.
    
    Adds a boolean column to control CV visibility to recruiters.
    Default is False (private) for all existing CVs.
    """
    op.add_column('cvs', sa.Column('is_public', sa.Boolean(), nullable=False, server_default=sa.text('false')))


def downgrade() -> None:
    """Remove is_public column from cvs table."""
    op.drop_column('cvs', 'is_public')
