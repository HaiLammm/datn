"""
Pydantic schemas for Epic 8: Virtual AI Interview Room.

Request and response schemas for interview API endpoints.
"""
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


# ============ Interview Session Schemas ============


class InterviewSessionCreate(BaseModel):
    """Request schema for creating a new interview session."""
    
    job_description: str = Field(..., min_length=10, description="Job description text")
    cv_content: str = Field(..., min_length=10, description="Candidate's CV content")
    position_level: str = Field(..., description="Position level: junior, middle, senior")
    num_questions: int = Field(default=10, ge=5, le=15, description="Number of questions to generate")
    focus_areas: Optional[List[str]] = Field(default=None, description="Optional focus areas for questions")
    
    @field_validator("position_level")
    @classmethod
    def validate_position_level(cls, v: str) -> str:
        allowed = ["junior", "middle", "senior"]
        if v.lower() not in allowed:
            raise ValueError(f"position_level must be one of: {', '.join(allowed)}")
        return v.lower()


class InterviewSessionResponse(BaseModel):
    """Response schema for interview session."""
    
    id: UUID
    candidate_id: int
    job_posting_id: Optional[UUID] = None
    status: str
    scheduled_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class InterviewSessionWithQuestions(InterviewSessionResponse):
    """Response schema for session with generated questions."""
    
    questions: List["InterviewQuestionResponse"]


class InterviewSessionListResponse(BaseModel):
    """Response schema for list of interview sessions."""
    
    sessions: List[InterviewSessionResponse]
    total: int


# ============ Interview Question Schemas ============


class InterviewQuestionResponse(BaseModel):
    """Response schema for interview question."""
    
    id: UUID
    interview_session_id: UUID
    question_id: str
    category: str
    difficulty: str
    question_text: str
    key_points: Optional[List[str]] = None
    ideal_answer_outline: Optional[str] = None
    evaluation_criteria: Optional[List[str]] = None
    order_index: int
    is_selected: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============ Interview Turn Schemas ============


class InterviewTurnCreate(BaseModel):
    """Request schema for processing a conversation turn."""
    
    current_question_id: UUID = Field(..., description="Current question UUID being answered")
    candidate_message: str = Field(..., min_length=1, max_length=10000, description="Candidate's answer (transcribed from voice)")


class TurnEvaluation(BaseModel):
    """Schema for per-turn answer evaluation scores."""
    
    technical_score: float = Field(..., ge=0, le=10, description="Technical accuracy score")
    communication_score: float = Field(..., ge=0, le=10, description="Communication clarity score")
    depth_score: float = Field(..., ge=0, le=10, description="Depth of knowledge score")
    overall_score: float = Field(..., ge=0, le=10, description="Overall turn score")


class NextAction(BaseModel):
    """Schema for AI's next action decision."""
    
    action_type: str = Field(..., description="Action type: 'follow_up', 'continue', 'next_question', 'end'")
    ai_response: str = Field(..., description="AI's verbal response to candidate")
    follow_up_question: Optional[str] = Field(None, description="Follow-up question if action_type is 'follow_up'")


class ContextUpdate(BaseModel):
    """Schema for conversation context updates."""
    
    topics_covered: List[str] = Field(default_factory=list, description="Topics covered so far")
    follow_up_depth: int = Field(default=0, ge=0, description="Current follow-up depth level")
    turn_count: int = Field(..., ge=1, description="Total number of turns in conversation")


class ProcessTurnResponse(BaseModel):
    """Response schema for processing a conversation turn via DialogFlow AI."""
    
    turn_evaluation: TurnEvaluation
    next_action: NextAction
    context_update: ContextUpdate
    turn_id: UUID = Field(..., description="UUID of the saved turn record")


class AnswerQuality(BaseModel):
    """Schema for answer quality scores (legacy - kept for backwards compatibility)."""
    
    technical_accuracy: float = Field(..., ge=0, le=10)
    communication_clarity: float = Field(..., ge=0, le=10)
    depth_of_knowledge: float = Field(..., ge=0, le=10)
    overall_score: float = Field(..., ge=0, le=10)


class InterviewTurnResponse(BaseModel):
    """Response schema for conversation turn."""
    
    id: UUID
    interview_session_id: UUID
    question_id: Optional[UUID] = None
    turn_number: int
    ai_message: str
    candidate_message: str
    answer_quality: Optional[AnswerQuality] = None
    key_observations: Optional[List[str]] = None
    strengths: Optional[List[str]] = None
    gaps: Optional[List[str]] = None
    action_type: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class InterviewTurnListResponse(BaseModel):
    """Response schema for list of conversation turns."""
    
    turns: List[InterviewTurnResponse]
    total: int


# ============ Interview Evaluation Schemas ============


class DimensionScore(BaseModel):
    """Schema for dimension scoring structure."""
    
    technical_competence: Dict[str, float]  # {technical_accuracy, problem_solving, depth_of_knowledge}
    communication_skills: Dict[str, float]  # {clarity, professionalism, engagement}
    behavioral_fit: Dict[str, float]  # {cultural_alignment, soft_skills, motivation}


class DetailedAnalysis(BaseModel):
    """Schema for detailed analysis structure."""
    
    strengths: List[str]
    weaknesses: List[str]
    notable_moments: List[str]
    red_flags: Optional[List[str]] = None


class Recommendations(BaseModel):
    """Schema for recommendations structure."""
    
    hiring_decision: str
    reasoning: str
    development_suggestions: Optional[List[str]] = None


class InterviewEvaluationResponse(BaseModel):
    """Response schema for interview evaluation."""
    
    id: UUID
    interview_session_id: UUID
    final_score: Decimal
    grade: str
    hiring_recommendation: str
    dimension_scores: DimensionScore
    detailed_analysis: DetailedAnalysis
    recommendations: Recommendations
    evaluation_metadata: Optional[Dict] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============ Agent Call Log Schemas ============


class AgentCallLogResponse(BaseModel):
    """Response schema for agent call log."""
    
    id: UUID
    agent_type: str
    interview_session_id: Optional[UUID] = None
    status: str
    error_message: Optional[str] = None
    latency_ms: Optional[int] = None
    model_used: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============ Combined Response Schemas ============


class InterviewSessionComplete(InterviewSessionResponse):
    """Complete interview session with all related data."""
    
    questions: List[InterviewQuestionResponse]
    turns: List[InterviewTurnResponse]
    evaluation: Optional[InterviewEvaluationResponse] = None


class InterviewCreateResponse(BaseModel):
    """Response after creating interview with generated questions."""
    
    session: InterviewSessionResponse
    questions: List[InterviewQuestionResponse]
    message: str = "Interview session created successfully"


class InterviewCompleteRequest(BaseModel):
    """Request schema for completing an interview."""
    
    force_complete: bool = Field(
        default=False, 
        description="Force complete even if not all questions answered"
    )


class InterviewCompleteResponse(BaseModel):
    """Response after completing interview and generating evaluation."""
    
    session: InterviewSessionResponse
    evaluation: InterviewEvaluationResponse
    message: str = "Interview completed and evaluated successfully"


# ============ Statistics and Monitoring Schemas ============


class AgentPerformanceStats(BaseModel):
    """Statistics for agent performance monitoring."""
    
    agent_type: str
    total_calls: int
    success_count: int
    error_count: int
    avg_latency_ms: float
    success_rate: float


class InterviewStatistics(BaseModel):
    """Statistics for interview sessions."""
    
    total_sessions: int
    completed_sessions: int
    avg_duration_minutes: Optional[float] = None
    avg_final_score: Optional[float] = None
    completion_rate: float
