"""
DialogFlow AI - Interview Conversation Agent
Manages interview conversation flow, analyzes answers, creates follow-ups
"""

from typing import Dict, Any, List, Optional
from .base_agent import BaseAgent


class ConversationAgent(BaseAgent):
    """
    Agent for managing interview conversations.
    
    Persona: Interview Conversation Facilitator
    - Warm, professional, encouraging
    - Active listening, purposeful follow-ups
    - Maintains natural conversation flow
    """
    
    def __init__(self, config_path: str = None):
        """
        Initialize DialogFlow AI agent.
        
        Args:
            config_path: Path to config file (defaults to standard location)
        """
        if config_path is None:
            import os
            config_path = os.path.join(
                os.path.dirname(__file__),
                '../configs/conversation_agent_config.json'
            )
        super().__init__(config_path)
        
        # Load conversation settings
        self.conversation_settings = self.config.get("conversation_settings", {})
        self.max_turns = self.conversation_settings.get("max_turns", 50)
        self.max_context_messages = self.conversation_settings.get("max_context_messages", 10)
        self.follow_up_depth = self.conversation_settings.get("follow_up_depth", 2)
        
        # Load scoring settings
        self.scoring_settings = self.config.get("scoring_settings", {})
        self.score_range = self.scoring_settings.get("score_range", [0, 10])
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a conversation turn (candidate's answer) and generate response.
        
        Args:
            input_data: {
                "interview_id": str,           # Interview session ID
                "current_question": Dict,       # Current question being asked
                "candidate_answer": str,        # Candidate's answer text
                "conversation_history": List[Dict], # Previous turns (optional)
                "interview_context": {          # Context about the interview
                    "position": str,
                    "level": str,
                    "candidate_name": str
                }
            }
        
        Returns:
            {
                "status": "success" or "error",
                "turn_evaluation": {
                    "turn_id": str,
                    "answer_quality": {
                        "technical_accuracy": float (0-10),
                        "communication_clarity": float (0-10),
                        "depth_of_knowledge": float (0-10),
                        "overall_score": float (0-10)
                    },
                    "key_observations": List[str],
                    "strengths": List[str],
                    "gaps": List[str]
                },
                "next_action": {
                    "action_type": str,  # "continue", "follow_up", "next_question", "end_interview"
                    "ai_response": str,  # What the AI says next
                    "follow_up_question": str (if action_type == "follow_up"),
                    "reasoning": str     # Why this action was chosen
                },
                "context_update": {
                    "topics_covered": List[str],
                    "follow_up_depth": int,
                    "turn_count": int
                },
                "error": str (if status == "error")
            }
        """
        # Validate input
        if not self._validate_input(input_data):
            return {
                "status": "error",
                "error": "Invalid input. Required: interview_id, current_question, candidate_answer"
            }
        
        try:
            # Build prompt with conversation context
            prompt = self._build_prompt(input_data)
            
            # Log request
            if self.config.get("logging", {}).get("log_requests", False):
                self.logger.info(f"Processing turn for interview {input_data.get('interview_id')}")
            
            # Call API with retry
            response = self._retry_on_failure(
                self._call_ollama_api,
                prompt
            )
            
            # Parse response
            result = self._parse_json_response(response)
            
            # Validate output
            if not self._validate_output(result):
                raise ValueError("Generated response does not meet quality standards")
            
            # Add status
            result["status"] = "success"
            
            # Log response
            if self.config.get("logging", {}).get("log_responses", False):
                self.logger.info(
                    f"Turn processed. Next action: {result.get('next_action', {}).get('action_type')}"
                )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error processing conversation turn: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate input data has required fields."""
        required = ["interview_id", "current_question", "candidate_answer"]
        return all(field in input_data for field in required)
    
    def _build_prompt(self, input_data: Dict[str, Any]) -> str:
        """Build complete prompt with conversation context."""
        # Extract input fields
        interview_id = input_data["interview_id"]
        current_question = input_data["current_question"]
        candidate_answer = input_data["candidate_answer"]
        conversation_history = input_data.get("conversation_history", [])
        interview_context = input_data.get("interview_context", {})
        
        # Build context section
        context_text = self._format_context(interview_context)
        
        # Build conversation history (limit to max_context_messages)
        history_text = self._format_history(
            conversation_history[-self.max_context_messages:]
        )
        
        # Build current question details
        question_text = self._format_question(current_question)
        
        # Assemble full prompt
        prompt = f"""{self.prompt_template}

---

## INTERVIEW CONTEXT
{context_text}

## CONVERSATION HISTORY
{history_text}

## CURRENT TURN

### Current Question:
{question_text}

### Candidate's Answer:
{candidate_answer}

---

Hãy phân tích câu trả lời của ứng viên, đánh giá chất lượng, và quyết định hành động tiếp theo.
Trả về kết quả dưới dạng JSON với cấu trúc đã được định nghĩa trong system prompt.
"""
        return prompt
    
    def _format_context(self, context: Dict[str, Any]) -> str:
        """Format interview context for prompt."""
        if not context:
            return "No additional context provided."
        
        lines = []
        if "position" in context:
            lines.append(f"- Vị trí: {context['position']}")
        if "level" in context:
            lines.append(f"- Cấp độ: {context['level']}")
        if "candidate_name" in context:
            lines.append(f"- Tên ứng viên: {context['candidate_name']}")
        
        return "\n".join(lines) if lines else "No context provided."
    
    def _format_history(self, history: List[Dict]) -> str:
        """Format conversation history for prompt."""
        if not history:
            return "Đây là lượt đầu tiên của cuộc phỏng vấn."
        
        lines = []
        for idx, turn in enumerate(history):
            lines.append(f"\n### Turn {idx + 1}:")
            lines.append(f"Q: {turn.get('question', 'N/A')}")
            lines.append(f"A: {turn.get('answer', 'N/A')}")
            if "score" in turn:
                lines.append(f"Score: {turn['score']}")
        
        return "\n".join(lines)
    
    def _format_question(self, question: Dict[str, Any]) -> str:
        """Format current question details for prompt."""
        lines = [
            f"**ID**: {question.get('question_id', 'N/A')}",
            f"**Category**: {question.get('category', 'N/A')}",
            f"**Difficulty**: {question.get('difficulty', 'N/A')}",
            f"**Question**: {question.get('question_text', 'N/A')}"
        ]
        
        if "key_points" in question:
            lines.append(f"**Key Points**: {', '.join(question['key_points'])}")
        
        if "evaluation_criteria" in question:
            lines.append(f"**Evaluation Criteria**: {', '.join(question['evaluation_criteria'])}")
        
        return "\n".join(lines)
    
    def _validate_output(self, result: Dict[str, Any]) -> bool:
        """Validate that generated output meets quality standards."""
        # Check required top-level fields
        required_fields = ["turn_evaluation", "next_action"]
        if not all(field in result for field in required_fields):
            self.logger.error("Output missing required fields")
            return False
        
        # Validate turn_evaluation structure
        turn_eval = result["turn_evaluation"]
        if "answer_quality" not in turn_eval or "overall_score" not in turn_eval["answer_quality"]:
            self.logger.error("Missing answer_quality or overall_score")
            return False
        
        # Validate score range
        score = turn_eval["answer_quality"]["overall_score"]
        if not (self.score_range[0] <= score <= self.score_range[1]):
            self.logger.error(f"Score {score} out of range {self.score_range}")
            return False
        
        # Validate next_action
        next_action = result["next_action"]
        if "action_type" not in next_action or "ai_response" not in next_action:
            self.logger.error("Missing action_type or ai_response in next_action")
            return False
        
        valid_actions = self.conversation_settings.get("action_types", [])
        if next_action["action_type"] not in valid_actions:
            self.logger.error(f"Invalid action_type: {next_action['action_type']}")
            return False
        
        return True
    
    def process_turn(
        self,
        interview_id: str,
        current_question: Dict[str, Any],
        candidate_answer: str,
        conversation_history: Optional[List[Dict]] = None,
        interview_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Convenience method to process a conversation turn.
        
        Args:
            interview_id: Interview session ID
            current_question: Current question being asked
            candidate_answer: Candidate's answer text
            conversation_history: Previous turns
            interview_context: Context about the interview
        
        Returns:
            Result dictionary with turn evaluation and next action
        """
        return self.process({
            "interview_id": interview_id,
            "current_question": current_question,
            "candidate_answer": candidate_answer,
            "conversation_history": conversation_history or [],
            "interview_context": interview_context or {}
        })
