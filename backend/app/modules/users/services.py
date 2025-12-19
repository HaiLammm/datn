from datetime import datetime
from typing import Optional
from collections import Counter

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.modules.users.models import User
from app.modules.users.schemas import UserCreate
from app.modules.cv.models import CV
from app.modules.ai.models import CVAnalysis, AnalysisStatus


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
