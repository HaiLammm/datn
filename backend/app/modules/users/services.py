from datetime import datetime
from typing import Optional

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.modules.users.models import User
from app.modules.users.schemas import UserCreate


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
