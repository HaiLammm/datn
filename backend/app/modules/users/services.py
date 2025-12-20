import logging
import os
from datetime import datetime
from typing import Optional
from collections import Counter

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.modules.users.models import User
from app.modules.users.schemas import UserCreate
from app.modules.cv.models import CV
from app.modules.ai.models import CVAnalysis, AnalysisStatus

logger = logging.getLogger(__name__)


class UserService:
    def __init__(self, db: AsyncSession = Depends(get_db)):
        self.db = db

    async def get_user_by_email(self, email: str) -> Optional[User]:
        result = await self.db.execute(select(User).filter(User.email == email))
        return result.scalars().first()

    async def create_user(
        self,
        user_in: UserCreate,
        hashed_password: str,
        activation_code: Optional[str] = None,
        activation_code_expires_at: Optional[datetime] = None,
    ) -> User:
        db_user = User(
            email=user_in.email,
            hashed_password=hashed_password,
            full_name=user_in.full_name,
            role=user_in.role,
            is_active=False,  # Default to inactive until email verification
            activation_code=activation_code,
            activation_code_expires_at=activation_code_expires_at,
        )
        self.db.add(db_user)
        await self.db.commit()
        await self.db.refresh(db_user)
        return db_user


async def get_user_stats(db: AsyncSession, user_id: int) -> dict:
    """
    Get statistics for a user's CVs and analyses.

    Returns:
        dict with keys:
        - total_cvs: Total number of active CVs
        - average_score: Average quality score from COMPLETED analyses (or None)
        - best_score: Maximum quality score from COMPLETED analyses (or None)
        - total_unique_skills: Count of unique skills across all analyses
        - top_skills: Top 5 most common skills by frequency
    """
    # Query CVs with their analyses using eager loading to avoid N+1
    result = await db.execute(
        select(CV)
        .options(selectinload(CV.analyses))
        .where(CV.user_id == user_id, CV.is_active == True)  # noqa: E712
    )
    cvs = result.scalars().all()

    total_cvs = len(cvs)

    # Collect scores and skills from COMPLETED analyses
    scores: list[int] = []
    all_skills: list[str] = []

    for cv in cvs:
        for analysis in cv.analyses:
            if analysis.status == AnalysisStatus.COMPLETED:
                if analysis.ai_score is not None:
                    scores.append(analysis.ai_score)
                if analysis.extracted_skills:
                    all_skills.extend(analysis.extracted_skills)

    # Calculate stats
    average_score = round(sum(scores) / len(scores), 1) if scores else None
    best_score = max(scores) if scores else None

    # Unique skills and top 5
    unique_skills = set(all_skills)
    skill_counts = Counter(all_skills)
    top_skills = [skill for skill, _ in skill_counts.most_common(5)]

    return {
        "total_cvs": total_cvs,
        "average_score": average_score,
        "best_score": best_score,
        "total_unique_skills": len(unique_skills),
        "top_skills": top_skills,
    }


async def delete_user_account(db: AsyncSession, user_id: int) -> None:
    """
    Delete a user account and all associated data.

    Deletion order (due to lack of CASCADE constraints on cvs.user_id and cv_analyses.cv_id):
    1. Query all user's CVs with their analyses using eager loading
    2. Delete files from local storage
    3. Delete all CVAnalysis records for each CV
    4. Delete all CV records
    5. Delete the user record (job_descriptions will cascade automatically)

    Args:
        db: The database session
        user_id: The ID of the user to delete

    Raises:
        ValueError: If user is not found
    """
    # Step 1: Query user's CVs with analyses using eager loading
    result = await db.execute(
        select(CV)
        .options(selectinload(CV.analyses))
        .where(CV.user_id == user_id)
    )
    cvs = result.scalars().all()

    # Collect file paths and analysis/CV IDs before any deletions
    file_paths: list[str] = []
    analysis_ids: list = []
    cv_ids: list = []

    for cv in cvs:
        if cv.file_path:
            file_paths.append(cv.file_path)
        cv_ids.append(cv.id)
        for analysis in cv.analyses:
            analysis_ids.append(analysis.id)

    # Step 2: Delete files from local storage
    for file_path in file_paths:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Deleted file: {file_path}")
        except OSError as e:
            # Log the error but continue with deletion
            logger.warning(f"Failed to delete file {file_path}: {e}")

    # Step 3: Delete all CVAnalysis records (no CASCADE on cv_id)
    if analysis_ids:
        await db.execute(
            delete(CVAnalysis).where(CVAnalysis.id.in_(analysis_ids))
        )

    # Step 4: Delete all CV records (no CASCADE on user_id)
    if cv_ids:
        await db.execute(
            delete(CV).where(CV.id.in_(cv_ids))
        )

    # Step 5: Delete the user record (job_descriptions will cascade automatically)
    await db.execute(
        delete(User).where(User.id == user_id)
    )

    await db.commit()
    logger.info(f"Successfully deleted user {user_id} and all associated data")
