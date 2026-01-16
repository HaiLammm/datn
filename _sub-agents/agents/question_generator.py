"""
QuestionCraft AI - Interview Question Generator Agent
Generates interview questions from Job Description and CV
"""

import json
import re
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
        
        # Initialize current_input for validation
        self.current_input = {}
        
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
            # Store input for validation
            self.current_input = input_data
            
            # Build prompt
            prompt = self._build_prompt(input_data)
            
            # Log request
            if self.config.get("logging", {}).get("log_requests", False):
                self.logger.info(f"Generating questions for {input_data.get('position_level')} position")
            
            # Override model params for single question generation (reduce tokens to prevent over-generation)
            model_params = None
            num_questions = input_data.get("num_questions", 10)
            if num_questions == 1:
                model_params = {
                    "num_predict": 1024,  # Reduced from 4096 to prevent generating too many questions
                    "temperature": 0.5,    # Lower temperature for more focused output
                }
                self.logger.info("Using reduced num_predict (1024) for single question generation")
            
            # Call API with retry
            response = self._retry_on_failure(
                self._call_ollama_api,
                prompt,
                model_params  # Pass override params
            )
            
            # Parse response
            result = self._parse_json_response(response)
            
            self.logger.info(f"Parsed result type: {type(result)}, keys: {list(result.keys()) if isinstance(result, dict) else 'N/A'}")
            if isinstance(result, dict) and 'questions' in result:
                self.logger.info(f"Found {len(result['questions'])} questions")
                if result['questions']:
                    first_q_keys = list(result['questions'][0].keys()) if isinstance(result['questions'][0], dict) else []
                    self.logger.info(f"First question keys: {first_q_keys}")
            
            # Handle case where model returns array instead of {"questions": [...]}
            if isinstance(result, list):
                self.logger.warning("Model returned array instead of object with 'questions' key. Wrapping...")
                result = {"questions": result}
            elif "questions" not in result and isinstance(result, dict):
                # If it's an object but doesn't have "questions", check if it has question-like keys
                if any(key.startswith("question") for key in result.keys()):
                    self.logger.warning("Model returned object without 'questions' key. Wrapping single question...")
                    result = {"questions": [result]}
            
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
        existing_questions = input_data.get("existing_questions", [])
        
        # Build focus areas text
        focus_text = ""
        if focus_areas:
            focus_text = f"\n\nCác lĩnh vực cần tập trung đặc biệt: {', '.join(focus_areas)}"
        
        # Build existing questions context (for sequential generation)
        existing_text = ""
        if existing_questions:
            existing_text = "\n\n### Already Generated Questions (DO NOT DUPLICATE):\n"
            for idx, q in enumerate(existing_questions, 1):
                existing_text += f"{idx}. [{q.get('category', 'unknown')}] {q.get('question_text', '')}\n"
            existing_text += "\nIMPORTANT: Generate NEW questions that are different from the above. Cover different topics/aspects."
        
        # Build instruction based on number of questions
        if num_questions == 1:
            instruction = f"""Hãy phân tích JD và CV, sau đó tạo ra CHÍNH XÁC 1 (MỘT) câu hỏi phỏng vấn duy nhất phù hợp với cấp độ {position_level}.

QUAN TRỌNG: 
- Chỉ tạo 1 câu hỏi duy nhất, KHÔNG tạo nhiều câu hỏi
- Câu hỏi phải có question_id là "Q{str(len(existing_questions) + 1).zfill(3)}" (ví dụ: Q001, Q002, Q003...)
- category PHẢI là một trong ba giá trị: "technical", "behavioral", hoặc "situational" (KHÔNG kết hợp)
{f"- Tránh trùng lặp với {len(existing_questions)} câu đã có ở trên." if existing_questions else ""}

Trả về kết quả dưới dạng JSON:
{{
  "questions": [
    {{
      "question_id": "Q{str(len(existing_questions) + 1).zfill(3)}",
      "category": "technical",
      "difficulty": "{position_level}",
      "question_text": "...",
      "key_points": [...],
      "ideal_answer_outline": "...",
      "evaluation_criteria": {{"excellent": "...", "good": "...", "average": "..."}}
    }}
  ]
}}

LƯU Ý: category chỉ được là "technical", "behavioral", hoặc "situational" - KHÔNG sử dụng kết hợp như "behavioral/situational"."""
        else:
            instruction = f"""Hãy phân tích JD và CV, sau đó tạo ra {num_questions} câu hỏi phỏng vấn phù hợp với cấp độ {position_level}.
Đảm bảo tuân thủ tỷ lệ phân bố: 60% Technical, 20% Behavioral, 20% Situational.
{f"Tránh tạo câu hỏi trùng lặp với {len(existing_questions)} câu đã có ở trên." if existing_questions else ""}

Trả về kết quả dưới dạng JSON với cấu trúc đã được định nghĩa trong system prompt."""

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
{existing_text}

---

{instruction}
"""
        return prompt
    
    def _validate_output(self, result: Dict[str, Any]) -> bool:
        """Validate that generated output meets quality standards."""
        if "questions" not in result:
            self.logger.error("Output missing 'questions' field")
            return False
        
        questions = result["questions"]
        
        # For sequential generation (num_questions=1), only require 1 question
        # This is stored in the current input context
        requested_count = self.current_input.get("num_questions", self.min_questions)
        min_required = min(requested_count, self.min_questions)
        
        # Check minimum number of questions
        if len(questions) < min_required:
            self.logger.error(f"Generated only {len(questions)} questions, minimum is {min_required} (requested: {requested_count})")
            return False
        
        # Validate each question has required fields
        valid_questions = 0
        for idx, question in enumerate(questions):
            if self._validate_required_fields(question, self.required_fields):
                valid_questions += 1
            else:
                self.logger.warning(f"Question {idx} missing required fields, will be excluded")
        
        # Accept if we have at least min_required valid questions
        if valid_questions < min_required:
            self.logger.error(f"Only {valid_questions} valid questions, minimum is {min_required}")
            return False
        
        if valid_questions < len(questions):
            self.logger.warning(f"Accepted {valid_questions}/{len(questions)} questions after validation")
        
        # Validate category distribution (warning only, don't fail)
        distribution = self._calculate_distribution(questions)
        total = sum(distribution.values())
        
        if total > 0:
            technical_ratio = distribution.get("technical", 0) / total
            expected_ratio = self.category_distribution.get("technical", 0.6)
            
            # Allow 20% tolerance (was 15%)
            if abs(technical_ratio - expected_ratio) > 0.20:
                self.logger.warning(
                    f"Category distribution off target: {technical_ratio:.2f} vs {expected_ratio:.2f}"
                )
        
        return True
    
    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """
        Parse JSON from model response, with special handling for common issues.
        Overrides base class method for more lenient parsing.
        """
        # Remove control characters that break JSON parsing (except \n, \r, \t)
        # Control characters are ASCII 0-31 except for tab(9), newline(10), carriage return(13)
        import re
        response = ''.join(char if (ord(char) >= 32 or char in '\t\n\r') else ' ' for char in response)
        
        # Try to extract JSON from markdown code blocks
        if "```json" in response:
            start = response.find("```json") + 7
            end = response.find("```", start)
            if end == -1:  # No closing fence
                response = response[start:].strip()
            else:
                response = response[start:end].strip()
        elif "```" in response:
            start = response.find("```") + 3
            end = response.find("```", start)
            if end == -1:  # No closing fence
                response = response[start:].strip()
            else:
                response = response[start:end].strip()
        
        # Clean up common JSON issues
        # 1. Remove trailing commas before ] or }
        response = re.sub(r',\s*([\]}])', r'\1', response)
        
        # 2. Fix missing commas between array elements or object properties
        # Add comma between }{
        response = re.sub(r'\}\s*\{', '},{', response)
        # Add comma between ][ 
        response = re.sub(r'\]\s*\[', '],[', response)
        
        # 3. Try to find where JSON ends if it got truncated
        # Look for the last valid closing bracket
        if response.count('[') > response.count(']'):
            # Array not closed, try to close it
            self.logger.warning(f"JSON has unclosed arrays: {response.count('[')} [ vs {response.count(']')} ]")
            response = response + ']' * (response.count('[') - response.count(']'))
        if response.count('{') > response.count('}'):
            # Object not closed, try to close it  
            self.logger.warning(f"JSON has unclosed objects: {response.count('{')} {{ vs {response.count('}')} }}")
            response = response + '}' * (response.count('{') - response.count('}'))
        
        # 4. Remove any trailing incomplete strings or values
        # Find the last complete JSON value before truncation
        response = re.sub(r',\s*$', '', response)  # Remove trailing comma
        response = re.sub(r':\s*"[^"]*$', '', response)  # Remove incomplete string value
        response = re.sub(r':\s*$', ': ""', response)  # Fill empty value
        
        # 5. Try to fix common structural issues
        # Ensure proper key-value format
        response = re.sub(r'"\s*:\s*\n\s*"', '": "', response)
        
        try:
            parsed = json.loads(response)
            return parsed
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse JSON: {e}")
            self.logger.error(f"Error at position {e.pos}: char {response[max(0,e.pos-20):e.pos+20]}")
            self.logger.error(f"Attempted to parse (first 1000 chars): {response[:1000]}...")
            if len(response) > 1000:
                self.logger.error(f"Middle (around error): ...{response[max(0,e.pos-200):min(len(response),e.pos+200)]}...")
            self.logger.error(f"Last 500 chars: ...{response[-500:]}")
            
            # ADVANCED REPAIR: Try to fix the specific error location
            try:
                # Try to fix the issue at the error position
                if e.msg and "Expecting ',' delimiter" in e.msg:
                    self.logger.warning(f"Attempting to add missing comma at position {e.pos}")
                    # Insert comma at error position
                    fixed = response[:e.pos] + ',' + response[e.pos:]
                    parsed = json.loads(fixed)
                    self.logger.info("✅ Successfully fixed JSON by adding comma")
                    return parsed
                elif e.msg and "Expecting property name" in e.msg:
                    self.logger.warning(f"Attempting to close object at position {e.pos}")
                    # Close the object properly
                    fixed = response[:e.pos] + '}' + response[e.pos:]
                    parsed = json.loads(fixed)
                    self.logger.info("✅ Successfully fixed JSON by closing object")
                    return parsed
            except Exception as fix_err:
                self.logger.debug(f"Advanced repair failed: {fix_err}")
            
            # Last resort: try to extract just the questions array
            match = re.search(r'\[\s*\{.*\}\s*\]', response, re.DOTALL)
            if match:
                try:
                    array_str = match.group(0)
                    # Fix trailing commas
                    array_str = re.sub(r',\s*([\]}])', r'\1', array_str)
                    
                    # Try to find complete question objects even if array isn't closed
                    # Extract all complete question objects
                    question_pattern = r'\{[^{}]*"question_id"[^{}]*"question_text"[^{}]*\}'
                    questions = re.findall(question_pattern, array_str, re.DOTALL)
                    
                    if questions:
                        self.logger.warning(f"Extracted {len(questions)} complete question objects from malformed JSON")
                        # Parse each question individually
                        parsed_questions = []
                        for q_str in questions:
                            try:
                                q_str = re.sub(r',\s*([\]}])', r'\1', q_str)
                                parsed_q = json.loads(q_str)
                                parsed_questions.append(parsed_q)
                            except:
                                continue
                        
                        if parsed_questions:
                            self.logger.info(f"Successfully parsed {len(parsed_questions)} questions from malformed response")
                            return {"questions": parsed_questions}
                    
                    # Original fallback
                    parsed = json.loads(array_str)
                    self.logger.warning("Extracted questions array from malformed JSON")
                    return {"questions": parsed} if isinstance(parsed, list) else parsed
                except:
                    pass
            
            raise ValueError(f"Invalid JSON in model response: {e}")
    
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
        focus_areas: List[str] = None,
        existing_questions: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Convenience method to generate questions.
        
        Args:
            job_description: Job description text
            cv_content: Candidate CV text
            position_level: "junior", "middle", or "senior"
            num_questions: Number of questions to generate
            focus_areas: Specific skills/areas to focus on
            existing_questions: List of already-generated questions to avoid duplicates (optional)
        
        Returns:
            Result dictionary with questions
        """
        return self.process({
            "job_description": job_description,
            "cv_content": cv_content,
            "position_level": position_level,
            "num_questions": num_questions,
            "focus_areas": focus_areas or [],
            "existing_questions": existing_questions or []
        })
