from datetime import datetime

from sqlalchemy import Boolean, Column, Integer, String, DateTime
from sqlalchemy.orm import relationship

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    role = Column(String, default="user", nullable=False)  # Enum: admin, user, recruiter, student
    is_active = Column(Boolean, default=False)
    is_scraped = Column(Boolean, default=False, comment="Đánh dấu tài khoản cào về")
    avatar = Column(String, nullable=True)
    activation_code = Column(String, nullable=True)
    activation_code_expires_at = Column(DateTime, nullable=True)
    password_reset_code = Column(String, nullable=True)
    password_reset_code_expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Example of relationship (if needed in the future)
    # items = relationship("Item", back_populates="owner")
