import uuid
from datetime import datetime
from typing import List, Optional

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


class SkillMatchRequest(BaseModel):
    """Request schema for skill matching endpoint.
    
    Attributes:
        jd_text: Job description text to extract requirements from.
            Must be at least 50 characters to ensure meaningful matching.
    """
    jd_text: str = Field(min_length=50, description="Job description text")
    
    @field_validator('jd_text')
    @classmethod
    def validate_jd_not_empty(cls, v: str) -> str:
        """Ensure jd_text is not just whitespace."""
        if not v.strip():
            raise ValueError('jd_text cannot be empty or whitespace')
        return v.strip()


class SkillMatchResponse(BaseModel):
    """Response schema for skill matching endpoint.
    
    Contains the results of matching CV skills against JD requirements,
    including matched skills, skill gaps, and match percentage.
    
    Attributes:
        matched_skills: Skills present in both CV and JD, grouped by category.
        missing_skills: JD requirements not found in CV (skill gaps).
        extra_skills: CV skills not required by JD.
        skill_match_rate: Match percentage (0.0 = no match, 1.0 = perfect match).
        jd_requirements: All skills extracted from JD, grouped by category.
        cv_skills: All skills from CV, grouped by category.
    """
    matched_skills: dict[str, List[str]] = Field(
        default_factory=dict,
        description="Skills found in both CV and JD"
    )
    missing_skills: dict[str, List[str]] = Field(
        default_factory=dict,
        description="JD requirements missing from CV"
    )
    extra_skills: dict[str, List[str]] = Field(
        default_factory=dict,
        description="CV skills not in JD requirements"
    )
    skill_match_rate: float = Field(
        ge=0.0, le=1.0,
        description="Match rate (0.0-1.0)"
    )
    jd_requirements: dict[str, List[str]] = Field(
        default_factory=dict,
        description="All skills extracted from JD"
    )
    cv_skills: dict[str, List[str]] = Field(
        default_factory=dict,
        description="All skills from CV"
    )
    
    @computed_field
    @property
    def match_percentage(self) -> float:
        """Calculate match percentage (0-100) for display."""
        return round(self.skill_match_rate * 100, 2)
    
    @field_validator('skill_match_rate')
    @classmethod
    def validate_match_rate_range(cls, v: float) -> float:
        """Ensure skill_match_rate is within valid range."""
        if not 0.0 <= v <= 1.0:
            raise ValueError('skill_match_rate must be between 0.0 and 1.0')
        return v