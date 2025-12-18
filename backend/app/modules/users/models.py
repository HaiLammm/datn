import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    full_name: Mapped[str | None] = mapped_column(String, nullable=True)
    birthday: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    role: Mapped[str] = mapped_column(
        String, default="user", nullable=False
    )  # Enum: admin, user, recruiter, student
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    is_scraped: Mapped[bool] = mapped_column(
        Boolean, default=False, comment="Đánh dấu tài khoản cào về"
    )
    avatar: Mapped[str | None] = mapped_column(String, nullable=True)
    activation_code: Mapped[str | None] = mapped_column(String, nullable=True)
    activation_code_expires_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True
    )
    password_reset_code: Mapped[str | None] = mapped_column(String, nullable=True)
    password_reset_code_expires_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    cvs = relationship("CV", back_populates="owner")
    job_descriptions = relationship("JobDescription", back_populates="user")
