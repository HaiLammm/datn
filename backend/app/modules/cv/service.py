import uuid
import asyncio
import logging
from pathlib import Path
from datetime import datetime

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.modules.cv.models import CV
from app.modules.users.models import User
from app.modules.ai.models import CVAnalysis, AnalysisStatus

logger = logging.getLogger(__name__)


async def create_cv(
    db: AsyncSession, file: UploadFile, current_user: User
) -> CV:
    # Ensure the upload directory exists
    upload_dir = settings.CV_STORAGE_PATH  # type: ignore
    upload_dir.mkdir(parents=True, exist_ok=True)

    # Generate a unique filename to prevent collisions
    file_extension = Path(file.filename).suffix
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = upload_dir / unique_filename

    # Save the file to disk
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    # Create a new CV record in the database
    db_cv = CV(
        user_id=current_user.id,
        filename=file.filename,  # Store original filename
        file_path=str(file_path),  # Store the path to the saved file
        uploaded_at=datetime.utcnow(),
        is_active=True
    )
    db.add(db_cv)
    await db.commit()
    await db.refresh(db_cv)

    # Store values before any more DB operations
    cv_id = db_cv.id
    cv_file_path = str(file_path)

    # Create CVAnalysis record with PENDING status
    cv_analysis = CVAnalysis(
        cv_id=cv_id,
        status=AnalysisStatus.PENDING,
    )
    db.add(cv_analysis)
    await db.commit()

    # Refresh db_cv to ensure all attributes are loaded before returning
    await db.refresh(db_cv)

    logger.info(f"CV uploaded and analysis record created for CV: {cv_id}")

    # Trigger background AI analysis (fire and forget)
    asyncio.create_task(trigger_ai_analysis(cv_id, cv_file_path))

    return db_cv


async def trigger_ai_analysis(cv_id: uuid.UUID, file_path: str) -> None:
    """Trigger AI analysis as a background task."""
    from app.core.database import AsyncSessionLocal
    from app.modules.ai.service import ai_service

    try:
        async with AsyncSessionLocal() as db:
            await ai_service.analyze_cv(cv_id, file_path, db)
            logger.info(f"AI analysis completed for CV: {cv_id}")
    except Exception as e:
        logger.error(f"AI analysis failed for CV {cv_id}: {str(e)}")
