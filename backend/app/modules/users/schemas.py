from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    birthday: Optional[datetime] = None
    role: Optional[str] = "user"  # Updated default role to "user"
    is_active: bool = False
    is_scraped: bool = False
    avatar: Optional[str] = None


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
