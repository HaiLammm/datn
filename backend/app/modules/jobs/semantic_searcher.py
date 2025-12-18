"""
Semantic Searcher - Natural language candidate search.

This module provides a SemanticSearcher class that allows searching for
CV candidates using natural language queries (e.g., "Python developer with AWS experience").

Features:
- Natural language query parsing
- Skill extraction using SkillExtractor
- LLM-enhanced query parsing with fallback
- Hybrid matching: skill-based + keyword-based scoring
- Pagination support
"""

import json
import logging
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

import httpx
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.modules.ai.models import CVAnalysis, AnalysisStatus
from app.modules.ai.skill_extractor import skill_extractor

logger = logging.getLogger(__name__)

# Scoring weights
SKILL_WEIGHT = 70  # 70% of total score from skills
KEYWORD_WEIGHT = 30  # 30% of total score from keyword matching

# Timeout for LLM requests (seconds)
_LLM_TIMEOUT = 60


@dataclass
class ParsedQuery:
    """
    Parsed search query containing extracted search criteria.
    
    Attributes:
        extracted_skills: List of normalized skill names extracted from query.
        experience_keywords: Keywords related to experience (e.g., "5 years", "senior").
        keywords: Additional keywords for matching.
        min_experience: Extracted minimum experience years (if found).
        raw_query: Original query string.
    """
    extracted_skills: List[str] = field(default_factory=list)
    experience_keywords: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    min_experience: Optional[int] = None
    raw_query: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "extracted_skills": self.extracted_skills,
            "experience_keywords": self.experience_keywords,
            "raw_query": self.raw_query,
        }


@dataclass
class SearchResult:
    """
    A candidate search result with relevance score.
    
    Attributes:
        cv_id: CV unique identifier.
        user_id: User ID who owns this CV.
        relevance_score: Relevance score (0-100).
        matched_skills: Skills from query that match CV.
        cv_summary: AI-generated summary of the CV.
        filename: Original filename of the CV.
    """
    cv_id: UUID
    user_id: int
    relevance_score: int
    matched_skills: List[str] = field(default_factory=list)
    cv_summary: Optional[str] = None
    filename: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "cv_id": str(self.cv_id),
            "user_id": self.user_id,
            "relevance_score": self.relevance_score,
            "matched_skills": self.matched_skills,
            "cv_summary": self.cv_summary,
            "filename": self.filename,
        }


class SemanticSearcher:
    """
    Semantic candidate search using natural language queries.
    
    This class parses natural language search queries, extracts skills
    and keywords, then matches against CV data.
    
    Scoring Algorithm:
    - Skill Match Score (70%): matched_skills / total_query_skills * 70
    - Keyword Match Score (30%): keyword matches in CV summary/content
    
    Example:
        >>> searcher = SemanticSearcher()
        >>> results, total = await searcher.search_candidates(
        ...     query="Python developer with AWS experience",
        ...     db=db_session,
        ...     limit=20,
        ...     offset=0,
        ...     min_score=0
        ... )
    """
    
    def __init__(
        self,
        ollama_url: Optional[str] = None,
        model: Optional[str] = None,
    ):
        """
        Initialize SemanticSearcher with optional Ollama configuration.
        
        Args:
            ollama_url: Ollama API URL (default from settings).
            model: LLM model name (default from settings).
        """
        self.ollama_url = ollama_url or settings.OLLAMA_URL
        self.model = model or settings.LLM_MODEL
        logger.info(f"SemanticSearcher initialized with model: {self.model}")
    
    async def search_candidates(
        self,
        query: str,
        db: AsyncSession,
        limit: int = 20,
        offset: int = 0,
        min_score: int = 0,
    ) -> Tuple[List[SearchResult], int]:
        """
        Search candidates using a natural language query.
        
        Args:
            query: Natural language search query.
            db: Database session.
            limit: Maximum number of results to return (default 20, max 100).
            offset: Number of results to skip (for pagination).
            min_score: Minimum relevance score to include (0-100).
            
        Returns:
            Tuple of (list of search results, total count before pagination).
        """
        logger.info(f"Searching candidates with query: '{query}'")
        
        # Step 1: Parse the query to extract skills and keywords
        parsed_query = await self._parse_query(query)
        
        if not parsed_query.extracted_skills and not parsed_query.keywords:
            # No searchable content extracted
            logger.info("No skills or keywords extracted from query")
            return [], 0
        
        # Step 2: Fetch all completed CV analyses
        cv_analyses = await self._get_all_cv_analyses(db)
        
        if not cv_analyses:
            logger.info("No completed CV analyses found")
            return [], 0
        
        # Step 3: Calculate relevance scores for all candidates
        results: List[SearchResult] = []
        
        for analysis in cv_analyses:
            result = self._calculate_relevance(parsed_query, analysis)
            
            if result.relevance_score >= min_score:
                results.append(result)
        
        # Step 4: Sort by relevance score (descending)
        results.sort(key=lambda x: x.relevance_score, reverse=True)
        
        # Get total before pagination
        total = len(results)
        
        # Step 5: Apply pagination
        paginated = results[offset:offset + limit]
        
        logger.info(
            f"Search completed: {total} candidates matched, "
            f"returning {len(paginated)} (offset={offset}, limit={limit})"
        )
        
        return paginated, total
    
    async def _parse_query(self, query: str) -> ParsedQuery:
        """
        Parse a natural language query to extract search criteria.
        
        Uses rule-based extraction first, then optionally enhances with LLM.
        
        Args:
            query: The natural language search query.
            
        Returns:
            ParsedQuery containing extracted skills and keywords.
        """
        logger.debug(f"Parsing query: '{query}'")
        
        # Rule-based extraction (primary method)
        parsed = self._parse_query_rules(query)
        
        # Try LLM enhancement if rules didn't extract much
        if len(parsed.extracted_skills) < 2:
            try:
                llm_parsed = await self._parse_query_with_llm(query)
                # Merge LLM results with rule-based results
                if llm_parsed:
                    parsed = self._merge_parsed_queries(parsed, llm_parsed)
            except Exception as e:
                logger.warning(f"LLM parsing failed, using rule-based only: {e}")
        
        logger.debug(
            f"Query parsed: {len(parsed.extracted_skills)} skills, "
            f"{len(parsed.keywords)} keywords"
        )
        
        return parsed
    
    def _parse_query_rules(self, query: str) -> ParsedQuery:
        """
        Parse query using rule-based extraction.
        
        Extracts:
        - Skills using SkillExtractor
        - Experience patterns (e.g., "3 years", "5+ years", "3 năm")
        - Role keywords (developer, engineer, senior, etc.)
        
        Args:
            query: The search query.
            
        Returns:
            ParsedQuery with extracted data.
        """
        # Extract skills using SkillExtractor
        extracted_skills = skill_extractor.extract_skills_flat(query)
        
        # Extract experience patterns
        experience_keywords: List[str] = []
        min_experience: Optional[int] = None
        
        # Match patterns like "3 years", "5+ years", "3 năm", "5 năm kinh nghiệm"
        exp_patterns = [
            r'(\d+)\+?\s*(?:years?|năm)',
            r'(?:experience|kinh nghiệm)\s*[:\-]?\s*(\d+)\+?\s*(?:years?|năm)?',
            r'(\d+)\+?\s*(?:years?|năm)\s*(?:experience|kinh nghiệm)?',
        ]
        
        for pattern in exp_patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                try:
                    years = int(match.group(1))
                    min_experience = years
                    experience_keywords.append(match.group(0).strip())
                    break
                except (ValueError, IndexError):
                    pass
        
        # Extract role/level keywords
        role_patterns = [
            r'\b(senior|sr\.?|lead|principal|staff)\b',
            r'\b(junior|jr\.?|entry[\-\s]?level)\b',
            r'\b(mid[\-\s]?level|middle)\b',
            r'\b(developer|engineer|programmer|architect|devops)\b',
            r'\b(frontend|front[\-\s]?end|backend|back[\-\s]?end|fullstack|full[\-\s]?stack)\b',
        ]
        
        keywords: List[str] = []
        for pattern in role_patterns:
            matches = re.findall(pattern, query, re.IGNORECASE)
            keywords.extend([m.lower() for m in matches if m])
        
        return ParsedQuery(
            extracted_skills=extracted_skills,
            experience_keywords=experience_keywords,
            keywords=list(set(keywords)),  # Remove duplicates
            min_experience=min_experience,
            raw_query=query,
        )
    
    async def _parse_query_with_llm(self, query: str) -> Optional[ParsedQuery]:
        """
        Parse query using LLM for enhanced extraction.
        
        Args:
            query: The search query.
            
        Returns:
            ParsedQuery or None if LLM fails.
        """
        try:
            prompt = self._build_llm_prompt(query)
            response = await self._call_ollama(prompt)
            
            if not response:
                return None
            
            # Parse LLM response
            return self._parse_llm_response(response, query)
            
        except Exception as e:
            logger.warning(f"LLM query parsing failed: {e}")
            return None
    
    def _build_llm_prompt(self, query: str) -> str:
        """
        Build LLM prompt for query parsing.
        
        Args:
            query: The search query.
            
        Returns:
            Formatted prompt string.
        """
        return f"""Analyze this candidate search query and extract structured requirements.

SEARCH QUERY:
{query}

Extract the following information and respond with JSON only:
{{
    "skills": ["skill1", "skill2", ...],
    "min_experience_years": <number or null>,
    "keywords": ["keyword1", "keyword2", ...]
}}

INSTRUCTIONS:
1. Extract ALL technical skills mentioned (programming languages, frameworks, databases, tools)
2. For experience, extract the minimum years if mentioned (e.g., "3+ years" -> 3)
3. Extract role keywords (senior, developer, engineer, etc.)
4. Support both Vietnamese and English terms

RESPOND WITH VALID JSON ONLY:"""
    
    async def _call_ollama(self, prompt: str) -> str:
        """
        Call Ollama API with a prompt.
        
        Args:
            prompt: The prompt to send to the LLM.
            
        Returns:
            The LLM response text.
            
        Raises:
            TimeoutError: If request times out.
            httpx.HTTPError: If request fails.
        """
        logger.debug(f"Calling Ollama API for query parsing")
        
        try:
            async with httpx.AsyncClient(timeout=_LLM_TIMEOUT) as client:
                response = await client.post(
                    f"{self.ollama_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "seed": 42,
                            "temperature": 0.1,
                            "top_p": 0.9,
                            "num_predict": 512,
                        }
                    }
                )
                response.raise_for_status()
                result = response.json()
                return result.get("response", "")
                
        except httpx.TimeoutException:
            logger.error(f"Ollama request timed out after {_LLM_TIMEOUT}s")
            raise TimeoutError("LLM request timed out")
        except Exception as e:
            logger.error(f"Ollama request failed: {e}")
            raise
    
    def _parse_llm_response(self, response: str, query: str) -> Optional[ParsedQuery]:
        """
        Parse LLM response into ParsedQuery.
        
        Args:
            response: The LLM response text.
            query: Original query for raw_query field.
            
        Returns:
            ParsedQuery or None if parsing fails.
        """
        if not response:
            return None
        
        # Extract JSON from response
        json_match = re.search(r'\{[\s\S]*\}', response)
        if not json_match:
            return None
        
        try:
            data = json.loads(json_match.group())
            
            # Normalize skills
            raw_skills = data.get("skills", [])
            normalized_skills: List[str] = []
            
            for skill in raw_skills:
                if not skill or not skill.strip():
                    continue
                canonical = skill_extractor.normalize_skill(skill)
                if canonical:
                    if canonical not in normalized_skills:
                        normalized_skills.append(canonical)
                else:
                    clean = skill.strip().lower()
                    if clean and clean not in normalized_skills:
                        normalized_skills.append(clean)
            
            return ParsedQuery(
                extracted_skills=normalized_skills,
                experience_keywords=[],
                keywords=data.get("keywords", []),
                min_experience=data.get("min_experience_years"),
                raw_query=query,
            )
            
        except json.JSONDecodeError:
            logger.warning("Failed to parse LLM response as JSON")
            return None
    
    def _merge_parsed_queries(
        self, primary: ParsedQuery, secondary: ParsedQuery
    ) -> ParsedQuery:
        """
        Merge two parsed queries, combining their results.
        
        Args:
            primary: Primary parsed query (from rules).
            secondary: Secondary parsed query (from LLM).
            
        Returns:
            Merged ParsedQuery.
        """
        # Combine skills (no duplicates)
        all_skills = list(primary.extracted_skills)
        for skill in secondary.extracted_skills:
            if skill not in all_skills:
                all_skills.append(skill)
        
        # Combine keywords
        all_keywords = list(primary.keywords)
        for kw in secondary.keywords:
            if kw not in all_keywords:
                all_keywords.append(kw)
        
        # Use experience from primary if available, else secondary
        min_exp = primary.min_experience or secondary.min_experience
        
        return ParsedQuery(
            extracted_skills=all_skills,
            experience_keywords=primary.experience_keywords,
            keywords=all_keywords,
            min_experience=min_exp,
            raw_query=primary.raw_query,
        )
    
    async def _get_all_cv_analyses(
        self, db: AsyncSession
    ) -> List[CVAnalysis]:
        """
        Fetch all completed CV analyses with their CVs.
        
        Only returns analyses with status COMPLETED that have extracted skills.
        
        Args:
            db: Database session.
            
        Returns:
            List of CVAnalysis objects.
        """
        result = await db.execute(
            select(CVAnalysis)
            .options(selectinload(CVAnalysis.cv))
            .where(CVAnalysis.status == AnalysisStatus.COMPLETED.value)
        )
        analyses = list(result.scalars().all())
        
        # Filter to only those with extracted skills
        return [a for a in analyses if a.extracted_skills]
    
    def _calculate_relevance(
        self, parsed_query: ParsedQuery, cv_analysis: CVAnalysis
    ) -> SearchResult:
        """
        Calculate relevance score between query and CV.
        
        Scoring:
        - Skill Match: (matched / total_query_skills) * 70
        - Keyword Match: keyword presence in summary * 30
        
        Args:
            parsed_query: Parsed search query.
            cv_analysis: CV analysis data.
            
        Returns:
            SearchResult with relevance score.
        """
        # Extract CV data
        cv_skills = cv_analysis.extracted_skills or []
        cv_summary = cv_analysis.ai_summary or ""
        
        # Calculate skill match score
        skill_score = self._skill_match_score(
            parsed_query.extracted_skills, cv_skills
        )
        
        # Calculate keyword match score
        keyword_score = self._keyword_match_score(
            parsed_query.keywords + parsed_query.experience_keywords,
            cv_summary
        )
        
        # Total score
        total_score = skill_score + keyword_score
        total_score = max(0, min(100, round(total_score)))
        
        # Find matched skills
        query_skills_lower = [s.lower() for s in parsed_query.extracted_skills]
        cv_skills_lower = [s.lower() for s in cv_skills]
        matched_skills = [
            s for s in query_skills_lower if s in cv_skills_lower
        ]
        
        return SearchResult(
            cv_id=cv_analysis.cv_id,
            user_id=cv_analysis.cv.user_id if cv_analysis.cv else 0,
            relevance_score=total_score,
            matched_skills=matched_skills,
            cv_summary=cv_summary,
            filename=cv_analysis.cv.filename if cv_analysis.cv else None,
        )
    
    def _skill_match_score(
        self, query_skills: List[str], cv_skills: List[str]
    ) -> float:
        """
        Calculate skill match score (0-70 points).
        
        Formula: (matched_skills / total_query_skills) * 70
        If no skills in query, returns 35 (neutral).
        
        Args:
            query_skills: Skills from the search query.
            cv_skills: Skills from the CV.
            
        Returns:
            Skill match score (0-70).
        """
        if not query_skills:
            # No skills in query = neutral score
            return 35.0
        
        # Normalize for comparison
        query_lower = set(s.lower() for s in query_skills)
        cv_lower = set(s.lower() for s in cv_skills)
        
        # Count matches
        matched = len(query_lower & cv_lower)
        
        # Calculate score
        score = (matched / len(query_lower)) * SKILL_WEIGHT
        
        return score
    
    def _keyword_match_score(
        self, keywords: List[str], cv_content: str
    ) -> float:
        """
        Calculate keyword match score (0-30 points).
        
        Checks for presence of keywords in CV summary/content.
        
        Args:
            keywords: Keywords to search for.
            cv_content: CV summary or content text.
            
        Returns:
            Keyword match score (0-30).
        """
        if not keywords or not cv_content:
            return 0.0
        
        cv_lower = cv_content.lower()
        matched = 0
        
        for keyword in keywords:
            if keyword.lower() in cv_lower:
                matched += 1
        
        if not keywords:
            return 0.0
        
        # Calculate score based on keyword matches
        score = (matched / len(keywords)) * KEYWORD_WEIGHT
        
        return score


# Module-level instance for convenient access
semantic_searcher = SemanticSearcher()
