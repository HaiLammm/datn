"""
Celery tasks for Epic 8: AI Interview Room background processing.

This module contains async tasks for:
- Question generation (long-running AI operation)
- Future: Evaluation generation, transcript processing
"""
import sys
import os
import logging
from typing import Dict, Any
from uuid import UUID

# Add _sub-agents to path
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
project_root = os.path.dirname(backend_dir)
sub_agents_dir = os.path.join(project_root, '_sub-agents')
if sub_agents_dir not in sys.path:
    sys.path.append(sub_agents_dir)

from celery import Task
from app.core.celery_app import celery_app
from app.core.database import AsyncSessionLocal
from sqlalchemy import select, update
from app.modules.interviews.models import InterviewSession, InterviewQuestion, AgentCallLog
from agents.question_generator import QuestionGeneratorAgent
from app.core.config import settings
import time

logger = logging.getLogger(__name__)


class DatabaseTask(Task):
    """Base task with database session management."""
    
    _db_session = None
    
    @property
    def db_session(self):
        if self._db_session is None:
            self._db_session = AsyncSessionLocal()
        return self._db_session
    
    def after_return(self, *args, **kwargs):
        """Close database session after task completes."""
        if self._db_session is not None:
            self._db_session.close()
            self._db_session = None


@celery_app.task(
    bind=True,
    base=DatabaseTask,
    name="app.modules.interviews.tasks.generate_questions_task",
    max_retries=2,  # Retry up to 2 times (3 total attempts)
    default_retry_delay=30,  # 30 seconds between retries
    # Don't auto-retry, we'll handle retry logic manually for better control
    autoretry_for=(),  # Empty tuple instead of None
    acks_late=True,  # Acknowledge task only after completion
    reject_on_worker_lost=True,  # Re-queue if worker crashes
)
def generate_questions_task(
    self,
    session_id: str,
    job_description: str,
    cv_content: str,
    position_level: str,
    num_questions: int = 10,
    focus_areas: list = None
) -> Dict[str, Any]:
    """
    Background task to generate interview questions using AI.
    
    Args:
        session_id: Interview session UUID (as string)
        job_description: Job description text
        cv_content: Candidate CV text
        position_level: junior/middle/senior
        num_questions: Number of questions to generate
        focus_areas: Optional list of focus areas
    
    Returns:
        Dict with status and results
    """
    start_time = time.time()
    session_uuid = UUID(session_id)
    
    try:
        logger.info(f"Starting question generation for session {session_id}")
        
        # Update session status to 'generating'
        import asyncio
        loop = asyncio.get_event_loop()
        
        async def update_status(status: str, error: str = None):
            async with AsyncSessionLocal() as db:
                stmt = update(InterviewSession).where(
                    InterviewSession.id == session_uuid
                ).values(
                    status=status,
                    error_message=error
                )
                await db.execute(stmt)
                await db.commit()
        
        loop.run_until_complete(update_status('generating'))
        
        # Initialize AI agent
        agent = QuestionGeneratorAgent(config_path=settings.QUESTION_AGENT_CONFIG)
        
        # Call AI agent (synchronous)
        result = agent.generate_questions(
            job_description=job_description,
            cv_content=cv_content,
            position_level=position_level,
            num_questions=num_questions,
            focus_areas=focus_areas or []
        )
        
        if result["status"] != "success":
            raise Exception(f"Agent error: {result.get('error')}")
        
        # Store results in database
        async def save_questions():
            async with AsyncSessionLocal() as db:
                try:
                    # Save questions
                    questions_data = []
                    for idx, q_data in enumerate(result["questions"]):
                        question = InterviewQuestion(
                            interview_session_id=session_uuid,
                            question_id=q_data["question_id"],
                            category=q_data["category"],
                            difficulty=q_data["difficulty"],
                            question_text=q_data["question_text"],
                            key_points=q_data.get("key_points"),
                            ideal_answer_outline=q_data.get("ideal_answer_outline"),
                            evaluation_criteria=q_data.get("evaluation_criteria"),
                            order_index=idx,
                            is_selected=True
                        )
                        db.add(question)
                        questions_data.append({
                            "question_id": q_data["question_id"],
                            "category": q_data["category"],
                            "question_text": q_data["question_text"]
                        })
                    
                    # Log agent call
                    latency_ms = int((time.time() - start_time) * 1000)
                    log = AgentCallLog(
                        agent_type="question_generator",
                        interview_session_id=session_uuid,
                        input_data={
                            "position_level": position_level,
                            "num_questions": num_questions,
                            "focus_areas": focus_areas or []
                        },
                        output_data=result.get("metadata", {}),
                        status="success",
                        latency_ms=latency_ms,
                        model_used=agent.model
                    )
                    db.add(log)
                    
                    # Update session status to 'ready'
                    stmt = update(InterviewSession).where(
                        InterviewSession.id == session_uuid
                    ).values(
                        status='ready',
                        error_message=None
                    )
                    await db.execute(stmt)
                    
                    await db.commit()
                    
                    logger.info(f"Successfully generated {len(questions_data)} questions in {latency_ms}ms")
                    return {
                        "status": "success",
                        "session_id": session_id,
                        "questions_count": len(questions_data),
                        "latency_ms": latency_ms
                    }
                    
                except Exception as e:
                    await db.rollback()
                    raise e
        
        return loop.run_until_complete(save_questions())
        
    except Exception as e:
        logger.error(f"Error in question generation task for session {session_id}: {e}", exc_info=True)
        
        # Determine if we should retry
        should_retry = False
        retry_delay = 30
        
        # Retry on specific errors
        error_str = str(e).lower()
        if any(keyword in error_str for keyword in ['timeout', 'connection', 'network', 'unavailable', 'ollama']):
            should_retry = True
            logger.warning(f"Retryable error detected for session {session_id}. Attempt {self.request.retries + 1}")
        
        # Update session status to 'error'
        async def log_error():
            async with AsyncSessionLocal() as db:
                # Log error to agent_call_logs
                latency_ms = int((time.time() - start_time) * 1000)
                log = AgentCallLog(
                    agent_type="question_generator",
                    interview_session_id=session_uuid,
                    input_data={
                        "position_level": position_level,
                        "num_questions": num_questions
                    },
                    status="error",
                    error_message=str(e),
                    latency_ms=latency_ms
                )
                db.add(log)
                
                # Update session status (only if not retrying)
                if not should_retry or self.request.retries >= self.max_retries:
                    stmt = update(InterviewSession).where(
                        InterviewSession.id == session_uuid
                    ).values(
                        status='error',
                        error_message=f"Failed after {self.request.retries + 1} attempts: {str(e)}"
                    )
                    await db.execute(stmt)
                
                await db.commit()
        
        loop.run_until_complete(log_error())
        
        # Retry if appropriate
        if should_retry and self.request.retries < self.max_retries:
            # Exponential backoff: 30s, 60s, 120s
            retry_delay = 30 * (2 ** self.request.retries)
            logger.info(f"Retrying task in {retry_delay} seconds...")
            raise self.retry(exc=e, countdown=retry_delay)
        
        return {
            "status": "error",
            "session_id": session_id,
            "error": str(e),
            "attempts": self.request.retries + 1
        }
