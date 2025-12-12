"""create cv_analyses table

Revision ID: e501602af441
Revises: 6bd05efc9d71
Create Date: 2025-12-11 16:17:00.433121

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e501602af441'
down_revision: Union[str, Sequence[str], None] = '6bd05efc9d71'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'cv_analyses',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('cv_id', sa.UUID(), nullable=False),
        sa.Column('status', sa.String(), nullable=False, server_default='PENDING'),
        sa.Column('ai_score', sa.Integer(), nullable=True),
        sa.Column('ai_summary', sa.Text(), nullable=True),
        sa.Column('ai_feedback', sa.JSON(), nullable=True),
        sa.Column('extracted_skills', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['cv_id'], ['cvs.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_cv_analyses_cv_id', 'cv_analyses', ['cv_id'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('cv_analyses')
