import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import Integer, String, Text, JSON, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class AnalysisStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class CVAnalysis(Base):
    __tablename__ = "cv_analyses"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    cv_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cvs.id"), nullable=False
    )
    status: Mapped[AnalysisStatus] = mapped_column(
        String, default=AnalysisStatus.PENDING, nullable=False
    )
    ai_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    ai_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    ai_feedback: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    extracted_skills: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    
    # Hybrid skill scoring columns (Story 5.3)
    skill_breakdown: Mapped[dict | None] = mapped_column(
        JSONB, nullable=True, comment="Hybrid skill scoring breakdown"
    )
    """Stores SkillBreakdown data: completeness_score, categorization_score, 
    evidence_score, market_relevance_score, total_score."""
    
    skill_categories: Mapped[dict | None] = mapped_column(
        JSONB, nullable=True, comment="Categorized skills by type"
    )
    """Stores categorized skills: programming_languages, frameworks, databases, 
    devops, soft_skills, ai_ml."""
    
    skill_recommendations: Mapped[list[str] | None] = mapped_column(
        JSONB, nullable=True, comment="Skill improvement recommendations"
    )
    """Stores list of skill improvement recommendations."""
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationship back to CV
    cv = relationship("CV", back_populates="analyses")