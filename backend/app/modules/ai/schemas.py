import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any

from pydantic import BaseModel, computed_field, Field, field_validator


class ExperienceBreakdown(BaseModel):
    total_years: int = 0
    key_roles: List[str] = []
    industries: List[str] = []


class CriteriaExplanation(BaseModel):
    completeness: int = 50
    experience: int = 50
    skills: int = 50
    professionalism: int = 50


class SkillBreakdown(BaseModel):
    """Hybrid skill scoring breakdown.
    
    Stores the individual component scores from the hybrid skill scoring system.
    """
    completeness_score: int = Field(ge=0, le=7, description="Skill completeness (0-7)")
    categorization_score: int = Field(ge=0, le=6, description="Category coverage (0-6)")
    evidence_score: int = Field(ge=0, le=6, description="Evidence from LLM (0-6)")
    market_relevance_score: int = Field(ge=0, le=6, description="Hot skills match (0-6)")
    total_score: int = Field(ge=0, le=25, description="Total skill score (0-25)")

    @field_validator('total_score')
    @classmethod
    def validate_total_not_exceed_max(cls, v: int) -> int:
        """Ensure total_score does not exceed maximum possible (25)."""
        if v > 25:
            raise ValueError('total_score cannot exceed 25')
        return v


class SkillCategories(BaseModel):
    """Categorized skills extracted from CV.
    
    Groups skills into standard IT taxonomy categories.
    """
    programming_languages: List[str] = Field(default_factory=list)
    frameworks: List[str] = Field(default_factory=list)
    databases: List[str] = Field(default_factory=list)
    devops: List[str] = Field(default_factory=list)
    soft_skills: List[str] = Field(default_factory=list)
    ai_ml: List[str] = Field(default_factory=list)


class AnalysisResult(BaseModel):
    """CV Analysis result schema.
    
    Attributes:
        extracted_skills: DEPRECATED - Use skill_categories instead.
            Kept for backward compatibility with existing clients.
    """
    id: uuid.UUID
    cv_id: uuid.UUID
    status: str
    ai_score: Optional[int] = None
    ai_summary: Optional[str] = None
    ai_feedback: Optional[dict] = None
    extracted_skills: Optional[List[str]] = None
    
    # New skill scoring fields (Story 5.3)
    skill_breakdown: Optional[SkillBreakdown] = None
    skill_categories: Optional[SkillCategories] = None
    skill_recommendations: Optional[List[str]] = None
    
    created_at: datetime
    updated_at: datetime

    # Computed fields that extract data from ai_feedback
    @computed_field
    @property
    def experience_breakdown(self) -> ExperienceBreakdown:
        if self.ai_feedback and "experience_breakdown" in self.ai_feedback:
            return ExperienceBreakdown(**self.ai_feedback["experience_breakdown"])
        return ExperienceBreakdown()

    @computed_field
    @property
    def formatting_feedback(self) -> List[str]:
        if self.ai_feedback and "formatting_feedback" in self.ai_feedback:
            return self.ai_feedback["formatting_feedback"]
        return []

    @computed_field
    @property
    def ats_hints(self) -> List[str]:
        if self.ai_feedback and "ats_hints" in self.ai_feedback:
            return self.ai_feedback["ats_hints"]
        return []

    @computed_field
    @property
    def strengths(self) -> List[str]:
        if self.ai_feedback and "strengths" in self.ai_feedback:
            return self.ai_feedback["strengths"]
        return []

    @computed_field
    @property
    def improvements(self) -> List[str]:
        if self.ai_feedback and "improvements" in self.ai_feedback:
            return self.ai_feedback["improvements"]
        return []

    @computed_field
    @property
    def criteria_explanation(self) -> CriteriaExplanation:
        if self.ai_feedback and "criteria" in self.ai_feedback:
            return CriteriaExplanation(**self.ai_feedback["criteria"])
        return CriteriaExplanation()

    class Config:
        from_attributes = True


class AnalysisStatus(BaseModel):
    status: str
    message: Optional[str] = None


class SkillExtraction(BaseModel):
    skills: List[str]


class QualityScore(BaseModel):
    score: int
    criteria: dict