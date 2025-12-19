import uuid
import asyncio
import logging
from pathlib import Path
from datetime import datetime

from fastapi import UploadFile, HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.modules.cv.models import CV
from app.modules.users.models import User
from app.modules.ai.models import CVAnalysis, AnalysisStatus

logger = logging.getLogger(__name__)


async def create_cv(
    db: AsyncSession, file: UploadFile, current_user: User
) -> CV:
    upload_dir = settings.CV_STORAGE_PATH  # type: ignore
    upload_dir.mkdir(parents=True, exist_ok=True)

    file_extension = Path(file.filename).suffix
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = upload_dir / unique_filename

    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    db_cv = CV(
        user_id=current_user.id,
        filename=file.filename,
        file_path=str(file_path),
        uploaded_at=datetime.utcnow(),
        is_active=True,
    )
    db.add(db_cv)
    await db.commit()
    await db.refresh(db_cv)

    cv_id = db_cv.id
    cv_file_path = str(file_path)

    cv_analysis = CVAnalysis(
        cv_id=cv_id,
        status=AnalysisStatus.PENDING,
    )
    db.add(cv_analysis)
    await db.commit()
    await db.refresh(db_cv)

    logger.info("CV uploaded and analysis record created for CV: %s", cv_id)

    asyncio.create_task(trigger_ai_analysis(cv_id, cv_file_path))

    return db_cv


async def delete_cv(
    db: AsyncSession, cv_id: uuid.UUID, current_user: User
) -> None:
    result = await db.execute(
        select(CV).where(CV.id == cv_id, CV.user_id == current_user.id)
    )
    cv = result.scalars().first()
    if cv is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="CV not found",
        )

    file_path = Path(cv.file_path)

    try:
        await db.execute(delete(CVAnalysis).where(CVAnalysis.cv_id == cv_id))
        await db.delete(cv)
        await db.commit()
    except Exception:
        await db.rollback()
        logger.exception("Failed to delete CV %s", cv_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete CV",
        )

    try:
        if file_path.exists():
            file_path.unlink()
        else:
            logger.warning("CV file not found on disk: %s", file_path)
    except Exception:
        logger.exception("Failed to remove CV file on disk: %s", file_path)


async def get_cv_for_download(
    db: AsyncSession, cv_id: uuid.UUID, current_user: User
) -> CV:
    """
    Get CV for download, verifying ownership and file existence.
    
    Args:
        db: Database session
        cv_id: UUID of the CV to download
        current_user: Current authenticated user
        
    Returns:
        CV object with file_path and filename
        
    Raises:
        HTTPException: 404 if CV not found, 403 if not owner
    """
    # Store user info before any DB operations for logging
    user_email = current_user.email
    user_id = current_user.id
    
    result = await db.execute(
        select(CV).where(CV.id == cv_id)
    )
    cv = result.scalars().first()
    
    if cv is None:
        logger.warning(
            "Download attempt for non-existent CV: %s by user: %s",
            cv_id, user_email
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="CV not found",
        )
    
    # Check ownership
    if cv.user_id != user_id:
        logger.warning(
            "Unauthorized download attempt for CV: %s by user: %s (owner: %s)",
            cv_id, user_email, cv.user_id
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to download this CV",
        )
    
    # Verify file exists on disk
    file_path = Path(cv.file_path)
    if not file_path.exists():
        logger.error(
            "CV file not found on disk: %s for CV: %s",
            file_path, cv_id
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="CV file not found on server",
        )
    
    # Log download attempt for audit
    logger.info(
        "CV download initiated - CV ID: %s, Filename: %s, User: %s",
        cv_id, cv.filename, user_email
    )
    
    return cv


async def trigger_ai_analysis(cv_id: uuid.UUID, file_path: str) -> None:
    """Trigger AI analysis as a background task."""
    from app.core.database import AsyncSessionLocal
    from app.modules.ai.service import ai_service

    try:
        async with AsyncSessionLocal() as db:
            await ai_service.analyze_cv(cv_id, file_path, db)
            logger.info("AI analysis completed for CV: %s", cv_id)
    except Exception as e:
        logger.error("AI analysis failed for CV %s: %s", cv_id, str(e))
