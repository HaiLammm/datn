from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, EmailStr, field_validator


# Role type for type safety
UserRole = Literal["job_seeker", "recruiter", "admin"]


class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    birthday: Optional[datetime] = None
    role: UserRole = "job_seeker"
    is_active: bool = False
    is_scraped: bool = False
    avatar: Optional[str] = None


class UserCreate(BaseModel):
    """Schema for user registration - only allows job_seeker or recruiter roles."""
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    role: Literal["job_seeker", "recruiter"] = "job_seeker"

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: str) -> str:
        """Ensure admin role cannot be set during registration."""
        if v == "admin":
            raise ValueError("Cannot register as admin")
        if v not in ("job_seeker", "recruiter"):
            raise ValueError("Role must be either 'job_seeker' or 'recruiter'")
        return v


class UserResponse(BaseModel):
    """Schema for user response - includes all user fields."""
    id: int
    email: EmailStr
    full_name: Optional[str] = None
    birthday: Optional[datetime] = None
    role: UserRole
    is_active: bool
    is_scraped: bool
    avatar: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Alias for backward compatibility
User = UserResponse


class UserStatsResponse(BaseModel):
    """Schema for user statistics response."""

    total_cvs: int
    average_score: Optional[float] = None  # null if no completed analyses
    best_score: Optional[int] = None  # null if no completed analyses
    total_unique_skills: int
    top_skills: List[str]  # Top 5 most common skills

    class Config:
        from_attributes = True
