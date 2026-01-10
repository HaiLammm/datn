"""add_interview_tables_for_epic8

Revision ID: 2141c520a6bc
Revises: c2b9997dde66
Create Date: 2026-01-07 17:39:34.820177

Epic 8: Virtual AI Interview Room
Adds tables for AI interview sessions, questions, turns, evaluations, and agent logs.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '2141c520a6bc'
down_revision: Union[str, Sequence[str], None] = 'c2b9997dde66'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - Create interview tables for Epic 8."""
    
    # Create interview_sessions table
    op.create_table(
        'interview_sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('job_posting_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('candidate_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='pending'),
        sa.Column('scheduled_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('started_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('completed_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('duration_minutes', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['candidate_id'], ['users.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_interview_sessions_candidate_id', 'interview_sessions', ['candidate_id'])
    op.create_index('ix_interview_sessions_status', 'interview_sessions', ['status'])
    
    # Create interview_questions table
    op.create_table(
        'interview_questions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('interview_session_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('question_id', sa.String(50), nullable=False),
        sa.Column('category', sa.String(20), nullable=False),
        sa.Column('difficulty', sa.String(20), nullable=False),
        sa.Column('question_text', sa.Text(), nullable=False),
        sa.Column('key_points', postgresql.JSONB(), nullable=True),
        sa.Column('ideal_answer_outline', sa.Text(), nullable=True),
        sa.Column('evaluation_criteria', postgresql.JSONB(), nullable=True),
        sa.Column('order_index', sa.Integer(), nullable=False),
        sa.Column('is_selected', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['interview_session_id'], ['interview_sessions.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_interview_questions_session_id', 'interview_questions', ['interview_session_id'])
    
    # Create interview_turns table
    op.create_table(
        'interview_turns',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('interview_session_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('question_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('turn_number', sa.Integer(), nullable=False),
        sa.Column('ai_message', sa.Text(), nullable=False),
        sa.Column('candidate_message', sa.Text(), nullable=False),
        sa.Column('answer_quality', postgresql.JSONB(), nullable=True),
        sa.Column('key_observations', postgresql.JSONB(), nullable=True),
        sa.Column('strengths', postgresql.JSONB(), nullable=True),
        sa.Column('gaps', postgresql.JSONB(), nullable=True),
        sa.Column('action_type', sa.String(20), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['interview_session_id'], ['interview_sessions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['question_id'], ['interview_questions.id'], ondelete='SET NULL'),
    )
    op.create_index('ix_interview_turns_session_id', 'interview_turns', ['interview_session_id'])
    op.create_index('ix_interview_turns_session_turn', 'interview_turns', ['interview_session_id', 'turn_number'])
    
    # Create interview_evaluations table
    op.create_table(
        'interview_evaluations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('interview_session_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('final_score', sa.Numeric(3, 1), nullable=False),
        sa.Column('grade', sa.String(20), nullable=False),
        sa.Column('hiring_recommendation', sa.String(20), nullable=False),
        sa.Column('dimension_scores', postgresql.JSONB(), nullable=False),
        sa.Column('detailed_analysis', postgresql.JSONB(), nullable=False),
        sa.Column('recommendations', postgresql.JSONB(), nullable=False),
        sa.Column('evaluation_metadata', postgresql.JSONB(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['interview_session_id'], ['interview_sessions.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_interview_evaluations_session_id', 'interview_evaluations', ['interview_session_id'])
    
    # Create agent_call_logs table
    op.create_table(
        'agent_call_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('agent_type', sa.String(50), nullable=False),
        sa.Column('interview_session_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('input_data', postgresql.JSONB(), nullable=True),
        sa.Column('output_data', postgresql.JSONB(), nullable=True),
        sa.Column('status', sa.String(20), nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('latency_ms', sa.Integer(), nullable=True),
        sa.Column('model_used', sa.String(100), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['interview_session_id'], ['interview_sessions.id'], ondelete='SET NULL'),
    )
    op.create_index('ix_agent_call_logs_session_id', 'agent_call_logs', ['interview_session_id'])
    op.create_index('ix_agent_call_logs_created_at', 'agent_call_logs', ['created_at'])


def downgrade() -> None:
    """Downgrade schema - Drop interview tables."""
    op.drop_table('agent_call_logs')
    op.drop_table('interview_evaluations')
    op.drop_table('interview_turns')
    op.drop_table('interview_questions')
    op.drop_table('interview_sessions')
