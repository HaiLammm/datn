import enum
from sqlalchemy import String, Boolean, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base
import utils


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String, unique=True)
    hash_password: Mapped[str] = mapped_column(String, unique=True)
    full_name: Mapped[str] = mapped_column(String)
    role: Mapped[UserRole] = mapped_column(
        SQLEnum(UserRole), default=UserRole.GUEST, nullable=False)
    is_activate: Mapped[bool] = mapped_column(Boolean, default=False)

    def is_admin(self):
        return self.role == UserRole.ADMIN
