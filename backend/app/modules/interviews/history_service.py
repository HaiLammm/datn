"""
Interview History Service for Story 8.4.

This service provides read-only access to interview session history,
including sessions list, detailed session info, transcripts, and evaluations.

Following SQLAlchemy async patterns to avoid MissingGreenlet errors:
- Use selectinload() for relationships
- Store values before any session operations
- Convert ORM objects to Pydantic models before returning
"""
import logging
from typing import List, Optional, Tuple
from uuid import UUID
from datetime import datetime

from sqlalchemy import select, func, desc, asc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

from app.modules.interviews.models import (
    InterviewSession,
    InterviewQuestion,
    InterviewTurn,
    InterviewEvaluation,
)

logger = logging.getLogger(__name__)


class HistoryService:
    """
    Service for managing interview history queries.
    
    Provides methods for:
    - Listing interview sessions with pagination and sorting
    - Retrieving detailed session information
    - Fetching conversation transcripts
    - Accessing evaluation reports
    
    All methods enforce authorization (user can only access their own data).
    """
    
    async def get_interview_sessions(
        self,
        db: AsyncSession,
        user_id: int,
        page: int = 1,
        page_size: int = 10,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        status_filter: Optional[str] = None,
    ) -> Tuple[List[InterviewSession], int]:
        """
        Get paginated list of interview sessions for a user.
        
        Args:
            db: Database session
            user_id: ID of the user (job seeker)
            page: Page number (1-indexed)
            page_size: Items per page (max 50)
            sort_by: Field to sort by ('created_at' or 'overall_score')
            sort_order: Sort direction ('asc' or 'desc')
            status_filter: Optional status filter ('active', 'completed', 'abandoned')
        
        Returns:
            Tuple of (list of sessions, total count)
        
        Performance:
            - Uses efficient query with LIMIT/OFFSET
            - No eager loading (list view only needs basic fields)
            - Separate count query for total
        """
        # Validate inputs
        page = max(1, page)  # Ensure page >= 1
        page_size = min(max(1, page_size), 50)  # Clamp between 1 and 50
        
        if sort_by not in ["created_at", "overall_score"]:
            sort_by = "created_at"
        
        if sort_order not in ["asc", "desc"]:
            sort_order = "desc"
        
        # Build base query
        query = select(InterviewSession).where(
            InterviewSession.candidate_id == user_id
        )
        
        # Apply status filter if provided
        if status_filter:
            if status_filter in ["active", "completed", "abandoned", "ready", "in_progress"]:
                query = query.where(InterviewSession.status == status_filter)
        
        # Get total count (before pagination)
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar_one()
        
        # Apply sorting
        sort_column = getattr(InterviewSession, sort_by)
        if sort_order == "desc":
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(asc(sort_column))
        
        # Apply pagination
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        
        # Execute query
        result = await db.execute(query)
        sessions = result.scalars().all()
        
        logger.info(
            f"Retrieved {len(sessions)} interview sessions for user {user_id} "
            f"(page {page}, total {total})"
        )
        
        return list(sessions), total
    
    async def get_interview_detail(
        self,
        db: AsyncSession,
        session_id: UUID,
        user_id: int,
    ) -> InterviewSession:
        """
        Get detailed information about a specific interview session.
        
        Args:
            db: Database session
            session_id: Interview session UUID
            user_id: ID of the requesting user (for authorization)
        
        Returns:
            InterviewSession with basic details (no relationships loaded)
        
        Raises:
            HTTPException 404: Session not found
            HTTPException 403: User doesn't own this session
        
        Performance:
            - Single query, no joins
            - Fast response for detail view metadata
        """
        # Query session
        query = select(InterviewSession).where(
            InterviewSession.id == session_id
        )
        
        result = await db.execute(query)
        session = result.scalar_one_or_none()
        
        if not session:
            logger.warning(f"Interview session {session_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Interview session not found"
            )
        
        # Authorization check
        if session.candidate_id != user_id:
            logger.warning(
                f"User {user_id} attempted to access session {session_id} "
                f"owned by user {session.candidate_id}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to access this interview session"
            )
        
        logger.info(f"Retrieved interview session {session_id} for user {user_id}")
        return session
    
    async def get_interview_transcript(
        self,
        db: AsyncSession,
        session_id: UUID,
        user_id: int,
    ) -> Tuple[InterviewSession, List[InterviewTurn], List[InterviewQuestion]]:
        """
        Get full conversation transcript for an interview session.
        
        Args:
            db: Database session
            session_id: Interview session UUID
            user_id: ID of the requesting user (for authorization)
        
        Returns:
            Tuple of (session, turns list, questions list)
        
        Raises:
            HTTPException 404: Session not found
            HTTPException 403: User doesn't own this session
        
        Performance:
            - Eager loads turns and questions in single query
            - Uses selectinload() to avoid N+1 queries
            - Ordered by turn_number for transcript display
        
        SQLAlchemy Async Notes:
            - Must use selectinload() for relationships in async context
            - Relationships are populated immediately, no lazy-loading
        """
        # Query session with eager-loaded relationships
        query = (
            select(InterviewSession)
            .options(
                selectinload(InterviewSession.turns),
                selectinload(InterviewSession.questions),
            )
            .where(InterviewSession.id == session_id)
        )
        
        result = await db.execute(query)
        session = result.scalar_one_or_none()
        
        if not session:
            logger.warning(f"Interview session {session_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interview session not found"
            )
        
        # Authorization check (before accessing relationships)
        if session.candidate_id != user_id:
            logger.warning(
                f"User {user_id} attempted to access transcript of session {session_id} "
                f"owned by user {session.candidate_id}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to access this interview session"
            )
        
        # Access relationships (already loaded, no additional queries)
        turns = session.turns  # List[InterviewTurn] ordered by turn_number
        questions = session.questions  # List[InterviewQuestion] ordered by order_index
        
        logger.info(
            f"Retrieved transcript for session {session_id}: "
            f"{len(turns)} turns, {len(questions)} questions"
        )
        
        return session, turns, questions
    
    async def get_interview_evaluation(
        self,
        db: AsyncSession,
        session_id: UUID,
        user_id: int,
    ) -> Tuple[InterviewSession, InterviewEvaluation]:
        """
        Get comprehensive evaluation report for a completed interview.
        
        Args:
            db: Database session
            session_id: Interview session UUID
            user_id: ID of the requesting user (for authorization)
        
        Returns:
            Tuple of (session, evaluation)
        
        Raises:
            HTTPException 404: Session or evaluation not found
            HTTPException 403: User doesn't own this session
            HTTPException 400: Interview not yet completed
        
        Performance:
            - Eager loads evaluation relationship
            - Single query with join
        
        SQLAlchemy Async Notes:
            - Must use selectinload() for evaluation relationship
            - Check evaluation exists before accessing (one-to-one)
        """
        # Query session with evaluation
        query = (
            select(InterviewSession)
            .options(selectinload(InterviewSession.evaluation))
            .where(InterviewSession.id == session_id)
        )
        
        result = await db.execute(query)
        session = result.scalar_one_or_none()
        
        if not session:
            logger.warning(f"Interview session {session_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interview session not found"
            )
        
        # Authorization check
        if session.candidate_id != user_id:
            logger.warning(
                f"User {user_id} attempted to access evaluation of session {session_id} "
                f"owned by user {session.candidate_id}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to access this interview session"
            )
        
        # Check if evaluation exists
        evaluation = session.evaluation
        
        if not evaluation:
            # Check if interview is completed
            if session.status != "completed":
                logger.info(
                    f"Evaluation requested for incomplete session {session_id} "
                    f"(status: {session.status})"
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Interview evaluation is not available yet. Complete the interview first."
                )
            else:
                logger.warning(
                    f"Completed session {session_id} has no evaluation record"
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Evaluation report not found for this interview"
                )
        
        logger.info(f"Retrieved evaluation for session {session_id}")
        return session, evaluation
    
    async def count_question_for_session(
        self,
        db: AsyncSession,
        session_id: UUID,
    ) -> int:
        """
        Count number of questions for a session (utility method).
        
        Args:
            db: Database session
            session_id: Interview session UUID
        
        Returns:
            Count of questions
        """
        query = select(func.count()).select_from(InterviewQuestion).where(
            InterviewQuestion.interview_session_id == session_id
        )
        result = await db.execute(query)
        return result.scalar_one()
    
    async def count_turns_for_session(
        self,
        db: AsyncSession,
        session_id: UUID,
    ) -> int:
        """
        Count number of turns for a session (utility method).
        
        Args:
            db: Database session
            session_id: Interview session UUID
        
        Returns:
            Count of turns
        """
        query = select(func.count()).select_from(InterviewTurn).where(
            InterviewTurn.interview_session_id == session_id
        )
        result = await db.execute(query)
        return result.scalar_one()
