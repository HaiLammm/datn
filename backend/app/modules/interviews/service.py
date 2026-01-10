"""
Service layer for Epic 8: Virtual AI Interview Room.

This module provides business logic for interview operations:
- InterviewService: Main orchestrator for interview sessions
- QuestionService: AI question generation
- ConversationService: Dialogue management and per-turn evaluation
- EvaluationService: Final comprehensive evaluation

All services integrate with AI agents from _sub-agents directory.
"""
import sys
import time
import logging
from datetime import datetime
from decimal import Decimal
from typing import List, Optional, Dict, Any
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

import os

# Add _sub-agents directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
# current: backend/app/modules/interviews
# move up 3 levels to backend
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
project_root = os.path.dirname(backend_dir)
sub_agents_dir = os.path.join(project_root, '_sub-agents')

if sub_agents_dir not in sys.path:
    sys.path.append(sub_agents_dir)

from agents.question_generator import QuestionGeneratorAgent
from agents.conversation_agent import ConversationAgent
from agents.performance_evaluator import PerformanceEvaluatorAgent

from app.modules.interviews.models import (
    InterviewSession,
    InterviewQuestion,
    InterviewTurn,
    InterviewEvaluation,
    AgentCallLog,
)
from app.modules.interviews.schemas import (
    InterviewSessionCreate,
    InterviewTurnCreate,
    AnswerQuality,
    DimensionScore,
    DetailedAnalysis,
    Recommendations,
)
from app.core.config import settings

logger = logging.getLogger(__name__)


class QuestionService:
    """Service for generating interview questions using QuestionCraft AI."""
    
    def __init__(self):
        """Initialize with QuestionGeneratorAgent."""
        self.agent = QuestionGeneratorAgent(
            config_path=settings.QUESTION_AGENT_CONFIG
        )
    
    async def generate_questions(
        self,
        db: AsyncSession,
        session_id: UUID,
        job_description: str,
        cv_content: str,
        position_level: str,
        num_questions: int = 10,
        focus_areas: Optional[List[str]] = None
    ) -> List[InterviewQuestion]:
        """
        Generate interview questions using AI and save to database.
        
        Args:
            db: Database session
            session_id: Interview session UUID
            job_description: Job description text
            cv_content: Candidate's CV content
            position_level: junior, middle, or senior
            num_questions: Number of questions to generate (5-15)
            focus_areas: Optional list of focus areas
        
        Returns:
            List of created InterviewQuestion objects
        
        Raises:
            Exception: If AI agent fails or database error occurs
        """
        start_time = time.time()
        
        try:
            # Call AI agent (synchronous call)
            result = self.agent.generate_questions(
                job_description=job_description,
                cv_content=cv_content,
                position_level=position_level,
                num_questions=num_questions,
                focus_areas=focus_areas or []
            )
            
            if result["status"] != "success":
                raise Exception(f"Agent error: {result.get('error')}")
            
            # Store agent metadata before commit (SQLAlchemy async rule #1)
            agent_model = self.agent.model
            agent_metadata = result.get("metadata", {})
            
            # Save questions to database
            questions = []
            for idx, q_data in enumerate(result["questions"]):
                question = InterviewQuestion(
                    interview_session_id=session_id,
                    question_id=q_data["question_id"],
                    category=q_data["category"],
                    difficulty=q_data["difficulty"],
                    question_text=q_data["question_text"],
                    key_points=q_data.get("key_points"),
                    ideal_answer_outline=q_data.get("ideal_answer_outline"),
                    evaluation_criteria=q_data.get("evaluation_criteria"),
                    order_index=idx,
                    is_selected=True
                )
                db.add(question)
                questions.append(question)
            
            # Log agent call
            latency_ms = int((time.time() - start_time) * 1000)
            log = AgentCallLog(
                agent_type="question_generator",
                interview_session_id=session_id,
                input_data={
                    "position_level": position_level,
                    "num_questions": num_questions,
                    "focus_areas": focus_areas or []
                },
                output_data=agent_metadata,
                status="success",
                latency_ms=latency_ms,
                model_used=agent_model
            )
            db.add(log)
            
            await db.commit()
            
            # Refresh questions to get IDs
            for q in questions:
                await db.refresh(q)
            
            logger.info(f"Generated {len(questions)} questions in {latency_ms}ms for session {session_id}")
            return questions
            
        except Exception as e:
            logger.error(f"Error generating questions for session {session_id}: {e}")
            
            # Log error
            latency_ms = int((time.time() - start_time) * 1000)
            log = AgentCallLog(
                agent_type="question_generator",
                interview_session_id=session_id,
                input_data={
                    "position_level": position_level,
                    "num_questions": num_questions
                },
                status="error",
                error_message=str(e),
                latency_ms=latency_ms
            )
            db.add(log)
            await db.commit()
            
            raise


class ConversationService:
    """Service for managing interview dialogue using DialogFlow AI."""
    
    def __init__(self):
        """Initialize with ConversationAgent."""
        self.agent = ConversationAgent(
            config_path=settings.CONVERSATION_AGENT_CONFIG
        )
    
    async def process_turn(
        self,
        db: AsyncSession,
        session_id: UUID,
        candidate_message: str
    ) -> InterviewTurn:
        """
        Process a conversation turn with AI evaluation.
        
        Args:
            db: Database session
            session_id: Interview session UUID
            candidate_message: Candidate's answer text
        
        Returns:
            Created InterviewTurn with AI evaluation
        
        Raises:
            Exception: If session not found or AI agent fails
        """
        start_time = time.time()
        
        try:
            # Get session with questions and previous turns (eager loading - Rule #2)
            result = await db.execute(
                select(InterviewSession)
                .options(
                    selectinload(InterviewSession.questions),
                    selectinload(InterviewSession.turns)
                )
                .where(InterviewSession.id == session_id)
            )
            session = result.scalar_one_or_none()
            
            if not session:
                raise ValueError(f"Interview session {session_id} not found")
            
            # Build context from previous turns
            conversation_history = []
            for turn in session.turns:
                conversation_history.append({
                    "ai": turn.ai_message,
                    "candidate": turn.candidate_message
                })
            
            # Get current question
            current_turn_number = len(session.turns) + 1
            current_question_index = min(current_turn_number - 1, len(session.questions) - 1)
            current_question = session.questions[current_question_index] if session.questions else None
            
            # Prepare question data for agent
            question_data = {
                "question_id": current_question.question_id,
                "question_text": current_question.question_text,
                "category": current_question.category,
                "difficulty": current_question.difficulty,
                "key_points": current_question.key_points,
                "evaluation_criteria": current_question.evaluation_criteria
            } if current_question else None
            
            # Call AI agent
            agent_result = self.agent.process_turn(
                candidate_message=candidate_message,
                current_question=question_data,
                conversation_history=conversation_history
            )
            
            if agent_result["status"] != "success":
                raise Exception(f"Agent error: {agent_result.get('error')}")
            
            # Store agent data before commit
            agent_model = self.agent.model
            ai_response = agent_result.get("ai_message", "")
            answer_quality = agent_result.get("answer_quality", {})
            key_observations = agent_result.get("key_observations", [])
            strengths = agent_result.get("strengths", [])
            gaps = agent_result.get("gaps", [])
            action_type = agent_result.get("action_type", "continue")
            
            # Create turn record
            turn = InterviewTurn(
                interview_session_id=session_id,
                question_id=current_question.id if current_question else None,
                turn_number=current_turn_number,
                ai_message=ai_response,
                candidate_message=candidate_message,
                answer_quality=answer_quality,
                key_observations=key_observations,
                strengths=strengths,
                gaps=gaps,
                action_type=action_type
            )
            db.add(turn)
            
            # Log agent call
            latency_ms = int((time.time() - start_time) * 1000)
            log = AgentCallLog(
                agent_type="conversation",
                interview_session_id=session_id,
                input_data={
                    "turn_number": current_turn_number,
                    "question_id": current_question.question_id if current_question else None
                },
                output_data={"action_type": action_type},
                status="success",
                latency_ms=latency_ms,
                model_used=agent_model
            )
            db.add(log)
            
            # Update session timestamp
            session.updated_at = datetime.utcnow()
            
            await db.commit()
            await db.refresh(turn)
            
            logger.info(f"Processed turn {current_turn_number} for session {session_id} in {latency_ms}ms")
            return turn
            
        except Exception as e:
            logger.error(f"Error processing turn for session {session_id}: {e}")
            
            # Log error
            latency_ms = int((time.time() - start_time) * 1000)
            log = AgentCallLog(
                agent_type="conversation",
                interview_session_id=session_id,
                status="error",
                error_message=str(e),
                latency_ms=latency_ms
            )
            db.add(log)
            await db.commit()
            
            raise


class EvaluationService:
    """Service for generating final evaluation using EvalMaster AI."""
    
    def __init__(self):
        """Initialize with PerformanceEvaluatorAgent."""
        self.agent = PerformanceEvaluatorAgent(
            config_path=settings.EVALUATOR_AGENT_CONFIG
        )
    
    async def generate_evaluation(
        self,
        db: AsyncSession,
        session_id: UUID
    ) -> InterviewEvaluation:
        """
        Generate comprehensive evaluation report for completed interview.
        
        Args:
            db: Database session
            session_id: Interview session UUID
        
        Returns:
            Created InterviewEvaluation with full analysis
        
        Raises:
            Exception: If session not found or AI agent fails
        """
        start_time = time.time()
        
        try:
            # Get session with all related data (eager loading)
            result = await db.execute(
                select(InterviewSession)
                .options(
                    selectinload(InterviewSession.questions),
                    selectinload(InterviewSession.turns)
                )
                .where(InterviewSession.id == session_id)
            )
            session = result.scalar_one_or_none()
            
            if not session:
                raise ValueError(f"Interview session {session_id} not found")
            
            # Prepare questions data
            questions = []
            for q in session.questions:
                questions.append({
                    "question_id": q.question_id,
                    "category": q.category,
                    "difficulty": q.difficulty,
                    "question_text": q.question_text,
                    "key_points": q.key_points,
                    "evaluation_criteria": q.evaluation_criteria
                })
            
            # Prepare transcript
            transcript = []
            for turn in session.turns:
                transcript.append({
                    "turn_number": turn.turn_number,
                    "ai_message": turn.ai_message,
                    "candidate_message": turn.candidate_message,
                    "answer_quality": turn.answer_quality,
                    "key_observations": turn.key_observations,
                    "strengths": turn.strengths,
                    "gaps": turn.gaps
                })
            
            # Calculate duration
            duration_minutes = None
            if session.started_at and session.completed_at:
                duration = (session.completed_at - session.started_at).total_seconds() / 60
                duration_minutes = int(duration)
            
            # Call AI agent
            agent_result = self.agent.generate_evaluation(
                questions=questions,
                transcript=transcript,
                duration_minutes=duration_minutes
            )
            
            if agent_result["status"] != "success":
                raise Exception(f"Agent error: {agent_result.get('error')}")
            
            # Store agent data before commit
            agent_model = self.agent.model
            final_score = Decimal(str(agent_result.get("final_score", 0.0)))
            grade = agent_result.get("grade", "average")
            hiring_recommendation = agent_result.get("hiring_recommendation", "consider")
            dimension_scores = agent_result.get("dimension_scores", {})
            detailed_analysis = agent_result.get("detailed_analysis", {})
            recommendations = agent_result.get("recommendations", {})
            evaluation_metadata = agent_result.get("metadata", {})
            
            # Create evaluation record
            evaluation = InterviewEvaluation(
                interview_session_id=session_id,
                final_score=final_score,
                grade=grade,
                hiring_recommendation=hiring_recommendation,
                dimension_scores=dimension_scores,
                detailed_analysis=detailed_analysis,
                recommendations=recommendations,
                evaluation_metadata=evaluation_metadata
            )
            db.add(evaluation)
            
            # Log agent call
            latency_ms = int((time.time() - start_time) * 1000)
            log = AgentCallLog(
                agent_type="evaluator",
                interview_session_id=session_id,
                input_data={
                    "total_questions": len(questions),
                    "total_turns": len(transcript),
                    "duration_minutes": duration_minutes
                },
                output_data={
                    "final_score": float(final_score),
                    "grade": grade,
                    "hiring_recommendation": hiring_recommendation
                },
                status="success",
                latency_ms=latency_ms,
                model_used=agent_model
            )
            db.add(log)
            
            # Update session status
            session.status = "completed"
            session.completed_at = datetime.utcnow()
            if session.started_at:
                session.duration_minutes = int((session.completed_at - session.started_at).total_seconds() / 60)
            session.updated_at = datetime.utcnow()
            
            await db.commit()
            await db.refresh(evaluation)
            
            logger.info(f"Generated evaluation for session {session_id} in {latency_ms}ms: score={final_score}")
            return evaluation
            
        except Exception as e:
            logger.error(f"Error generating evaluation for session {session_id}: {e}")
            
            # Log error
            latency_ms = int((time.time() - start_time) * 1000)
            log = AgentCallLog(
                agent_type="evaluator",
                interview_session_id=session_id,
                status="error",
                error_message=str(e),
                latency_ms=latency_ms
            )
            db.add(log)
            await db.commit()
            
            raise


class InterviewService:
    """Main orchestrator service for interview operations."""
    
    def __init__(self):
        """Initialize with all sub-services."""
        self.question_service = QuestionService()
        self.conversation_service = ConversationService()
        self.evaluation_service = EvaluationService()
    
    async def create_interview(
        self,
        db: AsyncSession,
        candidate_id: int,
        request: InterviewSessionCreate
    ) -> tuple[InterviewSession, List[InterviewQuestion]]:
        """
        Create new interview session and generate questions.
        
        Args:
            db: Database session
            candidate_id: ID of the candidate
            request: Interview creation request with JD and CV
        
        Returns:
            Tuple of (created session, generated questions)
        """
        try:
            # Create session
            session = InterviewSession(
                candidate_id=candidate_id,
                status="pending"
            )
            db.add(session)
            await db.flush()  # Get session ID
            
            # Store session ID before further operations
            session_id = session.id
            
            # Generate questions
            questions = await self.question_service.generate_questions(
                db=db,
                session_id=session_id,
                job_description=request.job_description,
                cv_content=request.cv_content,
                position_level=request.position_level,
                num_questions=request.num_questions,
                focus_areas=request.focus_areas
            )
            
            # Update session status
            session.status = "in_progress"
            session.started_at = datetime.utcnow()
            await db.commit()
            await db.refresh(session)
            
            logger.info(f"Created interview session {session_id} for candidate {candidate_id}")
            return session, questions
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Error creating interview for candidate {candidate_id}: {e}")
            raise
    
    async def get_session(
        self,
        db: AsyncSession,
        session_id: UUID,
        candidate_id: int
    ) -> Optional[InterviewSession]:
        """Get interview session by ID (with authorization check)."""
        result = await db.execute(
            select(InterviewSession)
            .options(
                selectinload(InterviewSession.questions),
                selectinload(InterviewSession.turns),
                selectinload(InterviewSession.evaluation)
            )
            .where(
                InterviewSession.id == session_id,
                InterviewSession.candidate_id == candidate_id
            )
        )
        return result.scalar_one_or_none()
    
    async def list_sessions(
        self,
        db: AsyncSession,
        candidate_id: int,
        skip: int = 0,
        limit: int = 20
    ) -> tuple[List[InterviewSession], int]:
        """List interview sessions for a candidate."""
        # Get total count
        count_result = await db.execute(
            select(func.count())
            .select_from(InterviewSession)
            .where(InterviewSession.candidate_id == candidate_id)
        )
        total = count_result.scalar()
        
        # Get sessions
        result = await db.execute(
            select(InterviewSession)
            .where(InterviewSession.candidate_id == candidate_id)
            .order_by(InterviewSession.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        sessions = result.scalars().all()
        
        return list(sessions), total
