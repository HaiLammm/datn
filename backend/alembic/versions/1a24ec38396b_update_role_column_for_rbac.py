"""Update role column for RBAC - change default to job_seeker, add constraint and index

Revision ID: 1a24ec38396b
Revises: ca9cda281bb7
Create Date: 2025-12-19 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1a24ec38396b'
down_revision: Union[str, Sequence[str], None] = 'ca9cda281bb7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Update existing 'user' roles to 'job_seeker'
    op.execute("UPDATE users SET role = 'job_seeker' WHERE role = 'user'")
    
    # 2. Change server default from 'user' to 'job_seeker'
    op.alter_column(
        'users',
        'role',
        existing_type=sa.String(),
        server_default='job_seeker',
        existing_nullable=False
    )
    
    # 3. Add CHECK constraint for role values
    op.create_check_constraint(
        'ck_users_role',
        'users',
        "role IN ('job_seeker', 'recruiter', 'admin')"
    )
    
    # 4. Add index for role column for query performance
    op.create_index('idx_users_role', 'users', ['role'])


def downgrade() -> None:
    # Drop index
    op.drop_index('idx_users_role', table_name='users')
    
    # Drop CHECK constraint
    op.drop_constraint('ck_users_role', 'users', type_='check')
    
    # Change server default back to 'user'
    op.alter_column(
        'users',
        'role',
        existing_type=sa.String(),
        server_default='user',
        existing_nullable=False
    )
    
    # Revert 'job_seeker' roles back to 'user'
    op.execute("UPDATE users SET role = 'user' WHERE role = 'job_seeker'")
