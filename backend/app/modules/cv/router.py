from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.dependencies import get_current_user, rate_limit_cv_upload
from app.modules.users.models import User
from app.core.database import get_db
from app.modules.cv.schemas import CVResponse
from app.modules.cv.service import create_cv


router = APIRouter(tags=["CVs"])


@router.get("/")
async def test_cv_router():
    return {"message": "CV router is working!"}


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
