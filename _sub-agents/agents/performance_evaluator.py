"""
EvalMaster AI - Performance Evaluator Agent
Comprehensive interview evaluation with detailed scoring and recommendations
"""

from typing import Dict, Any, List
from .base_agent import BaseAgent


class PerformanceEvaluatorAgent(BaseAgent):
    """
    Agent for comprehensive interview performance evaluation.
    
    Persona: Senior Technical Interviewer
    - Professional, analytical, objective
    - Evidence-based scoring with concrete examples
    - 3-dimension analysis: Technical + Communication + Behavioral
    """
    
    def __init__(self, config_path: str = None):
        """
        Initialize EvalMaster AI agent.
        
        Args:
            config_path: Path to config file (defaults to standard location)
        """
        if config_path is None:
            import os
            config_path = os.path.join(
                os.path.dirname(__file__),
                '../configs/performance_evaluator_config.json'
            )
        super().__init__(config_path)
        
        # Load evaluation settings
        self.evaluation_settings = self.config.get("evaluation_settings", {})
        self.scoring_dimensions = self.evaluation_settings.get("scoring_dimensions", {})
        self.grade_thresholds = self.evaluation_settings.get("grade_thresholds", {})
        self.hiring_thresholds = self.evaluation_settings.get("hiring_decision_thresholds", {})
        
        # Load report settings
        self.report_settings = self.config.get("report_settings", {})
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate complete interview performance and generate comprehensive report.
        
        Args:
            input_data: {
                "interview_id": str,
                "candidate_info": {
                    "name": str,
                    "position": str,
                    "level": str
                },
                "interview_transcript": List[Dict],  # Full conversation history
                "questions_asked": List[Dict],       # All questions with metadata
                "turn_evaluations": List[Dict],      # Per-turn scores from ConversationAgent
                "interview_duration_minutes": int
            }
        
        Returns:
            {
                "status": "success" or "error",
                "overall_evaluation": {
                    "final_score": float (0-10),
                    "grade": str,  # "excellent", "good", "average", "poor"
                    "hiring_recommendation": str  # "strong_hire", "hire", "consider", "no_hire"
                },
                "dimension_scores": {
                    "technical_competency": {
                        "score": float (0-10),
                        "weight": float,
                        "sub_scores": {
                            "knowledge_breadth": float,
                            "knowledge_depth": float,
                            "problem_solving": float,
                            "technical_accuracy": float
                        },
                        "evidence": List[str],
                        "analysis": str
                    },
                    "communication_skills": {
                        "score": float (0-10),
                        "weight": float,
                        "sub_scores": {...},
                        "evidence": List[str],
                        "analysis": str
                    },
                    "behavioral_fit": {
                        "score": float (0-10),
                        "weight": float,
                        "sub_scores": {...},
                        "evidence": List[str],
                        "analysis": str
                    }
                },
                "detailed_analysis": {
                    "key_strengths": List[str],
                    "areas_for_improvement": List[str],
                    "notable_moments": List[str],
                    "red_flags": List[str] (if any)
                },
                "recommendations": {
                    "hiring_decision": str,
                    "reasoning": str,
                    "suggested_role_fit": str,
                    "onboarding_suggestions": List[str] (if hire),
                    "development_areas": List[str]
                },
                "metadata": {
                    "total_questions": int,
                    "questions_by_category": Dict[str, int],
                    "interview_duration": int,
                    "evaluation_timestamp": str,
                    "model_used": str
                },
                "error": str (if status == "error")
            }
        """
        # Validate input
        if not self._validate_input(input_data):
            return {
                "status": "error",
                "error": "Invalid input. Required: interview_id, candidate_info, interview_transcript"
            }
        
        try:
            # Build prompt
            prompt = self._build_prompt(input_data)
            
            # Log request
            if self.config.get("logging", {}).get("log_requests", False):
                candidate_name = input_data.get("candidate_info", {}).get("name", "Unknown")
                self.logger.info(f"Evaluating interview for {candidate_name}")
            
            # Call API with retry
            response = self._retry_on_failure(
                self._call_ollama_api,
                prompt
            )
            
            # Parse response
            result = self._parse_json_response(response)
            
            # Validate output
            if not self._validate_output(result):
                raise ValueError("Generated evaluation does not meet quality standards")
            
            # Add status and metadata
            result["status"] = "success"
            result["metadata"] = self._build_metadata(input_data)
            
            # Log response
            if self.config.get("logging", {}).get("log_responses", False):
                final_score = result.get("overall_evaluation", {}).get("final_score", 0)
                recommendation = result.get("overall_evaluation", {}).get("hiring_recommendation", "N/A")
                self.logger.info(f"Evaluation complete. Score: {final_score}, Recommendation: {recommendation}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error evaluating interview performance: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate input data has required fields."""
        required = ["interview_id", "candidate_info", "interview_transcript"]
        return all(field in input_data for field in required)
    
    def _build_prompt(self, input_data: Dict[str, Any]) -> str:
        """Build complete prompt with interview data."""
        # Extract input fields
        interview_id = input_data["interview_id"]
        candidate_info = input_data["candidate_info"]
        transcript = input_data["interview_transcript"]
        questions = input_data.get("questions_asked", [])
        turn_evaluations = input_data.get("turn_evaluations", [])
        duration = input_data.get("interview_duration_minutes", 0)
        
        # Format sections
        candidate_text = self._format_candidate_info(candidate_info)
        transcript_text = self._format_transcript(transcript)
        questions_text = self._format_questions(questions)
        turn_eval_text = self._format_turn_evaluations(turn_evaluations)
        
        # Assemble full prompt
        prompt = f"""{self.prompt_template}

---

## INTERVIEW DATA

### Interview ID: {interview_id}

### Candidate Information:
{candidate_text}

### Interview Duration: {duration} minutes

### Questions Asked:
{questions_text}

### Full Interview Transcript:
{transcript_text}

### Per-Turn Evaluations:
{turn_eval_text}

---

Hãy đánh giá toàn diện hiệu suất phỏng vấn của ứng viên.
Phân tích theo 3 chiều: Technical Competency (50%), Communication Skills (25%), Behavioral Fit (25%).
Cung cấp điểm số có bằng chứng cụ thể, phân tích chi tiết, và khuyến nghị tuyển dụng rõ ràng.

Trả về kết quả dưới dạng JSON với cấu trúc đã được định nghĩa trong system prompt.
"""
        return prompt
    
    def _format_candidate_info(self, info: Dict[str, Any]) -> str:
        """Format candidate information for prompt."""
        lines = [
            f"- Tên: {info.get('name', 'N/A')}",
            f"- Vị trí ứng tuyển: {info.get('position', 'N/A')}",
            f"- Cấp độ: {info.get('level', 'N/A')}"
        ]
        return "\n".join(lines)
    
    def _format_transcript(self, transcript: List[Dict]) -> str:
        """Format interview transcript for prompt."""
        if not transcript:
            return "No transcript provided."
        
        lines = []
        for idx, turn in enumerate(transcript):
            lines.append(f"\n### Turn {idx + 1}:")
            lines.append(f"**AI**: {turn.get('ai_message', 'N/A')}")
            lines.append(f"**Candidate**: {turn.get('candidate_message', 'N/A')}")
        
        return "\n".join(lines)
    
    def _format_questions(self, questions: List[Dict]) -> str:
        """Format questions list for prompt."""
        if not questions:
            return "No questions provided."
        
        lines = []
        for idx, q in enumerate(questions):
            lines.append(f"\n{idx + 1}. [{q.get('category', 'N/A')}] {q.get('question_text', 'N/A')}")
            lines.append(f"   Difficulty: {q.get('difficulty', 'N/A')}")
        
        return "\n".join(lines)
    
    def _format_turn_evaluations(self, evaluations: List[Dict]) -> str:
        """Format per-turn evaluations for prompt."""
        if not evaluations:
            return "No per-turn evaluations provided."
        
        lines = []
        for idx, eval_data in enumerate(evaluations):
            quality = eval_data.get("answer_quality", {})
            lines.append(f"\n### Turn {idx + 1} Score: {quality.get('overall_score', 'N/A')}")
            lines.append(f"- Technical: {quality.get('technical_accuracy', 'N/A')}")
            lines.append(f"- Communication: {quality.get('communication_clarity', 'N/A')}")
            lines.append(f"- Depth: {quality.get('depth_of_knowledge', 'N/A')}")
            
            observations = eval_data.get("key_observations", [])
            if observations:
                lines.append(f"- Observations: {'; '.join(observations)}")
        
        return "\n".join(lines)
    
    def _build_metadata(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Build metadata section for result."""
        questions = input_data.get("questions_asked", [])
        
        # Count questions by category
        category_counts = {}
        for q in questions:
            cat = q.get("category", "unknown")
            category_counts[cat] = category_counts.get(cat, 0) + 1
        
        return {
            "total_questions": len(questions),
            "questions_by_category": category_counts,
            "interview_duration": input_data.get("interview_duration_minutes", 0),
            "model_used": self.model
        }
    
    def _validate_output(self, result: Dict[str, Any]) -> bool:
        """Validate that generated output meets quality standards."""
        # Check required top-level fields
        required_fields = ["overall_evaluation", "dimension_scores", "detailed_analysis", "recommendations"]
        if not all(field in result for field in required_fields):
            self.logger.error("Output missing required top-level fields")
            return False
        
        # Validate overall_evaluation
        overall = result["overall_evaluation"]
        if not all(key in overall for key in ["final_score", "grade", "hiring_recommendation"]):
            self.logger.error("Missing fields in overall_evaluation")
            return False
        
        # Validate dimension_scores
        dimension_scores = result["dimension_scores"]
        required_dimensions = ["technical_competency", "communication_skills", "behavioral_fit"]
        if not all(dim in dimension_scores for dim in required_dimensions):
            self.logger.error("Missing required scoring dimensions")
            return False
        
        # Validate each dimension has evidence
        if self.report_settings.get("include_evidence", True):
            for dim_name, dim_data in dimension_scores.items():
                if "evidence" not in dim_data or len(dim_data["evidence"]) < 1:
                    self.logger.warning(f"Dimension {dim_name} lacks evidence")
        
        # Validate score consistency
        if self.config.get("quality_settings", {}).get("validate_score_consistency", True):
            final_score = overall["final_score"]
            
            # Calculate weighted score from dimensions
            weighted_sum = 0
            for dim_name, dim_data in dimension_scores.items():
                score = dim_data.get("score", 0)
                weight = dim_data.get("weight", 0)
                weighted_sum += score * weight
            
            # Allow 0.5 tolerance
            if abs(final_score - weighted_sum) > 0.5:
                self.logger.warning(
                    f"Score inconsistency: final={final_score}, weighted={weighted_sum:.2f}"
                )
        
        return True
    
    def evaluate_interview(
        self,
        interview_id: str,
        candidate_info: Dict[str, Any],
        interview_transcript: List[Dict],
        questions_asked: List[Dict] = None,
        turn_evaluations: List[Dict] = None,
        interview_duration_minutes: int = 0
    ) -> Dict[str, Any]:
        """
        Convenience method to evaluate an interview.
        
        Args:
            interview_id: Interview session ID
            candidate_info: Candidate information
            interview_transcript: Full conversation history
            questions_asked: All questions with metadata
            turn_evaluations: Per-turn scores
            interview_duration_minutes: Interview duration
        
        Returns:
            Result dictionary with comprehensive evaluation
        """
        return self.process({
            "interview_id": interview_id,
            "candidate_info": candidate_info,
            "interview_transcript": interview_transcript,
            "questions_asked": questions_asked or [],
            "turn_evaluations": turn_evaluations or [],
            "interview_duration_minutes": interview_duration_minutes
        })
