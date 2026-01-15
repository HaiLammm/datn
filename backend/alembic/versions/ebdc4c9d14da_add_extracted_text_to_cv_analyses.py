"""add_extracted_text_to_cv_analyses

Revision ID: ebdc4c9d14da
Revises: 2cbc6f2d2a19
Create Date: 2026-01-15 17:21:55.367644

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ebdc4c9d14da'
down_revision: Union[str, Sequence[str], None] = '2cbc6f2d2a19'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add extracted_text column to cv_analyses table for performance optimization."""
    # Add extracted_text column to store full CV text content
    # This avoids re-extracting text from PDF/DOCX files when creating interviews
    op.add_column('cv_analyses', 
        sa.Column('extracted_text', sa.Text(), nullable=True,
                  comment='Full extracted text from CV file for interview generation'))


def downgrade() -> None:
    """Remove extracted_text column from cv_analyses table."""
    op.drop_column('cv_analyses', 'extracted_text')
