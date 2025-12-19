import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.database import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.users.models import User
from app.modules.cv.models import CV
from . import models, schemas

logger = logging.getLogger(__name__)

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

    logger.info(f"📊 ANALYSIS REQUEST - CV ID: {cv_id}, User: {current_user.email}")
    logger.info(f"📊 Score: {analysis.ai_score}")
    if analysis.ai_feedback:
        exp_score = analysis.ai_feedback.get('criteria', {}).get('experience', 'N/A')
        exp_years = analysis.ai_feedback.get('experience_breakdown', {}).get('total_years', 'N/A')
        logger.info(f"📊 Experience Score: {exp_score}, Years: {exp_years}")

    # Build response with cv_filename
    return schemas.AnalysisResult(
        id=analysis.id,
        cv_id=analysis.cv_id,
        status=analysis.status.value if hasattr(analysis.status, 'value') else str(analysis.status),
        ai_score=analysis.ai_score,
        ai_summary=analysis.ai_summary,
        ai_feedback=analysis.ai_feedback,
        extracted_skills=analysis.extracted_skills,
        cv_filename=cv.filename,
        skill_breakdown=analysis.skill_breakdown,
        skill_categories=analysis.skill_categories,
        skill_recommendations=analysis.skill_recommendations,
        created_at=analysis.created_at,
        updated_at=analysis.updated_at
    )


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


@router.post("/cvs/{cv_id}/match", response_model=schemas.SkillMatchResponse)
async def match_cv_with_jd(
    *,
    cv_id: str,
    request: schemas.SkillMatchRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Match CV skills against job description requirements.
    
    This endpoint compares the skills extracted from a CV against the
    requirements in a job description, calculating match rate and
    identifying skill gaps.
    
    Args:
        cv_id: UUID of the CV to match.
        request: SkillMatchRequest with jd_text.
        db: Database session.
        current_user: Authenticated user.
        
    Returns:
        SkillMatchResponse with matched/missing/extra skills and match rate.
        
    Raises:
        404: CV not found or access denied.
        400: CV analysis not completed yet (skill_categories is None).
        422: Invalid request (jd_text validation failed).
        
    Example Request:
        POST /api/v1/ai/cvs/{cv_id}/match
        {
            "jd_text": "Looking for Python developer with Django and React experience..."
        }
        
    Example Response:
        {
            "matched_skills": {"programming_languages": ["python"], "frameworks": ["django"]},
            "missing_skills": {"frameworks": ["react"]},
            "extra_skills": {"programming_languages": ["java"]},
            "skill_match_rate": 0.67,
            "match_percentage": 67.0,
            "jd_requirements": {...},
            "cv_skills": {...}
        }
    """
    logger.info(f"🔍 SKILL MATCH REQUEST - CV ID: {cv_id}, User: {current_user.email}, JD length: {len(request.jd_text)}")
    
    # 1. Verify CV ownership
    result = await db.execute(
        select(CV).where(
            CV.id == cv_id,
            CV.user_id == current_user.id
        )
    )
    cv = result.scalar_one_or_none()
    if not cv:
        logger.warning(f"CV not found or access denied: cv_id={cv_id}, user={current_user.email}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="CV not found or access denied"
        )
    
    # 2. Get CV analysis with skill_categories
    result = await db.execute(
        select(models.CVAnalysis).where(models.CVAnalysis.cv_id == cv_id)
    )
    analysis = result.scalar_one_or_none()
    
    if not analysis:
        logger.warning(f"Analysis not found for CV: cv_id={cv_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found for this CV"
        )
    
    # 3. Check if CV has been analyzed (skill_categories populated)
    if not analysis.skill_categories:
        logger.warning(f"CV analysis not completed: cv_id={cv_id}, status={analysis.status}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CV analysis not completed yet. Please wait for analysis to finish."
        )
    
    # 4. Perform skill matching
    from .skill_scorer import SkillMatcher
    
    matcher = SkillMatcher()
    match_result = matcher.match_skills(
        cv_skills=analysis.skill_categories,
        jd_text=request.jd_text
    )
    
    # 5. Build response
    response = schemas.SkillMatchResponse(
        matched_skills=match_result["matched_skills"],
        missing_skills=match_result["missing_skills"],
        extra_skills=match_result["extra_skills"],
        skill_match_rate=match_result["skill_match_rate"],
        jd_requirements=match_result["jd_requirements"],
        cv_skills=match_result["cv_skills"]
    )
    
    logger.info(
        f"✅ MATCH COMPLETE - CV ID: {cv_id}, "
        f"Match Rate: {match_result['skill_match_rate']:.2%}, "
        f"Matched: {sum(len(s) for s in match_result['matched_skills'].values())}, "
        f"Missing: {sum(len(s) for s in match_result['missing_skills'].values())}"
    )
    
    return response