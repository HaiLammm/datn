from typing import List

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.modules.auth.dependencies import get_current_user, rate_limit_cv_upload
from app.modules.users.models import User
from app.core.database import get_db
from app.modules.cv.schemas import CVResponse, CVWithStatusResponse
from app.modules.cv.service import create_cv
from app.modules.cv.models import CV


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
    # Single query with eager loading of analyses relationship
    result = await db.execute(
        select(CV)
        .options(selectinload(CV.analyses))
        .where(CV.user_id == current_user.id)
        .order_by(CV.uploaded_at.desc())
    )
    cvs = result.scalars().all()

    # Build response using pre-loaded analyses
    cv_responses = []
    for cv in cvs:
        # Get status from eagerly loaded analyses (first analysis if exists)
        analysis = cv.analyses[0] if cv.analyses else None
        if analysis:
            status_str = analysis.status.value if hasattr(analysis.status, 'value') else str(analysis.status)
        else:
            status_str = "PENDING"

        cv_responses.append(CVWithStatusResponse(
            id=cv.id,
            user_id=cv.user_id,
            filename=cv.filename,
            file_path=cv.file_path,
            uploaded_at=cv.uploaded_at,
            is_active=cv.is_active,
            analysis_status=status_str
        ))

    return cv_responses


@router.post("/", response_model=CVResponse, status_code=status.HTTP_201_CREATED)
async def upload_cv(
    file: UploadFile = File(...),
    current_user: User = Depends(rate_limit_cv_upload),
    db: AsyncSession = Depends(get_db),
):
    if file.content_type not in [
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chỉ chấp nhận file PDF hoặc DOCX.",
        )

    # Call the service function to handle file saving and DB record creation
    db_cv = await create_cv(db=db, file=file, current_user=current_user)
    return db_cv
