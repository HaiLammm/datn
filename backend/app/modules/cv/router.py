from typing import List
import uuid
import logging

from pathlib import Path

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.modules.auth.dependencies import get_current_user, rate_limit_cv_upload, require_job_seeker
from app.modules.users.models import User
from app.core.database import get_db
from app.modules.cv.schemas import CVResponse, CVWithStatusResponse, CVVisibilityUpdate, SkillSuggestionsResponse
from app.modules.cv.service import create_cv, delete_cv, get_cv_for_download
from app.modules.cv.models import CV
from app.modules.ai.models import CVAnalysis, AnalysisStatus # New import
from app.modules.ai.skill_suggestions import skill_suggester # New import

logger = logging.getLogger(__name__)

router = APIRouter(tags=["CVs"])


@router.get("/", response_model=List[CVWithStatusResponse])
async def list_user_cvs(
    current_user: User = Depends(require_job_seeker),
    db: AsyncSession = Depends(get_db),
):
    """
    Get a list of all CVs uploaded by the current user with their analysis status.
    Uses eager loading to avoid N+1 query problem.
    """
    result = await db.execute(
        select(CV)
        .options(selectinload(CV.analyses))
        .where(CV.user_id == current_user.id)
        .order_by(CV.uploaded_at.desc())
    )
    cvs = result.scalars().all()

    cv_responses = []
    for cv in cvs:
        analysis = cv.analyses[0] if cv.analyses else None
        if analysis:
            status_str = analysis.status.value if hasattr(analysis.status, "value") else str(analysis.status)
            quality_score = analysis.ai_score
        else:
            status_str = "PENDING"
            quality_score = None

        cv_responses.append(
            CVWithStatusResponse(
                id=cv.id,
                user_id=cv.user_id,
                filename=cv.filename,
                file_path=cv.file_path,
                uploaded_at=cv.uploaded_at,
                is_active=cv.is_active,
                is_public=cv.is_public,
                analysis_status=status_str,
                quality_score=quality_score,
            )
        )

    return cv_responses


@router.post("/", response_model=CVResponse, status_code=status.HTTP_201_CREATED)
async def upload_cv(
    file: UploadFile = File(...),
    current_user: User = Depends(rate_limit_cv_upload),
    db: AsyncSession = Depends(get_db),
):
    logger.info(f"📤 CV UPLOAD - User: {current_user.email}, Filename: {file.filename}")
    
    if file.content_type not in [
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chỉ chấp nhận file PDF hoặc DOCX.",
        )

    db_cv = await create_cv(db=db, file=file, current_user=current_user)
    logger.info(f"✅ CV UPLOAD SUCCESS - CV ID: {db_cv.id}, File: {file.filename}")
    return db_cv


@router.delete("/{cv_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_cv(
    cv_id: uuid.UUID,
    current_user: User = Depends(require_job_seeker),
    db: AsyncSession = Depends(get_db),
):
    await delete_cv(db=db, cv_id=cv_id, current_user=current_user)
    return None


@router.get("/{cv_id}/download")
async def download_cv(
    cv_id: uuid.UUID,
    current_user: User = Depends(require_job_seeker),
    db: AsyncSession = Depends(get_db),
):
    """
    Download the original CV file.
    
    Returns the file with correct content-type and Content-Disposition header
    to preserve the original filename.
    """
    cv = await get_cv_for_download(db=db, cv_id=cv_id, current_user=current_user)
    
    file_path = Path(cv.file_path)
    
    # Double-check file exists (service already checks, but be safe)
    if not file_path.exists():
        logger.error("CV file disappeared after service check: %s", file_path)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="CV file not found on server",
        )
    
    # Determine content type based on file extension
    content_type = "application/pdf"
    if cv.filename.lower().endswith(".docx"):
        content_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    elif cv.filename.lower().endswith(".doc"):
        content_type = "application/msword"
    
    logger.info("Serving CV file: %s for CV ID: %s", cv.filename, cv_id)
    
    return FileResponse(
        path=str(file_path),
        filename=cv.filename,  # Original filename for download
        media_type=content_type,
    )


@router.patch("/{cv_id}/visibility", response_model=CVWithStatusResponse)
async def update_cv_visibility(
    cv_id: uuid.UUID,
    visibility_update: CVVisibilityUpdate,
    current_user: User = Depends(require_job_seeker),
    db: AsyncSession = Depends(get_db),
):
    """
    Update CV visibility setting.
    Only the CV owner can change the visibility.
    """
    # Store user email before any commits (to avoid lazy loading issues after session changes)
    user_email = current_user.email
    
    # Fetch CV with analyses for response
    result = await db.execute(
        select(CV)
        .options(selectinload(CV.analyses))
        .where(CV.id == cv_id)
    )
    cv = result.scalar_one_or_none()

    if not cv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="CV not found"
        )

    # Check ownership
    if cv.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to modify this CV"
        )

    # Update visibility
    cv.is_public = visibility_update.is_public
    await db.commit()
    await db.refresh(cv)

    # Get analysis status and quality score
    analysis = cv.analyses[0] if cv.analyses else None
    if analysis:
        status_str = analysis.status.value if hasattr(analysis.status, "value") else str(analysis.status)
        quality_score = analysis.ai_score
    else:
        status_str = "PENDING"
        quality_score = None

    logger.info(f"CV VISIBILITY UPDATED - CV ID: {cv_id}, is_public: {visibility_update.is_public}, User: {user_email}")

    return CVWithStatusResponse(
        id=cv.id,
        user_id=cv.user_id,
        filename=cv.filename,
        file_path=cv.file_path,
        uploaded_at=cv.uploaded_at,
        is_active=cv.is_active,
        is_public=cv.is_public,
        analysis_status=status_str,
        quality_score=quality_score,
    )


@router.get(
    "/{cv_id}/suggestions",
    response_model=SkillSuggestionsResponse,
    summary="Get skill suggestions for a CV",
)
async def get_cv_skill_suggestions(
    cv_id: uuid.UUID,
    current_user: User = Depends(require_job_seeker),
    db: AsyncSession = Depends(get_db),
    max_suggestions: int = 10,
) -> SkillSuggestionsResponse:
    """
    Provides skill suggestions for a given CV based on its extracted skills.
    These suggestions can help job seekers improve their CV by adding related skills.
    
    Args:
        cv_id: The ID of the CV to get suggestions for.
        current_user: The authenticated job seeker.
        db: The database session.
        max_suggestions: Maximum number of suggestions to return.
        
    Returns:
        A list of suggested skill strings.
        
    Raises:
        HTTPException: 404 if CV or its analysis is not found.
        HTTPException: 403 if the CV does not belong to the current user.
    """
    # 1. Fetch CV and its analysis
    result = await db.execute(
        select(CV)
        .options(selectinload(CV.analyses))
        .where(CV.id == cv_id)
    )
    cv = result.scalar_one_or_none()

    if not cv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="CV not found."
        )
    
    # Check ownership
    if cv.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this CV."
        )

    analysis = cv.analyses[0] if cv.analyses else None
    if not analysis or not analysis.extracted_skills:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="CV analysis or extracted skills not found for this CV."
        )

    # 2. Get suggestions using the skill_suggester
    suggestions = skill_suggester.get_suggestions(
        cv_skills=analysis.extracted_skills,
        max_suggestions=max_suggestions
    )

    return SkillSuggestionsResponse(suggestions=suggestions)
