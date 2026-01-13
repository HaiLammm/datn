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
from typing import List, Optional

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
    InterviewStatusResponse,
    # Story 8.4: History schemas
    InterviewSessionSummary,
    InterviewSessionDetail,
    PaginatedInterviewSessions,
    InterviewTranscriptResponse,
    InterviewEvaluationDetail,
)
from app.modules.interviews.service import (
    InterviewService,
    ConversationService,
    EvaluationService,
)
from app.modules.interviews.history_service import HistoryService

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize services
interview_service = InterviewService()
history_service = HistoryService()
# Note: ConversationService requires db session, initialized per-request
evaluation_service = EvaluationService()


@router.post("", response_model=InterviewCreateResponse, status_code=status.HTTP_202_ACCEPTED)
async def create_interview(
    request: InterviewSessionCreate,
    current_user: User = Depends(require_job_seeker),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new interview session and trigger async question generation.
    
    This endpoint (UPDATED FOR ASYNC):
    1. Creates an interview session record with status='pending'
    2. Triggers background Celery task to generate questions
    3. Returns immediately with session_id (non-blocking)
    
    **Performance:** ~200ms (immediate response)
    **Question Generation:** 3-5 minutes in background
    
    **Requirements:**
    - User must be authenticated as job seeker (candidate role)
    - Job description must be at least 10 characters
    - CV content must be at least 10 characters
    - Position level: junior, middle, or senior
    - Number of questions: 5-15 (default 10)
    
    **Status Flow:**
    - 'pending' → 'generating' → 'ready' (success) OR 'error' (failure)
    
    **Next Step:**
    - Poll GET /interviews/{id}/status to check when ready
    """
    # Job seeker role enforced by dependency
    
    try:
        session = await interview_service.create_interview_async(
            db=db,
            candidate_id=current_user.id,
            request=request
        )
        
        return InterviewCreateResponse(
            session=InterviewSessionResponse.model_validate(session),
            questions=[],  # Empty - questions are being generated
            message="Interview session created. Questions are being generated. Check status endpoint for progress."
        )
    except Exception as e:
        logger.error(f"Error creating interview session: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create interview session: {str(e)}"
        )


@router.get("", response_model=PaginatedInterviewSessions)
async def list_interviews(
    page: int = Query(default=1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(default=10, ge=1, le=50, description="Items per page"),
    sort_by: str = Query(default="created_at", description="Sort field: created_at, overall_score"),
    sort_order: str = Query(default="desc", description="Sort order: asc, desc"),
    status: Optional[str] = Query(default=None, description="Filter by status: active, completed, abandoned"),
    current_user: User = Depends(require_job_seeker),
    db: AsyncSession = Depends(get_db),
):
    """
    [Story 8.4] Get paginated list of interview sessions with filtering and sorting.
    
    Returns interview history with summary information for each session.
    
    **Query Parameters:**
    - page: Page number (1-indexed, default: 1)
    - page_size: Items per page (1-50, default: 10)
    - sort_by: Sort field ('created_at', 'overall_score')
    - sort_order: Sort direction ('asc', 'desc')
    - status: Filter by status ('active', 'completed', 'abandoned')
    
    **Performance Target:** <200ms (P95)
    """
    try:
        sessions, total = await history_service.get_interview_sessions(
            db=db,
            user_id=current_user.id,
            page=page,
            page_size=page_size,
            sort_by=sort_by,
            sort_order=sort_order,
            status_filter=status,
        )
        
        # Convert ORM to Pydantic with computed fields
        items = []
        for session in sessions:
            # Get question_count and turn_count using helper methods
            question_count = await history_service.count_question_for_session(db, session.id)
            turn_count = await history_service.count_turns_for_session(db, session.id)
            
            # Build summary dict with computed fields
            summary = InterviewSessionSummary(
                id=session.id,
                job_title=session.job_title or "Untitled Position",
                created_at=session.created_at,
                completed_at=session.completed_at,
                status=session.status,
                overall_score=session.overall_score,
                overall_grade=session.overall_grade,
                duration_minutes=session.duration_minutes,
                question_count=question_count,
                turn_count=turn_count,
            )
            items.append(summary)
        
        # Calculate total_pages
        total_pages = (total + page_size - 1) // page_size if total > 0 else 0
        
        return PaginatedInterviewSessions(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )
    except Exception as e:
        logger.error(f"Error listing interview sessions for user {current_user.id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve interview history: {str(e)}"
        )


@router.get("/{session_id}/status", response_model=InterviewStatusResponse)
async def get_interview_status(
    session_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Check the status of interview question generation (polling endpoint).
    
    This endpoint allows frontend to poll for status updates after creating
    an interview session asynchronously.
    
    **Status Values:**
    - 'pending': Session created, task not started yet
    - 'generating': AI is generating questions (in progress)
    - 'ready': Questions generated successfully, ready to start interview
    - 'error': Generation failed (see error_message)
    - 'in_progress': Interview started
    - 'completed': Interview finished
    
    **Polling Recommendation:**
    - Poll every 3 seconds
    - Max 60 attempts (3 minutes timeout)
    - Stop polling when status is 'ready', 'error', 'in_progress', or 'completed'
    """
    if current_user.role != "job_seeker":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only job seekers can view interview sessions"
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
    
    # Build response based on status
    response_data = {
        "session_id": session.id,
        "status": session.status,
        "error_message": session.error_message if hasattr(session, 'error_message') else None,
        "questions": None,
        "message": ""
    }
    
    if session.status == "pending":
        response_data["message"] = "Interview session created. Waiting for question generation to start..."
    elif session.status == "generating":
        response_data["message"] = "AI is generating personalized questions for you. This may take 2-3 minutes..."
    elif session.status == "ready":
        # Load questions
        response_data["questions"] = [
            InterviewQuestionResponse.model_validate(q) for q in session.questions
        ]
        response_data["message"] = f"Questions ready! {len(session.questions)} questions generated. You can start the interview now."
    elif session.status == "error":
        response_data["message"] = f"Failed to generate questions: {session.error_message}"
    elif session.status == "in_progress":
        response_data["message"] = "Interview in progress"
    elif session.status == "completed":
        response_data["message"] = "Interview completed"
    
    return InterviewStatusResponse(**response_data)


@router.get("/{session_id}/detail", response_model=InterviewSessionDetail)
async def get_interview_detail_view(
    session_id: UUID,
    current_user: User = Depends(require_job_seeker),
    db: AsyncSession = Depends(get_db),
):
    """
    [Story 8.4] Get interview session detail (metadata only, no questions/turns/evaluation).
    
    Returns session metadata for detail page header and overview tab.
    For full transcript and evaluation, use dedicated endpoints.
    
    **Performance Target:** <300ms (P95)
    
    **Authorization:** User must own the interview session.
    
    **Error Responses:**
    - 403 Forbidden: User doesn't own this session
    - 404 Not Found: Session not found
    """
    try:
        session = await history_service.get_interview_detail(
            db=db,
            session_id=session_id,
            user_id=current_user.id,
        )
        
        # Get counts for computed fields
        question_count = await history_service.count_question_for_session(db, session.id)
        turn_count = await history_service.count_turns_for_session(db, session.id)
        
        # Build detail response with computed fields
        detail = InterviewSessionDetail(
            id=session.id,
            job_title=session.job_title or "Untitled Position",
            job_description=session.job_description,
            position_level=session.position_level,
            created_at=session.created_at,
            completed_at=session.completed_at,
            status=session.status,
            duration_minutes=session.duration_minutes,
            overall_score=session.overall_score,
            overall_grade=session.overall_grade,
            hiring_recommendation=session.hiring_recommendation,
            question_count=question_count,
            turn_count=turn_count,
            total_turns=turn_count,  # Alias for backwards compatibility
        )
        
        return detail
    except HTTPException:
        # Re-raise HTTPExceptions from service layer
        raise
    except Exception as e:
        logger.error(f"Error fetching detail for session {session_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve interview details: {str(e)}"
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
    if current_user.role != "job_seeker":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only job seekers can view interview sessions"
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
    if current_user.role != "job_seeker":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only job seekers can view interview sessions"
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


@router.get("/{session_id}/transcript", response_model=InterviewTranscriptResponse)
async def get_interview_transcript(
    session_id: UUID,
    current_user: User = Depends(require_job_seeker),
    db: AsyncSession = Depends(get_db),
):
    """
    [Story 8.4] Get full conversation transcript for an interview session.
    
    Returns complete Q&A history with per-turn scores and timestamps.
    Useful for review and analysis of interview performance.
    
    **Performance Target:** <500ms (P95)
    
    **Authorization:** User must own the interview session.
    
    **Error Responses:**
    - 403 Forbidden: User doesn't own this session
    - 404 Not Found: Session not found
    """
    try:
        transcript_data = await history_service.get_interview_transcript(
            db=db,
            session_id=session_id,
            user_id=current_user.id,
        )
        
        return InterviewTranscriptResponse(**transcript_data)
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error fetching transcript for session {session_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve interview transcript: {str(e)}"
        )


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
    if current_user.role != "job_seeker":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only job seekers can view interview turns"
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
    if current_user.role != "job_seeker":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only job seekers can complete interviews"
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
    if current_user.role != "job_seeker":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only job seekers can view interview evaluations"
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


@router.get("/{session_id}/evaluation/detail", response_model=InterviewEvaluationDetail)
async def get_interview_evaluation_detail(
    session_id: UUID,
    current_user: User = Depends(require_job_seeker),
    db: AsyncSession = Depends(get_db),
):
    """
    [Story 8.4] Get comprehensive evaluation report with detailed breakdown.
    
    Returns full evaluation analysis in the format expected by Story 8.4 frontend:
    - Overall evaluation (score, grade, recommendation)
    - Dimension scores (technical, communication, behavioral) with sub-scores and evidence
    - Detailed analysis (strengths, improvements, notable moments, red flags)
    - Recommendations (hiring decision, reasoning, role fit, development areas)
    
    **Performance Target:** <300ms (P95)
    
    **Authorization:** User must own the interview session.
    
    **Error Responses:**
    - 400 Bad Request: Interview not yet completed
    - 403 Forbidden: User doesn't own this session
    - 404 Not Found: Session or evaluation not found
    """
    try:
        session, evaluation = await history_service.get_interview_evaluation(
            db=db,
            session_id=session_id,
            user_id=current_user.id,
        )
        
        # Build InterviewEvaluationDetail from evaluation data
        # Note: The evaluation model stores data in JSONB fields that match our schema
        detail = InterviewEvaluationDetail(
            interview_id=session.id,
            job_title=session.job_title or "Untitled Position",
            overall_evaluation={
                "score": evaluation.final_score,
                "grade": evaluation.grade,
                "hiring_recommendation": evaluation.hiring_recommendation,
            },
            dimension_scores=evaluation.dimension_scores,  # Already in correct format
            detailed_analysis=evaluation.detailed_analysis,  # Already in correct format
            recommendations=evaluation.recommendations,  # Already in correct format
            created_at=evaluation.created_at,
        )
        
        return detail
    except HTTPException:
        # Re-raise HTTPExceptions from service layer
        raise
    except Exception as e:
        logger.error(f"Error fetching evaluation detail for session {session_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve evaluation report: {str(e)}"
        )


@router.get("/health/celery", status_code=status.HTTP_200_OK)
async def check_celery_health():
    """
    Health check endpoint for Celery workers and Redis connection.
    
    Returns:
    - worker_count: Number of active Celery workers
    - workers: List of active worker names
    - redis_connected: Whether Redis is reachable
    - tasks: Statistics about tasks (active, scheduled, reserved)
    
    Useful for monitoring and debugging async task system.
    """
    try:
        from app.core.celery_app import celery_app
        import redis
        from app.core.config import settings
        
        # Check Celery workers
        inspect = celery_app.control.inspect()
        stats = inspect.stats()
        active_tasks = inspect.active()
        scheduled_tasks = inspect.scheduled()
        reserved_tasks = inspect.reserved()
        
        worker_count = len(stats) if stats else 0
        worker_names = list(stats.keys()) if stats else []
        
        # Check Redis connection
        redis_connected = False
        try:
            r = redis.from_url(settings.REDIS_URL, socket_connect_timeout=2)
            redis_connected = r.ping()
        except Exception as redis_error:
            logger.warning(f"Redis health check failed: {redis_error}")
        
        # Count tasks
        total_active = sum(len(tasks) for tasks in (active_tasks or {}).values())
        total_scheduled = sum(len(tasks) for tasks in (scheduled_tasks or {}).values())
        total_reserved = sum(len(tasks) for tasks in (reserved_tasks or {}).values())
        
        return {
            "status": "healthy" if worker_count > 0 and redis_connected else "degraded",
            "timestamp": str(UUID),
            "celery": {
                "worker_count": worker_count,
                "workers": worker_names,
                "tasks": {
                    "active": total_active,
                    "scheduled": total_scheduled,
                    "reserved": total_reserved,
                }
            },
            "redis": {
                "connected": redis_connected,
                "url": settings.REDIS_HOST + ":" + str(settings.REDIS_PORT)
            },
            "message": (
                "All systems operational" if worker_count > 0 and redis_connected
                else "Warning: No active workers" if worker_count == 0
                else "Warning: Redis connection issue"
            )
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Celery health check failed: {str(e)}"
        )
