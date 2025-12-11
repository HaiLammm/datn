import random
import string
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_password_hash, verify_password
from app.modules.users.models import User
from app.modules.users.services import UserService
from app.modules.users.schemas import UserCreate



class AuthService:
    def __init__(
        self,
        db: AsyncSession = Depends(get_db),
        user_service: UserService = Depends(UserService),
    ):
        self.db = db
        self.user_service = user_service

    async def authenticate_user(self, *, email: str, password: str) -> Optional[User]:
        user = await self.user_service.get_user_by_email(email=email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    async def register_user(self, user_in: "UserCreate") -> tuple[User, str]:
        """
        Register a new user, hash their password, and create an activation code.
        """
        existing_user = await self.user_service.get_user_by_email(email=user_in.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The user with this email already exists in the system.",
            )

        hashed_password = get_password_hash(user_in.password)
        activation_code = self.generate_activation_code()
        activation_code_expires_at = datetime.utcnow() + timedelta(minutes=30) # 30-minute expiry

        db_user = await self.user_service.create_user(
            user_in=user_in,
            hashed_password=hashed_password,
            activation_code=activation_code,
            activation_code_expires_at=activation_code_expires_at
        )

        return db_user, activation_code


    def generate_activation_code(self, length: int = 6) -> str:
        """Generate a random activation code."""
        return "".join(random.choices(string.digits, k=length))

    async def activate_user(self, *, email: str, activation_code: str) -> User:
        user = await self.user_service.get_user_by_email(email=email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        if user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Account is already active",
            )
        if (
            not user.activation_code
            or user.activation_code != activation_code
            or user.activation_code_expires_at < datetime.utcnow()
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired activation code",
            )
        user.is_active = True
        user.activation_code = None
        user.activation_code_expires_at = None
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def request_password_change(self, *, user: User) -> str:
        """Generate and save a password reset OTP."""
        otp = self.generate_activation_code()
        user.password_reset_code = otp
        user.password_reset_code_expires_at = datetime.utcnow() + timedelta(
            minutes=5
        )
        await self.db.commit()
        await self.db.refresh(user)
        return otp

    async def change_password(self, *, user: User, otp: str, new_password: str) -> User:
        if (
            not user.password_reset_code
            or user.password_reset_code != otp
            or user.password_reset_code_expires_at < datetime.utcnow()
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired password reset code",
            )
        user.hashed_password = get_password_hash(new_password)
        user.password_reset_code = None
        user.password_reset_code_expires_at = None
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def request_password_reset(self, *, email: str) -> Optional[str]:
        """Generate and save a password reset OTP for an unauthenticated user."""
        user = await self.user_service.get_user_by_email(email=email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="The user with this email does not exist.",
            )
        otp = self.generate_activation_code()
        user.password_reset_code = otp
        user.password_reset_code_expires_at = datetime.utcnow() + timedelta(
            minutes=5
        )
        await self.db.commit()
        await self.db.refresh(user)
        return otp

    async def reset_password_with_code(
        self, *, email: str, otp: str, new_password: str
    ) -> User:
        """Reset user password using an OTP for an unauthenticated user."""
        user = await self.user_service.get_user_by_email(email=email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        if (
            not user.password_reset_code
            or user.password_reset_code != otp
            or user.password_reset_code_expires_at < datetime.utcnow()
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired password reset code",
            )
        user.hashed_password = get_password_hash(new_password)
        user.password_reset_code = None
        user.password_reset_code_expires_at = None
        await self.db.commit()
        await self.db.refresh(user)
        return user
