import uuid
from pathlib import Path
from datetime import datetime

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.modules.cv.models import CV
from app.modules.users.models import User  # Import User model to define the relationship


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

    # Placeholder for AI analysis trigger
    # In a real scenario, this would trigger a background task
    print(f"AI analysis triggered for CV: {db_cv.id}")

    return db_cv
