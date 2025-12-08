import random
import string
from datetime import datetime, timedelta
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password
from app.modules.users.models import User
from app.modules.users.services import UserService


class AuthService:
    def __init__(self, user_service: UserService = UserService()):
        self.user_service = user_service

    def authenticate_user(
        self, db: Session, *, email: str, password: str
    ) -> Optional[User]:
        user = self.user_service.get_user_by_email(db, email=email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    def generate_activation_code(self, length: int = 6) -> str:
        """Generate a random activation code."""
        return "".join(random.choices(string.digits, k=length))

    def activate_user(self, db: Session, *, email: str, activation_code: str) -> User:
        user = self.user_service.get_user_by_email(db, email=email)
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
        db.commit()
        db.refresh(user)
        return user

    def request_password_change(self, db: Session, *, user: User) -> str:
        """Generate and save a password reset OTP."""
        otp = self.generate_activation_code()
        user.password_reset_code = otp
        user.password_reset_code_expires_at = datetime.utcnow() + timedelta(
            minutes=5
        )
        db.commit()
        db.refresh(user)
        return otp

    def change_password(
        self, db: Session, *, user: User, otp: str, new_password: str
    ) -> User:
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
        db.commit()
        db.refresh(user)
        return user

    def request_password_reset(self, db: Session, *, email: str) -> Optional[str]:
        """Generate and save a password reset OTP for an unauthenticated user."""
        user = self.user_service.get_user_by_email(db, email=email)
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
        db.commit()
        db.refresh(user)
        return otp

    def reset_password_with_code(
        self, db: Session, *, email: str, otp: str, new_password: str
    ) -> User:
        """Reset user password using an OTP for an unauthenticated user."""
        user = self.user_service.get_user_by_email(db, email=email)
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
        db.commit()
        db.refresh(user)
        return user