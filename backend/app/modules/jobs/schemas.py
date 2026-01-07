from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID
from enum import Enum

from pydantic import BaseModel, Field, field_validator, model_validator


class LocationType(str, Enum):
    """Work location type for job descriptions."""
    REMOTE = "remote"
    HYBRID = "hybrid"
    ON_SITE = "on-site"


class JDParseStatus(str, Enum):
    """Status of JD parsing process."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ParsedJDRequirements(BaseModel):
    """
    Schema for parsed JD requirements extracted by AI.
    
    This is stored in the `parsed_requirements` JSONB field of JobDescription.
    """
    required_skills: List[str] = Field(
        default_factory=list,
        description="List of normalized required skill names"
    )
    nice_to_have_skills: List[str] = Field(
        default_factory=list,
        description="List of normalized optional/nice-to-have skill names"
    )
    min_experience_years: Optional[int] = Field(
        default=None,
        ge=0,
        description="Minimum years of experience required"
    )
    job_title_normalized: Optional[str] = Field(
        default=None,
        description="Normalized job title (e.g., 'Senior Python Developer')"
    )
    key_responsibilities: List[str] = Field(
        default_factory=list,
        description="Key job responsibilities (max 5)"
    )
    skill_categories: Optional[Dict[str, List[str]]] = Field(
        default=None,
        description="Skills organized by category for analysis"
    )

    model_config = {"from_attributes": True}


class ParsedRequirementsUpdate(BaseModel):
    """
    Schema for updating parsed JD requirements.
    
    All fields are optional - only provided fields will be updated.
    This allows partial updates to the parsed_requirements JSONB field.
    """
    required_skills: Optional[List[str]] = Field(
        default=None,
        description="List of required skill names"
    )
    nice_to_have_skills: Optional[List[str]] = Field(
        default=None,
        description="List of optional/nice-to-have skill names"
    )
    min_experience_years: Optional[int] = Field(
        default=None,
        ge=0,
        description="Minimum years of experience required"
    )

    @field_validator("required_skills", "nice_to_have_skills")
    @classmethod
    def validate_skills_list(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        """Validate that skills lists contain non-empty strings if provided."""
        if v is None:
            return v
        # Filter out empty strings and strip whitespace
        validated = [skill.strip() for skill in v if skill and skill.strip()]
        return validated

    model_config = {"from_attributes": True}


class JobDescriptionBase(BaseModel):
    """Base schema for JobDescription with common fields."""

    title: str = Field(..., min_length=1, max_length=255, description="Job title")
    description: str = Field(..., min_length=1, description="Full job description")
    required_skills: Optional[List[str]] = Field(
        default=None, description="List of required skills"
    )
    min_experience_years: Optional[int] = Field(
        default=None, ge=0, description="Minimum years of experience required"
    )
    location_type: LocationType = Field(
        default=LocationType.REMOTE, description="Work location type"
    )
    salary_min: Optional[int] = Field(
        default=None, ge=0, description="Minimum salary"
    )
    salary_max: Optional[int] = Field(
        default=None, ge=0, description="Maximum salary"
    )
    benefits: Optional[List[str]] = Field(
        default=None, description="List of benefits (e.g., Insurance, Training)"
    )

    @field_validator("salary_max")
    @classmethod
    def salary_max_must_be_greater_than_min(cls, v: Optional[int], info) -> Optional[int]:
        """Validate that salary_max is greater than or equal to salary_min."""
        if v is not None and info.data.get("salary_min") is not None:
            if v < info.data["salary_min"]:
                raise ValueError("salary_max must be greater than or equal to salary_min")
        return v


class JobDescriptionCreate(JobDescriptionBase):
    """Schema for creating a new JobDescription."""
    pass


class JobDescriptionFileUploadForm(BaseModel):
    """Schema for JD file upload form data (for documentation)."""
    
    title: str = Field(..., min_length=1, max_length=255, description="Job title")
    location_type: LocationType = Field(
        default=LocationType.REMOTE, description="Work location type"
    )
    required_skills: Optional[List[str]] = Field(
        default=None, description="List of required skills"
    )
    min_experience_years: Optional[int] = Field(
        default=None, ge=0, description="Minimum years of experience required"
    )
    salary_min: Optional[int] = Field(
        default=None, ge=0, description="Minimum salary"
    )
    salary_max: Optional[int] = Field(
        default=None, ge=0, description="Maximum salary"
    )


class JobDescriptionUpdate(BaseModel):
    """Schema for updating an existing JobDescription."""

    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, min_length=1)
    required_skills: Optional[List[str]] = None
    min_experience_years: Optional[int] = Field(default=None, ge=0)
    location_type: Optional[LocationType] = None
    salary_min: Optional[int] = Field(default=None, ge=0)
    salary_max: Optional[int] = Field(default=None, ge=0)
    is_active: Optional[bool] = None


class JobDescriptionResponse(BaseModel):
    """Schema for JobDescription response."""

    id: UUID
    user_id: int
    title: str
    description: str
    uploaded_at: datetime
    is_active: bool
    required_skills: Optional[List[str]] = None
    min_experience_years: Optional[int] = None
    location_type: str
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    parse_status: str = Field(default="pending", description="JD parsing status")
    parsed_requirements: Optional[ParsedJDRequirements] = None

    model_config = {"from_attributes": True}


class JDParseStatusResponse(BaseModel):
    """Response schema for parse status endpoint."""
    
    jd_id: UUID
    parse_status: str
    parsed_requirements: Optional[ParsedJDRequirements] = None
    parse_error: Optional[str] = None
    
    model_config = {"from_attributes": True}


class BasicJobSearchRequest(BaseModel):
    """Request schema for basic job search."""
    query: str = Field(..., min_length=1, description="Search query for job titles or keywords")
    location: Optional[str] = Field(default=None, description="Location for job search")
    location_type: Optional[LocationType] = Field(default=None, description="Work location type")
    min_salary: Optional[int] = Field(default=None, ge=0, description="Minimum salary")
    max_salary: Optional[int] = Field(default=None, ge=0, description="Maximum salary")
    min_experience_years: Optional[int] = Field(default=None, ge=0, description="Minimum years of experience")
    required_skills: Optional[List[str]] = Field(default=None, description="List of required skills")
    benefits: Optional[List[str]] = Field(default=None, description="List of benefits to filter by")
    limit: int = Field(default=20, ge=1, le=100, description="Maximum number of results to return")
    offset: int = Field(default=0, ge=0, description="Number of results to skip for pagination")


class BasicJobSearchItemResponse(BaseModel):
    """Schema for a single job item in basic search results."""
    id: UUID
    title: str
    description: str
    location_type: LocationType
    salary_min: Optional[int]
    salary_max: Optional[int]
    benefits: Optional[List[str]] = None

    model_config = {"from_attributes": True}


class JobDescriptionList(BaseModel):
    """Schema for list of JobDescriptions."""

    items: List[JobDescriptionResponse]
    total: int


# ============================================================================
# Candidate Ranking Schemas
# ============================================================================


class MatchBreakdownResponse(BaseModel):
    """Detailed breakdown of match between CV and JD."""

    matched_skills: List[str] = Field(
        default_factory=list,
        description="Skills from JD that candidate has"
    )
    missing_skills: List[str] = Field(
        default_factory=list,
        description="Required skills from JD that candidate lacks"
    )
    extra_skills: List[str] = Field(
        default_factory=list,
        description="Additional skills candidate has beyond JD requirements"
    )
    skill_score: float = Field(
        default=0.0,
        ge=0,
        le=70,
        description="Score from skill matching (0-70)"
    )
    experience_score: float = Field(
        default=0.0,
        ge=0,
        le=30,
        description="Score from experience matching (0-30)"
    )
    experience_years: Optional[int] = Field(
        default=None,
        description="Candidate's years of experience (if available)"
    )
    required_experience_years: Optional[int] = Field(
        default=None,
        description="JD's required years of experience (if specified)"
    )

    model_config = {"from_attributes": True}


class RankedCandidateResponse(BaseModel):
    """A candidate with match score and breakdown."""
    
    cv_id: UUID = Field(description="CV unique identifier")
    user_id: int = Field(description="User ID who owns this CV")
    match_score: int = Field(
        ge=0,
        le=100,
        description="Overall match score (0-100)"
    )
    breakdown: MatchBreakdownResponse = Field(
        description="Detailed breakdown of the match"
    )
    cv_summary: Optional[str] = Field(
        default=None,
        description="AI-generated summary of the CV"
    )
    filename: Optional[str] = Field(
        default=None,
        description="Original filename of the CV"
    )
    is_public: bool = Field(
        default=False,
        description="Whether the CV is public and viewable by recruiters"
    )
    
    model_config = {"from_attributes": True}


class RankedCandidateListResponse(BaseModel):
    """Paginated list of ranked candidates."""
    
    items: List[RankedCandidateResponse] = Field(
        default_factory=list,
        description="List of ranked candidates"
    )
    total: int = Field(
        ge=0,
        description="Total number of candidates (before pagination)"
    )
    limit: int = Field(
        ge=1,
        description="Maximum number of items per page"
    )
    offset: int = Field(
        ge=0,
        description="Number of items skipped"
    )
    
    model_config = {"from_attributes": True}


# ============================================================================
# Semantic Search Schemas
# ============================================================================


class SemanticSearchRequest(BaseModel):
    """Request schema for semantic candidate search."""
    
    query: str = Field(
        ...,
        min_length=2,
        description="Natural language search query (e.g., 'Python developer with AWS experience')"
    )
    limit: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Maximum number of results to return (default: 20, max: 100)"
    )
    offset: int = Field(
        default=0,
        ge=0,
        description="Number of results to skip for pagination (default: 0)"
    )
    min_score: int = Field(
        default=0,
        ge=0,
        le=100,
        description="Minimum relevance score to include (0-100, default: 0)"
    )
    
    @field_validator("query")
    @classmethod
    def validate_query(cls, v: str) -> str:
        """Validate that query is not empty or whitespace-only."""
        if not v or not v.strip():
            raise ValueError("Query cannot be empty or whitespace-only")
        return v.strip()
    
    model_config = {"from_attributes": True}


class ParsedQueryResponse(BaseModel):
    """Response schema for parsed query information."""
    
    extracted_skills: List[str] = Field(
        default_factory=list,
        description="Skills extracted from the search query"
    )
    experience_keywords: List[str] = Field(
        default_factory=list,
        description="Experience-related keywords from the query"
    )
    raw_query: str = Field(
        default="",
        description="Original search query"
    )
    
    model_config = {"from_attributes": True}


class SearchResultResponse(BaseModel):
    """Response schema for a single search result."""
    
    cv_id: UUID = Field(description="CV unique identifier")
    user_id: int = Field(description="User ID who owns this CV")
    relevance_score: int = Field(
        ge=0,
        le=100,
        description="Relevance score (0-100)"
    )
    matched_skills: List[str] = Field(
        default_factory=list,
        description="Skills from query that match the CV"
    )
    cv_summary: Optional[str] = Field(
        default=None,
        description="AI-generated summary of the CV"
    )
    filename: Optional[str] = Field(
        default=None,
        description="Original filename of the CV"
    )
    
    model_config = {"from_attributes": True}


class SearchResultListResponse(BaseModel):
    """Paginated list of search results."""
    
    items: List[SearchResultResponse] = Field(
        default_factory=list,
        description="List of search results"
    )
    total: int = Field(
        ge=0,
        description="Total number of matching candidates (before pagination)"
    )
    limit: int = Field(
        ge=1,
        description="Maximum number of items per page"
    )
    offset: int = Field(
        ge=0,
        description="Number of items skipped"
    )
    parsed_query: ParsedQueryResponse = Field(
        description="Information about how the query was parsed"
    )
    
    model_config = {"from_attributes": True}


# ============================================================================
# Recruiter CV Access Schemas
# ============================================================================


class RecruiterCVAccessResponse(BaseModel):
    """Response schema for recruiter accessing a candidate's CV."""
    
    cv_id: UUID = Field(description="CV unique identifier")
    filename: str = Field(description="Original filename of the CV")
    uploaded_at: datetime = Field(description="When the CV was uploaded")
    
    # Analysis data
    ai_score: Optional[int] = Field(
        default=None,
        description="AI-generated quality score (0-100)"
    )
    ai_summary: Optional[str] = Field(
        default=None,
        description="AI-generated summary of the CV"
    )
    extracted_skills: Optional[List[str]] = Field(
        default=None,
        description="Skills extracted from the CV"
    )
    skill_breakdown: Optional[Dict] = Field(
        default=None,
        description="Detailed skill scoring breakdown"
    )
    skill_categories: Optional[Dict] = Field(
        default=None,
        description="Skills organized by category"
    )
    
    # Match context (if applicable)
    match_score: Optional[int] = Field(
        default=None,
        description="Match score against the JD (0-100)"
    )
    matched_skills: Optional[List[str]] = Field(
        default=None,
        description="Skills matching the JD requirements"
    )
    
    model_config = {"from_attributes": True}


class CandidateCVFromSearchResponse(BaseModel):
    """Response schema for accessing a candidate's CV from search results (no JD context)."""
    
    cv_id: UUID = Field(description="CV unique identifier")
    filename: str = Field(description="Original filename of the CV")
    uploaded_at: datetime = Field(description="When the CV was uploaded")
    
    # Analysis data
    ai_score: Optional[int] = Field(
        default=None,
        description="AI-generated quality score (0-100)"
    )
    ai_summary: Optional[str] = Field(
        default=None,
        description="AI-generated summary of the CV"
    )
    extracted_skills: Optional[List[str]] = Field(
        default=None,
        description="Skills extracted from the CV"
    )
    skill_breakdown: Optional[Dict] = Field(
        default=None,
        description="Detailed skill scoring breakdown"
    )
    skill_categories: Optional[Dict] = Field(
        default=None,
        description="Skills organized by category"
    )
    
    # Visibility info
    is_public: bool = Field(
        default=False,
        description="Whether the CV is public"
    )

    model_config = {"from_attributes": True}


# ============================================================================
# Story 5.7: Job Match Score Schemas
# ============================================================================


class JobMatchRequest(BaseModel):
    """Request schema for job match score calculation."""

    cv_id: UUID = Field(
        description="CV unique identifier to calculate match score for"
    )

    model_config = {"from_attributes": True}


class JobMatchResponse(BaseModel):
    """Response schema for job match score calculation."""

    cv_id: UUID = Field(description="CV unique identifier")
    job_id: UUID = Field(description="Job description unique identifier")
    job_match_score: int = Field(
        ge=0,
        le=100,
        description="Job match score (0-100) prioritizing JD skill requirements"
    )

    model_config = {"from_attributes": True}


# ============================================================================
# Story 9.1: Basic Job Search Schemas
# ============================================================================


class BasicJobSearchRequest(BaseModel):
    """Request schema for basic job search by job seekers."""
    
    keyword: Optional[str] = Field(
        default=None,
        description="Search keyword to match in job title or description"
    )
    location: Optional[str] = Field(
        default=None,
        description="Location type filter: remote, hybrid, or on-site"
    )
    limit: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Maximum number of results to return (default: 20, max: 100)"
    )
    offset: int = Field(
        default=0,
        ge=0,
        description="Number of results to skip for pagination (default: 0)"
    )
    # Story 9.2: Advanced filters
    min_salary: Optional[int] = Field(
        default=None,
        ge=0,
        description="Minimum salary filter"
    )
    max_salary: Optional[int] = Field(
        default=None,
        ge=0,
        description="Maximum salary filter"
    )
    job_types: Optional[List[str]] = Field(
        default=None,
        description="List of job types to filter (e.g., full-time, part-time)"
    )
    
    @field_validator("location")
    @classmethod
    def validate_location(cls, v: Optional[str]) -> Optional[str]:
        """Validate location type if provided."""
        if v is not None:
            valid_locations = ["remote", "hybrid", "on-site"]
            if v.lower() not in valid_locations:
                raise ValueError(f"Location must be one of: {', '.join(valid_locations)}")
            return v.lower()
        return v
        
    @model_validator(mode='after')
    def validate_salary_range(self) -> 'BasicJobSearchRequest':
        """Validate that max_salary is greater than or equal to min_salary if both are provided."""
        if self.min_salary is not None and self.max_salary is not None:
            if self.max_salary < self.min_salary:
                raise ValueError("max_salary must be greater than or equal to min_salary")
        return self
    
        return self
    
    @field_validator("job_types")
    @classmethod
    def validate_job_types(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        """Validate job types if provided."""
        if v is not None:
            valid_types = ["full-time", "part-time", "contract", "internship", "freelance"]
            invalid_types = [t for t in v if t.lower() not in valid_types]
            if invalid_types:
                raise ValueError(f"Invalid job types: {', '.join(invalid_types)}. Valid types are: {', '.join(valid_types)}")
            return [t.lower() for t in v]
        return v
    
    model_config = {"from_attributes": True}


class BasicJobSearchItemResponse(BaseModel):
    """Response schema for a single job in basic search results."""
    
    id: UUID = Field(description="Job unique identifier")
    title: str = Field(description="Job title")
    description: str = Field(description="Job description (truncated for list view)")
    location_type: str = Field(description="Work location type")
    uploaded_at: datetime = Field(description="When the job was posted")
    salary_min: Optional[int] = Field(default=None, description="Minimum salary")
    salary_max: Optional[int] = Field(default=None, description="Maximum salary")
    job_type: Optional[str] = Field(default=None, description="Employment type (full-time, part-time, etc.)")
    
    model_config = {"from_attributes": True}


class BasicJobSearchResponse(BaseModel):
    """Response schema for basic job search results."""
    
    items: List[BasicJobSearchItemResponse] = Field(
        default_factory=list,
        description="List of matching jobs"
    )
    total: int = Field(
        ge=0,
        description="Total number of matching jobs (before pagination)"
    )
    limit: int = Field(
        ge=1,
        description="Maximum number of items per page"
    )
    offset: int = Field(
        ge=0,
        description="Number of items skipped"
    )
    
    model_config = {"from_attributes": True}

class SkillSuggestion(BaseModel):
    skill: str
    count: int

class SkillSuggestionResponse(BaseModel):
    suggestions: List[SkillSuggestion]


class ApplicationBase(BaseModel):
    cover_letter: Optional[str] = Field(None, description="Optional cover letter")

class ApplicationCreate(ApplicationBase):
    cv_id: UUID = Field(..., description="ID of the CV to apply with")

class ApplicationResponse(ApplicationBase):
    id: UUID
    job_id: UUID
    user_id: int
    cv_id: Optional[UUID]
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class JobRecommendationResponse(BaseModel):
    """Schema for a recommended job."""
    
    id: UUID = Field(description="Job unique identifier")
    title: str = Field(description="Job title")
    description: str = Field(description="Job description (truncated)")
    location_type: str = Field(description="Work location type")
    salary_min: Optional[int] = Field(default=None, description="Minimum salary")
    salary_max: Optional[int] = Field(default=None, description="Maximum salary")
    
    match_score: int = Field(ge=0, le=100, description="Overall match score (0-100)")
    semantic_score: Optional[float] = Field(default=0.0, description="Semantic vector similarity score (0-1)")
    
    # Matching breakdown
    matched_skills: List[str] = Field(default_factory=list, description="Skills matching the user's CV")
    missing_skills: List[str] = Field(default_factory=list, description="Required skills missing from CV")
    
    uploaded_at: datetime = Field(description="When the job was posted")

    model_config = {"from_attributes": True}
