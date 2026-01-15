"""
Celery tasks for AI-related operations.

This module contains background tasks for CV analysis processing.
Tasks are executed asynchronously by Celery workers.
"""
import uuid
import logging
from typing import Optional

# Import all models FIRST to ensure SQLAlchemy relationships are resolved
# This is critical for Celery workers which don't run app startup events
from app.modules.users.models import User
from app.modules.jobs.models import JobDescription, Application
from app.modules.cv.models import CV
from app.modules.ai.models import CVAnalysis, AnalysisStatus
from app.modules.interviews.models import (
    InterviewSession,
    InterviewQuestion,
    InterviewTurn,
    InterviewEvaluation,
    AgentCallLog
)

from app.core.celery_app import celery_app
from app.core.database import AsyncSessionLocal
from app.modules.ai.service import AIService

logger = logging.getLogger(__name__)


@celery_app.task(
    name="ai.analyze_cv",
    bind=True,
    max_retries=3,
    default_retry_delay=60,  # Retry after 60 seconds
    soft_time_limit=540,  # 9 minutes soft limit
    time_limit=600,  # 10 minutes hard limit
)
def analyze_cv_task(
    self,
    cv_id: str,
    file_path: str,
    force_ocr: bool = False
) -> dict:
    """
    Celery task to analyze a CV using AI service.
    
    This task is executed asynchronously by Celery workers. It performs
    comprehensive CV analysis including text extraction, skill scoring,
    and quality assessment.
    
    Args:
        self: Celery task instance (bound)
        cv_id: UUID string of the CV record
        file_path: Absolute path to the CV file on disk
        force_ocr: If True, skip text extraction and use OCR directly
        
    Returns:
        dict: Result summary with status and metrics
        
    Raises:
        Exception: If analysis fails after max retries
        
    Example:
        analyze_cv_task.delay(
            cv_id="123e4567-e89b-12d3-a456-426614174000",
            file_path="/uploads/cvs/cv_123.pdf"
        )
    """
    import asyncio
    
    logger.info(
        f"🚀 CELERY TASK STARTED - Task ID: {self.request.id}, "
        f"CV ID: {cv_id}, File: {file_path}, Force OCR: {force_ocr}"
    )
    
    try:
        # Convert cv_id string to UUID
        cv_uuid = uuid.UUID(cv_id)
        
        # Run async analysis in event loop
        result = asyncio.run(_run_analysis(cv_uuid, file_path, force_ocr))
        
        logger.info(
            f"✅ CELERY TASK COMPLETED - Task ID: {self.request.id}, "
            f"CV ID: {cv_id}, Status: {result['status']}"
        )
        
        return result
        
    except Exception as exc:
        logger.error(
            f"❌ CELERY TASK FAILED - Task ID: {self.request.id}, "
            f"CV ID: {cv_id}, Error: {str(exc)}, "
            f"Retry {self.request.retries}/{self.max_retries}"
        )
        
        # Mark as failed in DB before retry
        asyncio.run(_mark_analysis_failed(uuid.UUID(cv_id), str(exc)))
        
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


async def _run_analysis(
    cv_id: uuid.UUID,
    file_path: str,
    force_ocr: bool
) -> dict:
    """
    Internal async function to run CV analysis.
    
    Args:
        cv_id: UUID of the CV
        file_path: Path to CV file
        force_ocr: Whether to force OCR
        
    Returns:
        dict: Analysis result summary
    """
    async with AsyncSessionLocal() as db:
        ai_service = AIService()
        
        try:
            await ai_service.analyze_cv(
                cv_id=cv_id,
                file_path=file_path,
                db=db,
                force_ocr=force_ocr
            )
            
            return {
                "status": "completed",
                "cv_id": str(cv_id),
                "message": "CV analysis completed successfully"
            }
            
        except Exception as e:
            logger.error(f"Analysis failed for CV {cv_id}: {str(e)}")
            raise


async def _mark_analysis_failed(cv_id: uuid.UUID, error_message: str) -> None:
    """
    Mark CV analysis as failed in the database.
    
    Args:
        cv_id: UUID of the CV
        error_message: Error description
    """
    from sqlalchemy import update
    from app.modules.ai.models import CVAnalysis
    
    async with AsyncSessionLocal() as db:
        try:
            await db.execute(
                update(CVAnalysis)
                .where(CVAnalysis.cv_id == cv_id)
                .values(
                    status=AnalysisStatus.FAILED,
                    ai_summary=f"Analysis failed: {error_message}"
                )
            )
            await db.commit()
            logger.info(f"Marked CV {cv_id} analysis as FAILED")
        except Exception as e:
            logger.error(f"Failed to update status for CV {cv_id}: {str(e)}")
            await db.rollback()
