"""
Admin Schemas
"""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr


class AdminUserResponse(BaseModel):
    """Admin view of a user."""
    id: int
    email: EmailStr
    full_name: Optional[str] = None
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class AdminUserListResponse(BaseModel):
    """Paginated list of users for admin."""
    items: List[AdminUserResponse]
    total: int
    limit: int
    offset: int


class AdminStatsResponse(BaseModel):
    """System statistics for admin dashboard."""
    total_users: int
    job_seekers: int
    recruiters: int
    admins: int
