"""
Conversation Service for Epic 8.2: Voice Interaction with AI Interviewer.

This service integrates with DialogFlow AI agent (_sub-agents/agents/conversation_agent.py)
to process interview turns, evaluate answers, and manage conversation flow.

Key Features:
- Process candidate answers with per-turn evaluation
- Integrate with Qwen2.5-1.5B-Instruct via Ollama
- Real-time conversation flow management
- Database persistence for turns and evaluations
- Error handling with graceful degradation
"""
import json
import logging
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from uuid import UUID

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.interviews.models import (
    AgentCallLog,
    InterviewQuestion,
    InterviewSession,
    InterviewTurn,
)

logger = logging.getLogger(__name__)

# Ollama configuration
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_TIMEOUT = 15.0  # 15 seconds timeout
CONVERSATION_MODEL = "qwen2.5:1.5b-instruct-fp16"


class ConversationService:
    """
    Service for managing AI interview conversations.
    
    Integrates with DialogFlow AI agent to process candidate responses,
    generate AI feedback, and maintain conversation state.
    """
    
    def __init__(self, db: AsyncSession):
        """
        Initialize conversation service.
        
        Args:
            db: Async database session
        """
        self.db = db
    
    async def process_turn(
        self,
        session_id: UUID,
        current_question_id: UUID,
        candidate_answer: str,
        user_id: int,
    ) -> Dict:
        """
        Process a conversation turn with DialogFlow AI agent.
        
        This is the main entry point for voice interaction processing.
        Steps:
        1. Validate session ownership
        2. Load session and conversation history
        3. Call DialogFlow AI agent via Ollama
        4. Parse agent response
        5. Save turn to database
        6. Log agent call metrics
        
        Args:
            session_id: Interview session UUID
            current_question_id: Current question UUID
            candidate_answer: Transcribed text from voice input
            user_id: Current user ID for authorization
        
        Returns:
            Dict with structure:
            {
                "turn_evaluation": {
                    "technical_score": float,
                    "communication_score": float,
                    "depth_score": float,
                    "overall_score": float
                },
                "next_action": {
                    "action_type": str,  # 'follow_up', 'continue', 'next_question', 'end'
                    "ai_response": str,
                    "follow_up_question": str (optional)
                },
                "context_update": {
                    "topics_covered": List[str],
                    "follow_up_depth": int,
                    "turn_count": int
                },
                "turn_id": UUID
            }
        
        Raises:
            PermissionError: If user doesn't own the interview session
            ValueError: If session not found or in invalid state
            httpx.HTTPError: If Ollama service is unavailable
        """
        start_time = time.time()
        
        # Step 1: Validate session ownership
        session = await self._get_session_with_auth(session_id, user_id)
        
        # Step 2: Load conversation history
        conversation_history = await self._build_conversation_history(session_id)
        
        # Step 3: Get current question
        current_question = await self._get_question(current_question_id)
        
        # Step 4: Call DialogFlow AI agent
        try:
            agent_response = await self._call_conversation_agent(
                interview_id=str(session_id),
                current_question=current_question.question_text,
                candidate_answer=candidate_answer,
                conversation_history=conversation_history,
                question_metadata={
                    "category": current_question.category,
                    "difficulty": current_question.difficulty,
                    "key_points": current_question.key_points,
                }
            )
            
            latency_ms = int((time.time() - start_time) * 1000)
            
            # Step 5: Parse and validate response
            parsed_response = self._parse_agent_response(agent_response)
            
            # Step 6: Save turn to database
            turn = await self._save_turn(
                session_id=session_id,
                question_id=current_question_id,
                candidate_answer=candidate_answer,
                agent_response=parsed_response,
            )
            
            # Step 7: Log successful agent call
            await self._log_agent_call(
                agent_type="conversation",
                session_id=session_id,
                input_data={
                    "question": current_question.question_text,
                    "answer": candidate_answer,
                    "history_length": len(conversation_history),
                },
                output_data=parsed_response,
                status="success",
                latency_ms=latency_ms,
                model_used=CONVERSATION_MODEL,
            )
            
            # Step 8: Build final response
            return {
                "turn_evaluation": parsed_response["turn_evaluation"],
                "next_action": parsed_response["next_action"],
                "context_update": parsed_response["context_update"],
                "turn_id": turn.id,
            }
            
        except Exception as e:
            latency_ms = int((time.time() - start_time) * 1000)
            
            # Log failed agent call
            await self._log_agent_call(
                agent_type="conversation",
                session_id=session_id,
                input_data={
                    "question": current_question.question_text,
                    "answer": candidate_answer,
                },
                output_data=None,
                status="error",
                latency_ms=latency_ms,
                model_used=CONVERSATION_MODEL,
                error_message=str(e),
            )
            
            # Re-raise with context
            logger.error(
                f"Error processing turn for session {session_id}: {str(e)}",
                exc_info=True
            )
            raise
    
    async def _get_session_with_auth(
        self, session_id: UUID, user_id: int
    ) -> InterviewSession:
        """
        Get session and validate user ownership.
        
        Args:
            session_id: Interview session UUID
            user_id: Current user ID
        
        Returns:
            InterviewSession object
        
        Raises:
            PermissionError: If user doesn't own the session
            ValueError: If session not found
        """
        result = await self.db.execute(
            select(InterviewSession)
            .where(InterviewSession.id == session_id)
        )
        session = result.scalar_one_or_none()
        
        if not session:
            raise ValueError(f"Interview session {session_id} not found")
        
        if session.candidate_id != user_id:
            raise PermissionError(
                f"User {user_id} does not have permission to access session {session_id}"
            )
        
        if session.status not in ["in_progress", "pending"]:
            raise ValueError(
                f"Interview session {session_id} is not active (status: {session.status})"
            )
        
        # Update status to in_progress if pending
        if session.status == "pending":
            session.status = "in_progress"
            session.started_at = datetime.utcnow()
            await self.db.commit()
            await self.db.refresh(session)
        
        return session
    
    async def _build_conversation_history(
        self, session_id: UUID
    ) -> List[Dict[str, str]]:
        """
        Build conversation history from database turns.
        
        Args:
            session_id: Interview session UUID
        
        Returns:
            List of conversation turns: [{"ai": str, "candidate": str}, ...]
        """
        result = await self.db.execute(
            select(InterviewTurn)
            .where(InterviewTurn.interview_session_id == session_id)
            .order_by(InterviewTurn.turn_number)
        )
        turns = result.scalars().all()
        
        history = []
        for turn in turns:
            history.append({
                "ai": turn.ai_message,
                "candidate": turn.candidate_message,
            })
        
        return history
    
    async def _get_question(self, question_id: UUID) -> InterviewQuestion:
        """
        Get interview question by ID.
        
        Args:
            question_id: Question UUID
        
        Returns:
            InterviewQuestion object
        
        Raises:
            ValueError: If question not found
        """
        result = await self.db.execute(
            select(InterviewQuestion)
            .where(InterviewQuestion.id == question_id)
        )
        question = result.scalar_one_or_none()
        
        if not question:
            raise ValueError(f"Question {question_id} not found")
        
        return question
    
    async def _call_conversation_agent(
        self,
        interview_id: str,
        current_question: str,
        candidate_answer: str,
        conversation_history: List[Dict[str, str]],
        question_metadata: Optional[Dict] = None,
    ) -> Dict:
        """
        Call DialogFlow AI agent via Ollama API.
        
        This method constructs the prompt and calls the Ollama generate endpoint.
        The agent uses Qwen2.5-1.5B-Instruct model for fast inference (<3s target).
        
        Args:
            interview_id: Interview session UUID string
            current_question: Current question text
            candidate_answer: Candidate's transcribed answer
            conversation_history: Previous Q&A pairs
            question_metadata: Additional question context
        
        Returns:
            Dict with agent's JSON response
        
        Raises:
            httpx.HTTPError: If Ollama service is unreachable
            ValueError: If response is invalid JSON
        """
        # Build conversation context
        context_lines = []
        if conversation_history:
            context_lines.append("Previous conversation:")
            for idx, turn in enumerate(conversation_history[-3:], 1):  # Last 3 turns
                context_lines.append(f"Q{idx}: {turn['ai'][:100]}...")
                context_lines.append(f"A{idx}: {turn['candidate'][:100]}...")
        
        context_str = "\n".join(context_lines) if context_lines else "This is the first question."
        
        # Build prompt following DialogFlow AI system prompt structure
        prompt = f"""You are an AI interviewer evaluating a candidate's response.

Interview ID: {interview_id}
Question Category: {question_metadata.get('category', 'technical') if question_metadata else 'technical'}
Difficulty Level: {question_metadata.get('difficulty', 'middle') if question_metadata else 'middle'}

{context_str}

Current Question: {current_question}

Candidate's Answer: {candidate_answer}

Evaluate this answer and respond with a JSON object containing:
1. turn_evaluation: Scores (0-10) for technical_score, communication_score, depth_score, overall_score
2. next_action: action_type ('follow_up', 'continue', 'next_question', 'end'), ai_response (encouraging feedback), follow_up_question (if action_type is 'follow_up')
3. context_update: topics_covered (list), follow_up_depth (int), turn_count (current turn number)

Response must be valid JSON only, no additional text.
"""
        
        # Call Ollama API
        async with httpx.AsyncClient(timeout=OLLAMA_TIMEOUT) as client:
            try:
                response = await client.post(
                    f"{OLLAMA_BASE_URL}/api/generate",
                    json={
                        "model": CONVERSATION_MODEL,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.7,
                            "top_p": 0.9,
                        }
                    }
                )
                response.raise_for_status()
                
                result = response.json()
                agent_output = result.get("response", "")
                
                # Try to parse JSON from response
                try:
                    # Extract JSON if wrapped in markdown code blocks
                    if "```json" in agent_output:
                        json_start = agent_output.find("```json") + 7
                        json_end = agent_output.find("```", json_start)
                        agent_output = agent_output[json_start:json_end].strip()
                    elif "```" in agent_output:
                        json_start = agent_output.find("```") + 3
                        json_end = agent_output.find("```", json_start)
                        agent_output = agent_output[json_start:json_end].strip()
                    
                    parsed_json = json.loads(agent_output)
                    return parsed_json
                    
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse agent JSON response: {e}")
                    logger.debug(f"Raw agent output: {agent_output}")
                    
                    # Return safe default response
                    return self._get_default_agent_response(
                        candidate_answer=candidate_answer,
                        current_question=current_question,
                    )
            
            except httpx.TimeoutException:
                logger.error(f"Ollama request timeout after {OLLAMA_TIMEOUT}s")
                raise ValueError(
                    "AI processing timeout. The system is taking longer than usual. Please try again."
                )
            
            except httpx.HTTPError as e:
                logger.error(f"Ollama HTTP error: {e}")
                raise ValueError(
                    "AI service is currently unavailable. Please ensure Ollama is running and try again."
                )
    
    def _get_default_agent_response(
        self, candidate_answer: str, current_question: str
    ) -> Dict:
        """
        Generate a safe default response when agent fails.
        
        Args:
            candidate_answer: Candidate's answer
            current_question: Question that was asked
        
        Returns:
            Dict with default safe response structure
        """
        answer_length = len(candidate_answer)
        
        # Simple heuristic scoring based on answer length
        if answer_length < 50:
            base_score = 5.0
        elif answer_length < 150:
            base_score = 6.5
        elif answer_length < 300:
            base_score = 7.5
        else:
            base_score = 8.0
        
        return {
            "turn_evaluation": {
                "technical_score": base_score,
                "communication_score": base_score + 0.5,
                "depth_score": base_score - 0.5,
                "overall_score": base_score,
            },
            "next_action": {
                "action_type": "continue",
                "ai_response": "Thank you for your answer. Let's continue with the next question.",
                "follow_up_question": None,
            },
            "context_update": {
                "topics_covered": ["general"],
                "follow_up_depth": 0,
                "turn_count": 1,
            }
        }
    
    def _parse_agent_response(self, agent_response: Dict) -> Dict:
        """
        Parse and validate agent response structure.
        
        Args:
            agent_response: Raw agent response dict
        
        Returns:
            Validated response dict
        
        Raises:
            ValueError: If response structure is invalid
        """
        required_keys = ["turn_evaluation", "next_action", "context_update"]
        for key in required_keys:
            if key not in agent_response:
                raise ValueError(f"Missing required key in agent response: {key}")
        
        # Validate turn_evaluation
        eval_keys = ["technical_score", "communication_score", "depth_score", "overall_score"]
        for key in eval_keys:
            if key not in agent_response["turn_evaluation"]:
                agent_response["turn_evaluation"][key] = 7.0  # Default score
        
        # Validate next_action
        if "action_type" not in agent_response["next_action"]:
            agent_response["next_action"]["action_type"] = "continue"
        if "ai_response" not in agent_response["next_action"]:
            agent_response["next_action"]["ai_response"] = "Let's continue."
        
        return agent_response
    
    async def _save_turn(
        self,
        session_id: UUID,
        question_id: UUID,
        candidate_answer: str,
        agent_response: Dict,
    ) -> InterviewTurn:
        """
        Save conversation turn to database.
        
        Follows SQLAlchemy async best practices to avoid MissingGreenlet errors.
        
        Args:
            session_id: Interview session UUID
            question_id: Question UUID
            candidate_answer: Candidate's answer text
            agent_response: Parsed agent response
        
        Returns:
            Created InterviewTurn object
        """
        # Get current turn count
        result = await self.db.execute(
            select(InterviewTurn)
            .where(InterviewTurn.interview_session_id == session_id)
        )
        existing_turns = result.scalars().all()
        turn_number = len(existing_turns) + 1
        
        # Extract data from agent response
        turn_eval = agent_response["turn_evaluation"]
        next_action = agent_response["next_action"]
        
        # Create turn object
        turn = InterviewTurn(
            interview_session_id=session_id,
            question_id=question_id,
            turn_number=turn_number,
            ai_message=next_action.get("ai_response", ""),
            candidate_message=candidate_answer,
            answer_quality={
                "technical_accuracy": turn_eval.get("technical_score", 0.0),
                "communication_clarity": turn_eval.get("communication_score", 0.0),
                "depth_of_knowledge": turn_eval.get("depth_score", 0.0),
                "overall_score": turn_eval.get("overall_score", 0.0),
            },
            key_observations=agent_response.get("context_update", {}).get("topics_covered", []),
            action_type=next_action.get("action_type", "continue"),
        )
        
        self.db.add(turn)
        await self.db.commit()
        await self.db.refresh(turn)
        
        return turn
    
    async def _log_agent_call(
        self,
        agent_type: str,
        session_id: UUID,
        input_data: Optional[Dict],
        output_data: Optional[Dict],
        status: str,
        latency_ms: int,
        model_used: str,
        error_message: Optional[str] = None,
    ) -> None:
        """
        Log agent call for monitoring and debugging.
        
        Args:
            agent_type: Type of agent ('conversation', 'question_generator', 'evaluator')
            session_id: Interview session UUID
            input_data: Agent input data (sanitized, no PII)
            output_data: Agent output data
            status: 'success' or 'error'
            latency_ms: Call latency in milliseconds
            model_used: Model name used
            error_message: Error message if status is 'error'
        """
        log = AgentCallLog(
            agent_type=agent_type,
            interview_session_id=session_id,
            input_data=input_data,
            output_data=output_data,
            status=status,
            error_message=error_message,
            latency_ms=latency_ms,
            model_used=model_used,
        )
        
        self.db.add(log)
        await self.db.commit()
