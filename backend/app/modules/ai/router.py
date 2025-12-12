from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.database import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.users.models import User
from app.modules.cv.models import CV
from . import models, schemas

router = APIRouter(tags=["AI Analysis"])


@router.get("/cvs/{cv_id}/analysis", response_model=schemas.AnalysisResult)
async def get_cv_analysis(
    *,
    cv_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get the AI analysis results for a specific CV.
    """
    # Verify CV ownership
    result = await db.execute(
        select(CV).where(
            CV.id == cv_id,
            CV.user_id == current_user.id
        )
    )
    cv = result.scalar_one_or_none()
    if not cv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="CV not found or access denied"
        )

    # Get analysis result
    result = await db.execute(
        select(models.CVAnalysis).where(models.CVAnalysis.cv_id == cv_id)
    )
    analysis = result.scalar_one_or_none()
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found"
        )

    return analysis


@router.get("/cvs/{cv_id}/status", response_model=schemas.AnalysisStatus)
async def get_cv_analysis_status(
    *,
    cv_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get the current analysis status for a specific CV.
    """
    # Verify CV ownership
    result = await db.execute(
        select(CV).where(
            CV.id == cv_id,
            CV.user_id == current_user.id
        )
    )
    cv = result.scalar_one_or_none()
    if not cv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="CV not found or access denied"
        )

    # Get analysis status
    result = await db.execute(
        select(models.CVAnalysis.status).where(models.CVAnalysis.cv_id == cv_id)
    )
    status_result = result.scalar_one_or_none()

    if not status_result:
        return schemas.AnalysisStatus(status="PENDING", message="Analysis not started")

    # Handle both enum and string status values
    status_value = status_result.value if hasattr(status_result, 'value') else str(status_result)
    return schemas.AnalysisStatus(status=status_value)