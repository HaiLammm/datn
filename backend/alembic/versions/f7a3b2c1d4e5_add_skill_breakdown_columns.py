"""add skill breakdown columns

Revision ID: f7a3b2c1d4e5
Revises: e501602af441
Create Date: 2025-12-16 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers, used by Alembic.
revision: str = 'f7a3b2c1d4e5'
down_revision: Union[str, Sequence[str], None] = 'e501602af441'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add skill breakdown columns to cv_analyses table.
    
    Adds three new JSONB columns for storing hybrid skill scoring data:
    - skill_breakdown: Stores scoring breakdown (completeness, categorization, etc.)
    - skill_categories: Stores categorized skills by type
    - skill_recommendations: Stores improvement recommendations
    """
    op.add_column('cv_analyses', sa.Column('skill_breakdown', JSONB(), nullable=True))
    op.add_column('cv_analyses', sa.Column('skill_categories', JSONB(), nullable=True))
    op.add_column('cv_analyses', sa.Column('skill_recommendations', JSONB(), nullable=True))


def downgrade() -> None:
    """Remove skill breakdown columns from cv_analyses table."""
    op.drop_column('cv_analyses', 'skill_recommendations')
    op.drop_column('cv_analyses', 'skill_categories')
    op.drop_column('cv_analyses', 'skill_breakdown')
