"""
Admin Router - Protected endpoints for admin users only.

All endpoints in this router require admin role.
"""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func

from app.core.database import get_db
from app.modules.auth.dependencies import require_admin
from app.modules.users.models import User
from app.modules.admin.schemas import (
    AdminUserListResponse,
    AdminUserResponse,
    AdminStatsResponse,
)

router = APIRouter(tags=["Admin"])


@router.get("/stats", response_model=AdminStatsResponse)
async def get_admin_stats(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> AdminStatsResponse:
    """
    Get overall system statistics.
    Admin only endpoint.
    """
    # Count total users by role
    result = await db.execute(
        select(User.role, func.count(User.id))
        .group_by(User.role)
    )
    role_counts = dict(result.all())
    
    total_users = sum(role_counts.values())
    
    return AdminStatsResponse(
        total_users=total_users,
        job_seekers=role_counts.get("job_seeker", 0),
        recruiters=role_counts.get("recruiter", 0),
        admins=role_counts.get("admin", 0),
    )


@router.get("/users", response_model=AdminUserListResponse)
async def list_all_users(
    role: Optional[str] = Query(None, description="Filter by role"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> AdminUserListResponse:
    """
    List all users with optional role filtering.
    Admin only endpoint.
    """
    query = select(User)
    
    if role:
        if role not in ("job_seeker", "recruiter", "admin"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid role filter"
            )
        query = query.where(User.role == role)
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Get paginated results
    query = query.order_by(User.created_at.desc()).limit(limit).offset(offset)
    result = await db.execute(query)
    users = result.scalars().all()
    
    return AdminUserListResponse(
        items=[
            AdminUserResponse(
                id=user.id,
                email=user.email,
                full_name=user.full_name,
                role=user.role,
                is_active=user.is_active,
                created_at=user.created_at,
            )
            for user in users
        ],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/users/{user_id}", response_model=AdminUserResponse)
async def get_user_by_id(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> AdminUserResponse:
    """
    Get a specific user by ID.
    Admin only endpoint.
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return AdminUserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at,
    )
