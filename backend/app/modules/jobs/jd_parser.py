"""
JD Parser - AI-powered Job Description parsing with skill extraction.

This module provides a JDParser class that uses LLM (Ollama) to parse
job descriptions and extract structured requirements including:
- Required skills (normalized using skill taxonomy)
- Nice-to-have skills
- Minimum experience years
- Normalized job title
- Key responsibilities

Features:
- Async LLM integration with Ollama
- Skill normalization using existing SkillExtractor
- JSON parsing with regex fallback
- Robust error handling
"""

import json
import logging
import re
from typing import Any, Dict, List, Optional

import httpx

from app.core.config import settings
from app.modules.ai.skill_extractor import skill_extractor

logger = logging.getLogger(__name__)

# Timeout for LLM requests (seconds)
_LLM_TIMEOUT = 120


class ParsedJDRequirements:
    """
    Structured container for parsed JD requirements.
    
    Attributes:
        required_skills: List of normalized required skill names.
        nice_to_have_skills: List of normalized optional skill names.
        min_experience_years: Minimum years of experience required (or None).
        job_title_normalized: Normalized job title string.
        key_responsibilities: List of key job responsibilities.
        skill_categories: Dict mapping categories to skills (for analysis).
        raw_llm_output: Original LLM response for debugging.
    """
    
    def __init__(
        self,
        required_skills: Optional[List[str]] = None,
        nice_to_have_skills: Optional[List[str]] = None,
        min_experience_years: Optional[int] = None,
        job_title_normalized: Optional[str] = None,
        key_responsibilities: Optional[List[str]] = None,
        skill_categories: Optional[Dict[str, List[str]]] = None,
        raw_llm_output: Optional[str] = None,
    ):
        self.required_skills = required_skills or []
        self.nice_to_have_skills = nice_to_have_skills or []
        self.min_experience_years = min_experience_years
        self.job_title_normalized = job_title_normalized
        self.key_responsibilities = key_responsibilities or []
        self.skill_categories = skill_categories or {}
        self.raw_llm_output = raw_llm_output
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "required_skills": self.required_skills,
            "nice_to_have_skills": self.nice_to_have_skills,
            "min_experience_years": self.min_experience_years,
            "job_title_normalized": self.job_title_normalized,
            "key_responsibilities": self.key_responsibilities,
            "skill_categories": self.skill_categories,
        }


class JDParser:
    """
    AI-powered Job Description parser using Ollama LLM.
    
    This class extracts structured requirements from job description text,
    normalizes skills using the existing skill taxonomy, and returns
    structured data suitable for matching with CV skills.
    
    Example:
        >>> parser = JDParser()
        >>> result = await parser.parse_jd('''
        ...     Senior Python Developer
        ...     Requirements: 3+ years Python, FastAPI, PostgreSQL
        ...     Nice to have: Docker, AWS
        ... ''')
        >>> print(result.required_skills)
        ['python', 'fastapi', 'postgresql']
        >>> print(result.min_experience_years)
        3
    """
    
    def __init__(
        self,
        ollama_url: Optional[str] = None,
        model: Optional[str] = None,
    ):
        """
        Initialize JDParser with Ollama configuration.
        
        Args:
            ollama_url: Ollama API URL (default from settings).
            model: LLM model name (default from settings).
        """
        self.ollama_url = ollama_url or settings.OLLAMA_URL
        self.model = model or settings.LLM_MODEL
        logger.info(f"JDParser initialized with model: {self.model}")
    
    async def parse_jd(self, jd_text: str) -> ParsedJDRequirements:
        """
        Parse a job description and extract structured requirements.
        
        Args:
            jd_text: The full job description text.
            
        Returns:
            ParsedJDRequirements containing extracted and normalized data.
            
        Raises:
            ValueError: If jd_text is empty or too short.
            TimeoutError: If LLM request times out.
        """
        if not jd_text or len(jd_text.strip()) < 20:
            logger.warning("JD text too short for meaningful parsing")
            return ParsedJDRequirements()
        
        logger.info(f"Parsing JD text ({len(jd_text)} chars)")
        
        try:
            # Step 1: Call LLM to extract raw requirements
            prompt = self._build_prompt(jd_text)
            llm_response = await self._call_ollama(prompt)
            
            # Step 2: Parse LLM response into structured data
            raw_data = self._parse_llm_response(llm_response)
            
            # Step 3: Normalize skills using skill taxonomy
            required_skills = self._normalize_skills(
                raw_data.get("required_skills", [])
            )
            nice_to_have_skills = self._normalize_skills(
                raw_data.get("nice_to_have_skills", [])
            )
            
            # Step 4: Categorize skills for analysis
            all_skills = required_skills + nice_to_have_skills
            skill_categories = self._categorize_skills(all_skills)
            
            # Step 5: Build result
            result = ParsedJDRequirements(
                required_skills=required_skills,
                nice_to_have_skills=nice_to_have_skills,
                min_experience_years=raw_data.get("min_experience_years"),
                job_title_normalized=raw_data.get("job_title_normalized"),
                key_responsibilities=raw_data.get("key_responsibilities", []),
                skill_categories=skill_categories,
                raw_llm_output=llm_response,
            )
            
            logger.info(
                f"JD parsed successfully: {len(required_skills)} required skills, "
                f"{len(nice_to_have_skills)} nice-to-have skills"
            )
            return result
            
        except TimeoutError:
            logger.error("LLM timeout during JD parsing")
            raise
        except Exception as e:
            logger.error(f"Error parsing JD: {e}")
            # Return empty result on error (don't crash)
            return ParsedJDRequirements()
    
    def _build_prompt(self, jd_text: str) -> str:
        """
        Build the LLM prompt for JD parsing.
        
        Args:
            jd_text: The job description text.
            
        Returns:
            Formatted prompt string.
        """
        return f"""Analyze this Job Description and extract structured requirements.

JOB DESCRIPTION:
{jd_text}

Extract the following information and respond with JSON only:
{{
    "required_skills": ["skill1", "skill2", ...],
    "nice_to_have_skills": ["skill1", "skill2", ...],
    "min_experience_years": <number or null>,
    "job_title_normalized": "string",
    "key_responsibilities": ["responsibility1", "responsibility2", ...]
}}

IMPORTANT INSTRUCTIONS:
1. Extract ALL technical skills mentioned (programming languages, frameworks, databases, tools, cloud platforms)
2. For experience, extract the MINIMUM years required (e.g., "3-5 years" -> 3, "5+ years" -> 5)
3. Clearly separate REQUIRED skills from NICE-TO-HAVE/PREFERRED/BONUS skills
4. Normalize the job title (e.g., "Sr. Python Dev" -> "Senior Python Developer")
5. List key responsibilities (max 5 most important ones)
6. If a field is not mentioned, use null for numbers or empty array for lists

RESPOND WITH VALID JSON ONLY, NO EXPLANATIONS:"""
    
    async def _call_ollama(self, prompt: str) -> str:
        """
        Call Ollama API with a prompt and return the response.
        
        Args:
            prompt: The prompt to send to the LLM.
            
        Returns:
            The LLM response text.
            
        Raises:
            TimeoutError: If the request times out.
            httpx.HTTPError: If the request fails.
        """
        logger.debug(f"Calling Ollama API with prompt ({len(prompt)} chars)")
        
        try:
            async with httpx.AsyncClient(timeout=_LLM_TIMEOUT) as client:
                response = await client.post(
                    f"{self.ollama_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "seed": 42,  # Fixed seed for reproducibility
                            "temperature": 0.1,  # Low temp for consistent extraction
                            "top_p": 0.9,
                            "num_predict": 2048,
                        }
                    }
                )
                response.raise_for_status()
                result = response.json()
                llm_response = result.get("response", "")
                logger.debug(f"Ollama response received ({len(llm_response)} chars)")
                return llm_response
                
        except httpx.TimeoutException:
            logger.error(f"Ollama request timed out after {_LLM_TIMEOUT}s")
            raise TimeoutError("LLM request timed out")
        except httpx.HTTPStatusError as e:
            logger.error(f"Ollama HTTP error: {e.response.status_code}")
            raise
        except Exception as e:
            logger.error(f"Ollama request failed: {e}")
            raise
    
    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        """
        Parse LLM response into structured data.
        
        Attempts JSON parsing first, then falls back to regex extraction
        if JSON parsing fails.
        
        Args:
            response: The raw LLM response text.
            
        Returns:
            Parsed dictionary with extracted fields.
        """
        if not response:
            return {}
        
        # Try to extract JSON from response (LLM might include extra text)
        json_match = re.search(r'\{[\s\S]*\}', response)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError as e:
                logger.warning(f"JSON parse failed: {e}, trying regex fallback")
        
        # Fallback: regex extraction for partial recovery
        return self._regex_fallback_parse(response)
    
    def _regex_fallback_parse(self, response: str) -> Dict[str, Any]:
        """
        Fallback regex-based parsing when JSON parsing fails.
        
        Args:
            response: The raw LLM response text.
            
        Returns:
            Partially extracted dictionary.
        """
        result: Dict[str, Any] = {
            "required_skills": [],
            "nice_to_have_skills": [],
            "min_experience_years": None,
            "job_title_normalized": None,
            "key_responsibilities": [],
        }
        
        # Try to extract skills using patterns
        skills_pattern = r'"required_skills"\s*:\s*\[(.*?)\]'
        skills_match = re.search(skills_pattern, response, re.DOTALL)
        if skills_match:
            skills_str = skills_match.group(1)
            skills = re.findall(r'"([^"]+)"', skills_str)
            result["required_skills"] = skills
        
        nice_pattern = r'"nice_to_have_skills"\s*:\s*\[(.*?)\]'
        nice_match = re.search(nice_pattern, response, re.DOTALL)
        if nice_match:
            nice_str = nice_match.group(1)
            nice_skills = re.findall(r'"([^"]+)"', nice_str)
            result["nice_to_have_skills"] = nice_skills
        
        # Try to extract experience years
        exp_pattern = r'"min_experience_years"\s*:\s*(\d+|null)'
        exp_match = re.search(exp_pattern, response)
        if exp_match:
            exp_val = exp_match.group(1)
            if exp_val != "null":
                try:
                    result["min_experience_years"] = int(exp_val)
                except ValueError:
                    pass
        
        # Try to extract job title
        title_pattern = r'"job_title_normalized"\s*:\s*"([^"]*)"'
        title_match = re.search(title_pattern, response)
        if title_match:
            result["job_title_normalized"] = title_match.group(1)
        
        logger.info(f"Regex fallback extracted: {len(result['required_skills'])} skills")
        return result
    
    def _normalize_skills(self, raw_skills: List[str]) -> List[str]:
        """
        Normalize skills using the skill taxonomy.
        
        For each skill from LLM:
        1. Try to normalize using skill_extractor.normalize_skill()
        2. If recognized, use canonical name
        3. If not recognized, keep as lowercase (for custom requirements)
        
        Args:
            raw_skills: List of raw skill names from LLM.
            
        Returns:
            List of normalized skill names (no duplicates).
        """
        normalized: List[str] = []
        seen: set = set()
        
        for skill in raw_skills:
            if not skill or not skill.strip():
                continue
            
            # Try taxonomy normalization first
            canonical = skill_extractor.normalize_skill(skill)
            
            if canonical:
                # Skill is in taxonomy
                if canonical not in seen:
                    normalized.append(canonical)
                    seen.add(canonical)
            else:
                # Not in taxonomy - keep as lowercase
                clean = skill.strip().lower()
                if clean and clean not in seen:
                    normalized.append(clean)
                    seen.add(clean)
        
        return normalized
    
    def _categorize_skills(self, skills: List[str]) -> Dict[str, List[str]]:
        """
        Categorize skills using the skill taxonomy.
        
        Args:
            skills: List of normalized skill names.
            
        Returns:
            Dict mapping category names to lists of skills.
        """
        categories: Dict[str, List[str]] = {}
        
        for skill in skills:
            category = skill_extractor.get_skill_category(skill)
            if category:
                if category not in categories:
                    categories[category] = []
                categories[category].append(skill)
            else:
                # Uncategorized skills go to "other"
                if "other" not in categories:
                    categories["other"] = []
                categories["other"].append(skill)
        
        return categories


# Module-level instance for convenient access
jd_parser = JDParser()
