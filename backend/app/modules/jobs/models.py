import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
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
    job_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    benefits: Mapped[Optional[List[str]]] = mapped_column(ARRAY(Text), nullable=True)
    
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
        CheckConstraint(
            "job_type IN ('full-time', 'part-time', 'contract', 'internship', 'freelance') OR job_type IS NULL",
            name="check_job_type"
        ),
    )
    
    # Relationships
    applications = relationship("Application", back_populates="job", cascade="all, delete-orphan")


class Application(Base):
    __tablename__ = "applications"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("job_descriptions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    cv_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cvs.id", ondelete="SET NULL"), nullable=True
    )
    cover_letter: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        String(50), default="pending", nullable=False, index=True
    )
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    job = relationship("JobDescription", back_populates="applications")
    user = relationship("User") 
    cv = relationship("CV")

    __table_args__ = (
        UniqueConstraint('user_id', 'job_id', name='uq_user_job_application'),
        CheckConstraint(
            "status IN ('pending', 'reviewed', 'shortlisted', 'rejected', 'accepted', 'hired')",
            name="check_application_status"
        ),
    )

