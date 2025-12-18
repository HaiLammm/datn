from typing import List
import uuid
import logging

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.modules.auth.dependencies import get_current_user, rate_limit_cv_upload
from app.modules.users.models import User
from app.core.database import get_db
from app.modules.cv.schemas import CVResponse, CVWithStatusResponse, CVVisibilityUpdate
from app.modules.cv.service import create_cv, delete_cv
from app.modules.cv.models import CV

logger = logging.getLogger(__name__)

router = APIRouter(tags=["CVs"])


@router.get("/", response_model=List[CVWithStatusResponse])
async def list_user_cvs(
    current_user: User = Depends(get_current_user),
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
        else:
            status_str = "PENDING"

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
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await delete_cv(db=db, cv_id=cv_id, current_user=current_user)
    return None


@router.patch("/{cv_id}/visibility", response_model=CVWithStatusResponse)
async def update_cv_visibility(
    cv_id: uuid.UUID,
    visibility_update: CVVisibilityUpdate,
    current_user: User = Depends(get_current_user),
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

    # Get analysis status
    analysis = cv.analyses[0] if cv.analyses else None
    if analysis:
        status_str = analysis.status.value if hasattr(analysis.status, "value") else str(analysis.status)
    else:
        status_str = "PENDING"

    logger.info(f"🔒 CV VISIBILITY UPDATED - CV ID: {cv_id}, is_public: {visibility_update.is_public}, User: {user_email}")

    return CVWithStatusResponse(
        id=cv.id,
        user_id=cv.user_id,
        filename=cv.filename,
        file_path=cv.file_path,
        uploaded_at=cv.uploaded_at,
        is_active=cv.is_active,
        is_public=cv.is_public,
        analysis_status=status_str,
    )
