import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class JobDescription(Base):
    __tablename__ = "job_descriptions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    required_skills: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(Text), nullable=True
    )
    min_experience_years: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    location_type: Mapped[str] = mapped_column(
        String(50), nullable=False, default="remote"
    )
    salary_min: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    salary_max: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Parsing status: pending, processing, completed, failed
    parse_status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="pending", index=True
    )
    # Error message when parsing fails
    parse_error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    # Parsed requirements stored as JSONB (populated by JDParser)
    parsed_requirements: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    
    # Embedding stored as JSONB array for now; will be populated by Story 3.2/3.3
    # ChromaDB is used for vector similarity search (see ai/vector_store.py)
    embedding: Mapped[Optional[List[float]]] = mapped_column(JSONB, nullable=True)

    # Relationship
    user = relationship("User", back_populates="job_descriptions")

    __table_args__ = (
        CheckConstraint(
            "location_type IN ('remote', 'hybrid', 'on-site')",
            name="check_location_type"
        ),
        CheckConstraint(
            "parse_status IN ('pending', 'processing', 'completed', 'failed')",
            name="check_parse_status"
        ),
    )
