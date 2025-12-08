from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.modules.users.models import User
from app.modules.users.schemas import UserCreate


class UserService:
    def get_user_by_email(self, db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

    def create_user(
        self,
        db: Session,
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
            is_active=user_in.is_active,
            is_scraped=user_in.is_scraped,
            avatar=user_in.avatar,
            activation_code=activation_code,
            activation_code_expires_at=activation_code_expires_at,
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
