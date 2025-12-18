"""
Candidate Ranker - AI-powered candidate ranking based on JD requirements.

This module provides a CandidateRanker class that matches CV candidates
against job description requirements and calculates match scores.

Features:
- Skill matching with required vs nice-to-have weighting
- Experience years matching
- Match breakdown with matched/missing/extra skills
- Pagination support
"""

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.ai.models import CVAnalysis, AnalysisStatus
from app.modules.cv.models import CV
from app.modules.jobs.models import JobDescription
from app.modules.jobs.schemas import JDParseStatus

logger = logging.getLogger(__name__)

# Scoring weights
SKILL_WEIGHT = 70  # 70% of total score from skills
EXPERIENCE_WEIGHT = 30  # 30% of total score from experience
REQUIRED_SKILL_WEIGHT = 60  # Within skill score, required skills worth 60%
NICE_TO_HAVE_WEIGHT = 10  # Within skill score, nice-to-have worth 10%


@dataclass
class MatchBreakdown:
    """Detailed breakdown of match between CV and JD."""
    
    matched_skills: List[str] = field(default_factory=list)
    missing_skills: List[str] = field(default_factory=list)
    extra_skills: List[str] = field(default_factory=list)
    skill_score: float = 0.0
    experience_score: float = 0.0
    experience_years: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "matched_skills": self.matched_skills,
            "missing_skills": self.missing_skills,
            "extra_skills": self.extra_skills,
            "skill_score": round(self.skill_score, 1),
            "experience_score": round(self.experience_score, 1),
            "experience_years": self.experience_years,
        }


@dataclass
class RankedCandidate:
    """A candidate with match score and breakdown."""
    
    cv_id: UUID
    user_id: int
    match_score: int
    breakdown: MatchBreakdown
    cv_summary: Optional[str] = None
    filename: Optional[str] = None
    is_public: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "cv_id": str(self.cv_id),
            "user_id": self.user_id,
            "match_score": self.match_score,
            "breakdown": self.breakdown.to_dict(),
            "cv_summary": self.cv_summary,
            "filename": self.filename,
            "is_public": self.is_public,
        }


class CandidateRanker:
    """
    Ranks CV candidates against Job Description requirements.
    
    This class calculates match scores based on:
    - Skill overlap (required skills: 60%, nice-to-have: 10%)
    - Experience years (30% of total score)
    
    Example:
        >>> ranker = CandidateRanker()
        >>> candidates = await ranker.rank_candidates(
        ...     db=db_session,
        ...     jd_id=uuid,
        ...     limit=20,
        ...     offset=0,
        ...     min_score=50
        ... )
    """
    
    async def rank_candidates(
        self,
        db: AsyncSession,
        jd_id: UUID,
        limit: int = 20,
        offset: int = 0,
        min_score: int = 0,
    ) -> tuple[List[RankedCandidate], int]:
        """
        Rank all available candidates against a job description.
        
        Args:
            db: Database session.
            jd_id: Job description ID.
            limit: Maximum number of candidates to return.
            offset: Number of candidates to skip (for pagination).
            min_score: Minimum match score to include (0-100).
            
        Returns:
            Tuple of (list of ranked candidates, total count before pagination).
            
        Raises:
            ValueError: If JD not found or parsing not complete.
        """
        logger.info(f"Ranking candidates for JD {jd_id}")
        
        # Step 1: Fetch and validate JD
        jd = await self._get_jd(db, jd_id)
        if jd is None:
            raise ValueError(f"Job description {jd_id} not found")
        
        if jd.parse_status != JDParseStatus.COMPLETED.value:
            raise ValueError(f"JD parsing not complete (status: {jd.parse_status})")
        
        if not jd.parsed_requirements:
            raise ValueError("JD has no parsed requirements")
        
        # Step 2: Fetch all completed CV analyses
        cv_analyses = await self._get_all_cv_analyses(db)
        
        if not cv_analyses:
            logger.info("No completed CV analyses found")
            return [], 0
        
        # Step 3: Calculate match scores for all candidates
        ranked: List[RankedCandidate] = []
        
        for analysis in cv_analyses:
            match_result = self._calculate_match(jd.parsed_requirements, analysis)
            
            if match_result.match_score >= min_score:
                ranked.append(match_result)
        
        # Step 4: Sort by match score (descending)
        ranked.sort(key=lambda x: x.match_score, reverse=True)
        
        # Get total before pagination
        total = len(ranked)
        
        # Step 5: Apply pagination
        paginated = ranked[offset:offset + limit]
        
        logger.info(
            f"Ranked {total} candidates for JD {jd_id}, "
            f"returning {len(paginated)} (offset={offset}, limit={limit})"
        )
        
        return paginated, total
    
    async def _get_jd(
        self, db: AsyncSession, jd_id: UUID
    ) -> Optional[JobDescription]:
        """Fetch job description by ID."""
        result = await db.execute(
            select(JobDescription).where(JobDescription.id == jd_id)
        )
        return result.scalars().first()
    
    async def _get_all_cv_analyses(
        self, db: AsyncSession
    ) -> List[CVAnalysis]:
        """
        Fetch all completed CV analyses with their CVs.
        
        Only returns analyses with:
        - status COMPLETED
        - extracted skills present
        - CV is active (not soft-deleted)
        """
        result = await db.execute(
            select(CVAnalysis)
            .join(CV, CVAnalysis.cv_id == CV.id)
            .options(selectinload(CVAnalysis.cv))
            .where(
                CVAnalysis.status == AnalysisStatus.COMPLETED.value,
                CV.is_active == True,  # Exclude soft-deleted CVs
            )
        )
        analyses = list(result.scalars().all())
        
        # Filter to only those with extracted skills
        return [a for a in analyses if a.extracted_skills]
    
    def _calculate_match(
        self,
        jd_requirements: Dict[str, Any],
        cv_analysis: CVAnalysis,
    ) -> RankedCandidate:
        """
        Calculate match score between JD requirements and CV analysis.
        
        Args:
            jd_requirements: Parsed JD requirements dict.
            cv_analysis: CV analysis with extracted skills.
            
        Returns:
            RankedCandidate with score and breakdown.
        """
        # Extract JD data
        required_skills = jd_requirements.get("required_skills", [])
        nice_to_have = jd_requirements.get("nice_to_have_skills", [])
        required_years = jd_requirements.get("min_experience_years")
        
        # Extract CV data
        cv_skills = cv_analysis.extracted_skills or []
        cv_skill_categories = cv_analysis.skill_categories or {}
        
        # Flatten CV skills from categories if needed
        if not cv_skills and cv_skill_categories:
            cv_skills = []
            for skills in cv_skill_categories.values():
                if isinstance(skills, list):
                    cv_skills.extend(skills)
        
        # Normalize all skills to lowercase for comparison
        required_skills_lower = [s.lower() for s in required_skills]
        nice_to_have_lower = [s.lower() for s in nice_to_have]
        cv_skills_lower = [s.lower() for s in cv_skills]
        
        # Calculate skill match
        skill_result = self._calculate_skill_score(
            required_skills_lower,
            nice_to_have_lower,
            cv_skills_lower,
        )
        
        # Calculate experience match
        # Try to extract years from CV analysis (if available in breakdown)
        cv_years = self._extract_experience_years(cv_analysis)
        experience_score = self._calculate_experience_score(required_years, cv_years)
        
        # Total score
        total_score = skill_result["skill_score"] + experience_score
        total_score = max(0, min(100, round(total_score)))  # Clamp to 0-100
        
        # Build breakdown
        breakdown = MatchBreakdown(
            matched_skills=skill_result["matched_skills"],
            missing_skills=skill_result["missing_skills"],
            extra_skills=skill_result["extra_skills"],
            skill_score=skill_result["skill_score"],
            experience_score=experience_score,
            experience_years=cv_years,
        )
        
        return RankedCandidate(
            cv_id=cv_analysis.cv_id,
            user_id=cv_analysis.cv.user_id if cv_analysis.cv else 0,
            match_score=total_score,
            breakdown=breakdown,
            cv_summary=cv_analysis.ai_summary,
            filename=cv_analysis.cv.filename if cv_analysis.cv else None,
            is_public=cv_analysis.cv.is_public if cv_analysis.cv else False,
        )
    
    def _calculate_skill_score(
        self,
        required_skills: List[str],
        nice_to_have: List[str],
        cv_skills: List[str],
    ) -> Dict[str, Any]:
        """
        Calculate skill match score.
        
        Score breakdown:
        - Required skills: Up to 60 points (REQUIRED_SKILL_WEIGHT)
        - Nice-to-have skills: Up to 10 points (NICE_TO_HAVE_WEIGHT)
        
        Args:
            required_skills: List of required skill names (lowercase).
            nice_to_have: List of nice-to-have skill names (lowercase).
            cv_skills: List of CV skill names (lowercase).
            
        Returns:
            Dict with matched_skills, missing_skills, extra_skills, skill_score.
        """
        cv_skills_set = set(cv_skills)
        required_set = set(required_skills)
        nice_set = set(nice_to_have)
        
        # Find matched and missing skills
        matched_required = required_set & cv_skills_set
        matched_nice = nice_set & cv_skills_set
        missing_skills = list(required_set - cv_skills_set)
        
        # All matched skills
        matched_skills = list(matched_required | matched_nice)
        
        # Extra skills (not in JD requirements)
        all_jd_skills = required_set | nice_set
        extra_skills = list(cv_skills_set - all_jd_skills)
        
        # Calculate scores
        if required_set:
            required_score = (len(matched_required) / len(required_set)) * REQUIRED_SKILL_WEIGHT
        else:
            # No required skills means full required score
            required_score = REQUIRED_SKILL_WEIGHT
        
        if nice_set:
            nice_score = (len(matched_nice) / len(nice_set)) * NICE_TO_HAVE_WEIGHT
        else:
            nice_score = 0
        
        total_skill_score = required_score + nice_score
        
        return {
            "matched_skills": sorted(matched_skills),
            "missing_skills": sorted(missing_skills),
            "extra_skills": sorted(extra_skills),
            "skill_score": total_skill_score,
        }
    
    def _calculate_experience_score(
        self,
        required_years: Optional[int],
        cv_years: Optional[int],
    ) -> float:
        """
        Calculate experience match score.
        
        - If no requirement: Full experience score
        - If meets or exceeds: Full experience score
        - If below: Proportional score
        
        Args:
            required_years: Minimum years required (from JD).
            cv_years: Years of experience (from CV).
            
        Returns:
            Experience score (0 to EXPERIENCE_WEIGHT).
        """
        # No requirement means full score
        if required_years is None or required_years == 0:
            return float(EXPERIENCE_WEIGHT)
        
        # No CV years info means 0 score
        if cv_years is None:
            return 0.0
        
        # Calculate proportional score
        ratio = min(cv_years / required_years, 1.0)  # Cap at 1.0
        return ratio * EXPERIENCE_WEIGHT
    
    def _extract_experience_years(self, cv_analysis: CVAnalysis) -> Optional[int]:
        """
        Extract years of experience from CV analysis.
        
        Tries to find experience info from:
        1. skill_breakdown field
        2. ai_feedback field
        
        Returns None if not available.
        """
        # Try skill_breakdown
        if cv_analysis.skill_breakdown:
            years = cv_analysis.skill_breakdown.get("experience_years")
            if years is not None:
                try:
                    return int(years)
                except (ValueError, TypeError):
                    pass
        
        # Try ai_feedback
        if cv_analysis.ai_feedback:
            years = cv_analysis.ai_feedback.get("experience_years")
            if years is not None:
                try:
                    return int(years)
                except (ValueError, TypeError):
                    pass
        
        return None


# Module-level instance for convenient access
candidate_ranker = CandidateRanker()
