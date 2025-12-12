import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any

from pydantic import BaseModel, computed_field


class ExperienceBreakdown(BaseModel):
    total_years: int = 0
    key_roles: List[str] = []
    industries: List[str] = []


class CriteriaExplanation(BaseModel):
    completeness: int = 50
    experience: int = 50
    skills: int = 50
    professionalism: int = 50


class AnalysisResult(BaseModel):
    id: uuid.UUID
    cv_id: uuid.UUID
    status: str
    ai_score: Optional[int] = None
    ai_summary: Optional[str] = None
    ai_feedback: Optional[dict] = None
    extracted_skills: Optional[List[str]] = None
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