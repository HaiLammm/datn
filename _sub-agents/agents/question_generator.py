"""
QuestionCraft AI - Interview Question Generator Agent
Generates interview questions from Job Description and CV
"""

from typing import Dict, Any, List
from .base_agent import BaseAgent


class QuestionGeneratorAgent(BaseAgent):
    """
    Agent for generating interview questions based on JD and CV.
    
    Persona: AI Interview Question Architect
    - Systematic, precise, structured
    - Generates scenario-based, level-appropriate questions
    - Maintains 60-20-20 distribution (Technical-Behavioral-Situational)
    """
    
    def __init__(self, config_path: str = None):
        """
        Initialize QuestionCraft AI agent.
        
        Args:
            config_path: Path to config file (defaults to standard location)
        """
        if config_path is None:
            import os
            config_path = os.path.join(
                os.path.dirname(__file__),
                '../configs/question_generator_config.json'
            )
        super().__init__(config_path)
        
        # Load quality settings
        self.quality_settings = self.config.get("quality_settings", {})
        self.min_questions = self.quality_settings.get("min_questions_per_level", 3)
        self.required_fields = self.quality_settings.get("required_fields", [])
        self.category_distribution = self.quality_settings.get("category_distribution", {})
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate interview questions from JD and CV.
        
        Args:
            input_data: {
                "job_description": str,  # Job description text
                "cv_content": str,       # Candidate CV text
                "position_level": str,   # "junior", "middle", or "senior"
                "num_questions": int,    # Number of questions to generate (optional)
                "focus_areas": List[str] # Specific skills/areas to focus on (optional)
            }
        
        Returns:
            {
                "status": "success" or "error",
                "questions": [
                    {
                        "question_id": str,
                        "category": str,
                        "difficulty": str,
                        "question_text": str,
                        "key_points": List[str],
                        "ideal_answer_outline": str,
                        "evaluation_criteria": List[str]
                    },
                    ...
                ],
                "metadata": {
                    "total_questions": int,
                    "distribution": {
                        "technical": int,
                        "behavioral": int,
                        "situational": int
                    },
                    "generated_at": str,
                    "model_used": str
                },
                "error": str (if status == "error")
            }
        """
        # Validate input
        if not self._validate_input(input_data):
            return {
                "status": "error",
                "error": "Invalid input data. Required: job_description, cv_content, position_level"
            }
        
        try:
            # Build prompt
            prompt = self._build_prompt(input_data)
            
            # Log request
            if self.config.get("logging", {}).get("log_requests", False):
                self.logger.info(f"Generating questions for {input_data.get('position_level')} position")
            
            # Call API with retry
            response = self._retry_on_failure(
                self._call_ollama_api,
                prompt
            )
            
            # Parse response
            result = self._parse_json_response(response)
            
            # Validate output quality
            if not self._validate_output(result):
                raise ValueError("Generated questions do not meet quality standards")
            
            # Add metadata
            result["status"] = "success"
            result["metadata"] = {
                "total_questions": len(result.get("questions", [])),
                "distribution": self._calculate_distribution(result.get("questions", [])),
                "model_used": self.model
            }
            
            # Log response
            if self.config.get("logging", {}).get("log_responses", False):
                self.logger.info(f"Successfully generated {result['metadata']['total_questions']} questions")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error generating questions: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate input data has required fields."""
        required = ["job_description", "cv_content", "position_level"]
        return all(field in input_data and input_data[field] for field in required)
    
    def _build_prompt(self, input_data: Dict[str, Any]) -> str:
        """Build complete prompt from template and input data."""
        # Extract input fields
        job_description = input_data["job_description"]
        cv_content = input_data["cv_content"]
        position_level = input_data["position_level"]
        num_questions = input_data.get("num_questions", 10)
        focus_areas = input_data.get("focus_areas", [])
        
        # Build focus areas text
        focus_text = ""
        if focus_areas:
            focus_text = f"\n\nCác lĩnh vực cần tập trung đặc biệt: {', '.join(focus_areas)}"
        
        # Insert into template
        prompt = f"""{self.prompt_template}

---

## INPUT DATA

### Job Description:
{job_description}

### Candidate CV:
{cv_content}

### Position Level: {position_level}

### Number of Questions Requested: {num_questions}
{focus_text}

---

Hãy phân tích JD và CV, sau đó tạo ra {num_questions} câu hỏi phỏng vấn phù hợp với cấp độ {position_level}.
Đảm bảo tuân thủ tỷ lệ phân bố: 60% Technical, 20% Behavioral, 20% Situational.

Trả về kết quả dưới dạng JSON với cấu trúc đã được định nghĩa trong system prompt.
"""
        return prompt
    
    def _validate_output(self, result: Dict[str, Any]) -> bool:
        """Validate that generated output meets quality standards."""
        if "questions" not in result:
            self.logger.error("Output missing 'questions' field")
            return False
        
        questions = result["questions"]
        
        # Check minimum number of questions
        if len(questions) < self.min_questions:
            self.logger.error(f"Generated only {len(questions)} questions, minimum is {self.min_questions}")
            return False
        
        # Validate each question has required fields
        for idx, question in enumerate(questions):
            if not self._validate_required_fields(question, self.required_fields):
                self.logger.error(f"Question {idx} missing required fields")
                return False
        
        # Validate category distribution
        distribution = self._calculate_distribution(questions)
        total = sum(distribution.values())
        
        if total > 0:
            technical_ratio = distribution.get("technical", 0) / total
            expected_ratio = self.category_distribution.get("technical", 0.6)
            
            # Allow 10% tolerance
            if abs(technical_ratio - expected_ratio) > 0.15:
                self.logger.warning(
                    f"Category distribution off target: {technical_ratio:.2f} vs {expected_ratio:.2f}"
                )
        
        return True
    
    def _calculate_distribution(self, questions: List[Dict]) -> Dict[str, int]:
        """Calculate category distribution of questions."""
        distribution = {"technical": 0, "behavioral": 0, "situational": 0}
        
        for question in questions:
            category = question.get("category", "").lower()
            if category in distribution:
                distribution[category] += 1
        
        return distribution
    
    def generate_questions(
        self,
        job_description: str,
        cv_content: str,
        position_level: str,
        num_questions: int = 10,
        focus_areas: List[str] = None
    ) -> Dict[str, Any]:
        """
        Convenience method to generate questions.
        
        Args:
            job_description: Job description text
            cv_content: Candidate CV text
            position_level: "junior", "middle", or "senior"
            num_questions: Number of questions to generate
            focus_areas: Specific skills/areas to focus on
        
        Returns:
            Result dictionary with questions
        """
        return self.process({
            "job_description": job_description,
            "cv_content": cv_content,
            "position_level": position_level,
            "num_questions": num_questions,
            "focus_areas": focus_areas or []
        })
