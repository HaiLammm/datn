from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.auth.dependencies import get_current_active_user
from app.modules.users.models import User
from app.modules.users.schemas import User as UserSchema, UserStatsResponse
from app.modules.users import services

router = APIRouter()


@router.get("/me", response_model=UserSchema)
async def read_current_user(current_user: User = Depends(get_current_active_user)) -> Any:
    """
    Get current user.
    """
    return current_user


@router.get("/me/stats", response_model=UserStatsResponse)
async def get_current_user_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get statistics for the current user's CVs and analyses.

    Returns:
        - total_cvs: Total number of uploaded CVs
        - average_score: Average quality score from completed analyses
        - best_score: Best (highest) quality score
        - total_unique_skills: Total unique skills across all CVs
        - top_skills: Top 5 most common skills by frequency
    """
    # Store user_id before any potential session expiration
    user_id = current_user.id
    stats = await services.get_user_stats(db, user_id)
    return stats
