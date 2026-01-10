"""
FastAPI router for Epic 8: Virtual AI Interview Room.

Provides endpoints for:
- Creating interview sessions with AI question generation
- Processing conversation turns with real-time evaluation
- Completing interviews and generating final evaluation reports
- Retrieving interview history and statistics
"""
import logging
from uuid import UUID
from typing import List

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.auth.dependencies import get_current_user, require_job_seeker
from app.modules.users.models import User
from app.modules.interviews.schemas import (
    InterviewSessionCreate,
    InterviewSessionResponse,
    InterviewSessionWithQuestions,
    InterviewSessionListResponse,
    InterviewQuestionResponse,
    InterviewTurnCreate,
    InterviewTurnResponse,
    InterviewTurnListResponse,
    InterviewEvaluationResponse,
    InterviewCompleteRequest,
    InterviewCreateResponse,
    InterviewCompleteResponse,
    InterviewSessionComplete,
    ProcessTurnResponse,
)
from app.modules.interviews.service import (
    InterviewService,
    ConversationService,
    EvaluationService,
)

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize services
interview_service = InterviewService()
# Note: ConversationService requires db session, initialized per-request
evaluation_service = EvaluationService()


@router.post("", response_model=InterviewCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_interview(
    request: InterviewSessionCreate,
    current_user: User = Depends(require_job_seeker),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new interview session and generate questions using AI.
    
    This endpoint:
    1. Creates an interview session record
    2. Calls QuestionCraft AI to generate personalized questions
    3. Returns the session with all generated questions
    
    **Performance:** ~3-5 seconds (AI generation time)
    
    **Requirements:**
    - User must be authenticated as job seeker (candidate role)
    - Job description must be at least 10 characters
    - CV content must be at least 10 characters
    - Position level: junior, middle, or senior
    - Number of questions: 5-15 (default 10)
    """
    # Job seeker role enforced by dependency
    
    try:
        session, questions = await interview_service.create_interview(
            db=db,
            candidate_id=current_user.id,
            request=request
        )
        
        return InterviewCreateResponse(
            session=InterviewSessionResponse.model_validate(session),
            questions=[InterviewQuestionResponse.model_validate(q) for q in questions],
            message=f"Interview session created with {len(questions)} questions"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create interview session: {str(e)}"
        )


@router.get("", response_model=InterviewSessionListResponse)
async def list_interviews(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get list of interview sessions for the current user.
    
    Returns paginated list of interviews ordered by creation date (newest first).
    Only shows sessions belonging to the authenticated user.
    """
    if current_user.role != "candidate":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only candidates can view interview sessions"
        )
    
    sessions, total = await interview_service.list_sessions(
        db=db,
        candidate_id=current_user.id,
        skip=skip,
        limit=limit
    )
    
    return InterviewSessionListResponse(
        sessions=[InterviewSessionResponse.model_validate(s) for s in sessions],
        total=total
    )


@router.get("/{session_id}", response_model=InterviewSessionComplete)
async def get_interview(
    session_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get detailed interview session with questions, turns, and evaluation.
    
    Returns complete interview data including:
    - Session metadata (status, timestamps, duration)
    - All generated questions
    - Conversation history (all Q&A turns)
    - Final evaluation report (if completed)
    """
    if current_user.role != "candidate":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only candidates can view interview sessions"
        )
    
    session = await interview_service.get_session(
        db=db,
        session_id=session_id,
        candidate_id=current_user.id
    )
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Interview session {session_id} not found"
        )
    
    return InterviewSessionComplete.model_validate(session)


@router.get("/{session_id}/questions", response_model=List[InterviewQuestionResponse])
async def get_interview_questions(
    session_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all questions for an interview session.
    
    Returns the list of AI-generated questions in order.
    """
    if current_user.role != "candidate":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only candidates can view interview questions"
        )
    
    session = await interview_service.get_session(
        db=db,
        session_id=session_id,
        candidate_id=current_user.id
    )
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Interview session {session_id} not found"
        )
    
    return [InterviewQuestionResponse.model_validate(q) for q in session.questions]


@router.post("/{session_id}/turns", response_model=ProcessTurnResponse)
async def process_interview_turn(
    session_id: UUID,
    request: InterviewTurnCreate,
    current_user: User = Depends(require_job_seeker),
    db: AsyncSession = Depends(get_db),
):
    """
    Process a conversation turn (candidate answer) with real-time AI evaluation via DialogFlow AI.
    
    This endpoint:
    1. Receives candidate's answer (transcribed from voice or typed)
    2. Validates interview session ownership and status
    3. Calls DialogFlow AI agent (Qwen2.5-1.5B) to evaluate the answer
    4. Generates AI response (follow-up question or feedback)
    5. Determines next action (continue, ask follow-up, move to next question, end)
    6. Saves turn data with scores to database
    7. Logs agent call metrics for monitoring
    
    **Performance Target:** ~2-3 seconds (AI evaluation time, P95)
    
    **Real-time features:**
    - Per-turn scoring (technical accuracy, communication, depth)
    - Immediate feedback on answer quality
    - Smart follow-up questions based on answer quality
    - Context-aware conversation flow management
    
    **Error Handling:**
    - 403: User doesn't own the interview session
    - 400: Session in invalid state or bad input
    - 503: Ollama/AI service unavailable
    - 500: Unexpected server error
    """
    
    # Dependency already enforces job_seeker role
    
    # Initialize conversation service with db session
    conversation_service_instance = ConversationService(db=db)
    
    try:
        turn_response = await conversation_service_instance.process_turn(
            session_id=session_id,
            current_question_id=request.current_question_id,
            candidate_answer=request.candidate_message,
            user_id=current_user.id,
        )
        
        return ProcessTurnResponse(**turn_response)
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"AI service unavailable: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error processing turn for session {session_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process interview turn: {str(e)}"
        )


@router.get("/{session_id}/turns", response_model=InterviewTurnListResponse)
async def get_interview_turns(
    session_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all conversation turns for an interview session.
    
    Returns complete dialogue history with AI evaluations.
    """
    if current_user.role != "candidate":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only candidates can view interview turns"
        )
    
    session = await interview_service.get_session(
        db=db,
        session_id=session_id,
        candidate_id=current_user.id
    )
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Interview session {session_id} not found"
        )
    
    return InterviewTurnListResponse(
        turns=[InterviewTurnResponse.model_validate(t) for t in session.turns],
        total=len(session.turns)
    )


@router.post("/{session_id}/complete", response_model=InterviewCompleteResponse)
async def complete_interview(
    session_id: UUID,
    request: InterviewCompleteRequest = InterviewCompleteRequest(),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Complete interview and generate final evaluation report.
    
    This endpoint:
    1. Marks interview session as completed
    2. Calls EvalMaster AI to analyze entire interview
    3. Generates comprehensive evaluation with:
       - Final score (0-10)
       - Grade (excellent, good, average, poor)
       - Hiring recommendation (strong_hire, hire, consider, no_hire)
       - 3-dimension scoring breakdown
       - Detailed strengths/weaknesses analysis
       - Notable moments and red flags
       - Development suggestions
    
    **Performance:** ~5-8 seconds (comprehensive AI analysis)
    
    **Requirements:**
    - Interview must be in 'in_progress' status
    - At least 3 conversation turns recommended (can be forced)
    """
    if current_user.role != "candidate":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only candidates can complete interviews"
        )
    
    # Verify session belongs to user
    session = await interview_service.get_session(
        db=db,
        session_id=session_id,
        candidate_id=current_user.id
    )
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Interview session {session_id} not found"
        )
    
    if session.status == "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Interview already completed"
        )
    
    if len(session.turns) < 3 and not request.force_complete:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Interview must have at least 3 turns. Use force_complete=true to override."
        )
    
    try:
        evaluation = await evaluation_service.generate_evaluation(
            db=db,
            session_id=session_id
        )
        
        # Refresh session to get updated status
        await db.refresh(session)
        
        return InterviewCompleteResponse(
            session=InterviewSessionResponse.model_validate(session),
            evaluation=InterviewEvaluationResponse.model_validate(evaluation),
            message="Interview completed successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to complete interview: {str(e)}"
        )


@router.get("/{session_id}/evaluation", response_model=InterviewEvaluationResponse)
async def get_interview_evaluation(
    session_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get evaluation report for a completed interview.
    
    Returns comprehensive analysis including scores, recommendations, and feedback.
    Only available after interview is completed.
    """
    if current_user.role != "candidate":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only candidates can view interview evaluations"
        )
    
    session = await interview_service.get_session(
        db=db,
        session_id=session_id,
        candidate_id=current_user.id
    )
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Interview session {session_id} not found"
        )
    
    if not session.evaluation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evaluation not found. Complete the interview first."
        )
    
    return InterviewEvaluationResponse.model_validate(session.evaluation)
