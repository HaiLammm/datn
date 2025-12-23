"""
Hybrid Skill Scorer - Combines rule-based and LLM analysis for skill scoring.

This module provides a SkillScorer class that calculates skill scores
based on extracted skills from CV text. It combines deterministic
rule-based scoring with LLM-based evidence scoring.

Score Breakdown (Total: 0-25):
- Completeness (0-7): Based on quantity and diversity of skills
- Categorization (0-6): Based on coverage across skill categories
- Evidence (0-6): Extracted from LLM analysis (skill usage in experience)
- Market Relevance (0-6): Based on presence of hot/in-demand skills
"""

import logging
from typing import Any, Dict, List, Optional, TypedDict

from .skill_extractor import SkillExtractor
from .skill_taxonomy import HOT_SKILLS_2024, HOT_SKILLS_VERSIONS, is_hot_skill, is_hot_skill_versioned


logger = logging.getLogger(__name__)


class SkillScoreResult(TypedDict):
    """Type definition for skill score calculation result."""
    completeness_score: int  # 0-7
    categorization_score: int  # 0-6
    evidence_score: int  # 0-6
    market_relevance_score: int  # 0-6
    total_score: int  # 0-25
    skill_categories: Dict[str, List[str]]
    recommendations: List[str]


class SkillMatchResult(TypedDict):
    """Type definition for skill matching result."""
    matched_skills: Dict[str, List[str]]  # skills in both CV and JD
    missing_skills: Dict[str, List[str]]  # JD requirements not in CV
    extra_skills: Dict[str, List[str]]  # CV skills not in JD
    skill_match_rate: float  # 0.0 to 1.0
    jd_requirements: Dict[str, List[str]]  # all JD skills
    cv_skills: Dict[str, List[str]]  # all CV skills


# Main categories to evaluate for categorization score
MAIN_CATEGORIES = [
    "programming_languages",
    "frameworks",
    "databases",
    "devops",
    "infrastructure",
    "networking",
    "compliance",
    "soft_skills",
    "ai_ml",
]


class SkillScorer:
    """
    Hybrid skill scorer combining rule-based and LLM analysis.

    This class calculates skill scores based on extracted skills from CV text.
    It uses a singleton pattern to avoid rebuilding dependencies on each
    instantiation.

    Attributes:
        _extractor: SkillExtractor instance for extracting skills from text.

    Example:
        >>> scorer = SkillScorer()
        >>> result = scorer.calculate_skill_score("Python developer with React experience")
        >>> print(result["total_score"])
        15
    """

    _instance: Optional["SkillScorer"] = None

    def __new__(cls) -> "SkillScorer":
        """Create or return singleton instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self) -> None:
        """Initialize dependencies."""
        logger.debug("Initializing SkillScorer...")
        self._extractor = SkillExtractor()
        logger.debug("SkillScorer initialized successfully")

    def calculate_skill_score(
        self,
        cv_text: str,
        llm_response: Optional[Dict[str, Any]] = None
    ) -> SkillScoreResult:
        """
        Calculate comprehensive skill score from CV text.

        This method extracts skills from the CV text, calculates rule-based
        scores (deterministic), and extracts evidence score from LLM response.

        Args:
            cv_text: Raw text content from CV.
            llm_response: Optional LLM analysis response containing criteria.

        Returns:
            SkillScoreResult with all sub-scores, total, categories, and recommendations.

        Example:
            >>> scorer = SkillScorer()
            >>> result = scorer.calculate_skill_score(
            ...     "Python developer with React and PostgreSQL experience",
            ...     llm_response={"criteria": {"skills": 75}}
            ... )
            >>> result["total_score"]
            18
        """
        logger.debug(f"Calculating skill score for text of length {
                     len(cv_text)}")

        # Extract LLM skills for "other" category support
        llm_skills: Optional[List[str]] = None
        if llm_response and "skills" in llm_response:
            llm_skills = llm_response.get("skills", [])
            if isinstance(llm_skills, list):
                logger.debug(f"LLM provided {len(llm_skills)} skills for matching")

        # 1. Extract skills using SkillExtractor with "other" category support
        extracted_skills = self._extractor.extract_skills_with_other(
            cv_text, 
            llm_skills=llm_skills
        )
        logger.debug(f"Extracted skills: {extracted_skills}")

        # 2. Calculate rule-based scores (deterministic)
        completeness_score = self._calculate_completeness(extracted_skills)
        categorization_score = self._calculate_categorization(extracted_skills)
        market_relevance_score = self._calculate_market_relevance(
            extracted_skills)

        # 3. Extract evidence score from LLM (or default)
        evidence_score = self.extract_evidence_score(llm_response)

        # 4. Calculate total score
        total_score = (
            completeness_score +
            categorization_score +
            evidence_score +
            market_relevance_score
        )

        # 5. Generate recommendations
        scores = {
            "completeness_score": completeness_score,
            "categorization_score": categorization_score,
            "evidence_score": evidence_score,
            "market_relevance_score": market_relevance_score,
        }
        recommendations = self._generate_recommendations(
            extracted_skills, scores)

        result: SkillScoreResult = {
            "completeness_score": completeness_score,
            "categorization_score": categorization_score,
            "evidence_score": evidence_score,
            "market_relevance_score": market_relevance_score,
            "total_score": total_score,
            "skill_categories": extracted_skills,
            "recommendations": recommendations,
        }

        logger.info(
            f"Skill score calculated: total={total_score}, "
            f"completeness={completeness_score}, categorization={
                categorization_score}, "
            f"evidence={evidence_score}, market_relevance={
                market_relevance_score}"
        )

        return result

    def _calculate_completeness(
        self,
        extracted_skills: Dict[str, List[str]]
    ) -> int:
        """
        Calculate completeness score based on quantity and diversity of skills.

        Scoring logic (0-7 points):
        - 0 points: 0 skills found
        - 1 point: 1-2 skills found
        - 2 points: 3-4 skills found
        - 3 points: 5 skills found
        - 4 points: 6-8 skills found
        - 5 points: 9-10 skills found
        - 6 points: 11-15 skills found
        - 7 points: 16+ skills with diversity across 3+ categories

        Args:
            extracted_skills: Dict mapping categories to lists of skill names.

        Returns:
            Integer score from 0 to 7.
        """
        # Count total unique skills
        total_skills = sum(len(skills) for skills in extracted_skills.values())

        # Count categories with at least one skill
        categories_with_skills = sum(
            1 for skills in extracted_skills.values() if len(skills) > 0
        )

        logger.debug(
            f"Completeness calc: total_skills={total_skills}, "
            f"categories_with_skills={categories_with_skills}"
        )

        # Calculate base score based on skill count
        if total_skills == 0:
            score = 0
        elif total_skills <= 2:
            score = 1
        elif total_skills <= 4:
            score = 2
        elif total_skills == 5:
            score = 3
        elif total_skills <= 8:
            score = 4
        elif total_skills <= 10:
            score = 5
        elif total_skills <= 15:
            score = 6
        else:
            # 16+ skills - check for diversity bonus
            if categories_with_skills >= 3:
                score = 7
            else:
                score = 6

        logger.debug(f"Completeness score: {score}")
        return score

    def _calculate_categorization(
        self,
        extracted_skills: Dict[str, List[str]]
    ) -> int:
        """
        Calculate categorization score based on coverage across skill categories.

        Scoring logic (0-6 points):
        - 1 point per main category with at least 1 skill (max 5)
        - 1 bonus point for balanced distribution (no category > 50% of total)

        Args:
            extracted_skills: Dict mapping categories to lists of skill names.

        Returns:
            Integer score from 0 to 6.
        """
        # Count main categories with at least one skill
        categories_covered = 0
        for category in MAIN_CATEGORIES:
            if category in extracted_skills and len(extracted_skills[category]) > 0:
                categories_covered += 1

        # Calculate total skills for balance check
        total_skills = sum(len(skills) for skills in extracted_skills.values())

        # Check for balanced distribution
        is_balanced = True
        if total_skills > 0:
            for skills in extracted_skills.values():
                if len(skills) > total_skills * 0.5:
                    is_balanced = False
                    break

        # Calculate score
        score = categories_covered  # 0-5 points for category coverage

        # Add bonus for balance (only if at least 2 categories covered)
        if is_balanced and categories_covered >= 2:
            score += 1

        # Cap at 6
        score = min(6, score)

        logger.debug(
            f"Categorization calc: categories_covered={categories_covered}, "
            f"is_balanced={is_balanced}, score={score}"
        )

        return score

    def _calculate_market_relevance(
        self,
        extracted_skills: Dict[str, List[str]],
        years: List[int] | None = None
    ) -> int:
        """
        Calculate market relevance score based on presence of hot/in-demand skills.

        Uses additive logic: a skill is considered "hot" if it appears in ANY
        of the checked years' lists.

        Scoring logic (0-6 points):
        - 1 point per hot skill found (max 6)

        Args:
            extracted_skills: Dict mapping categories to lists of skill names.
            years: List of years to check hot skills against. If None, checks
                   all available years in HOT_SKILLS_VERSIONS.

        Returns:
            Integer score from 0 to 6.
        """
        # Flatten all skills
        all_skills: List[str] = []
        for skills in extracted_skills.values():
            all_skills.extend(skills)

        # Count hot skills using versioned check
        hot_skills_found = 0
        found_hot_skills: List[str] = []

        for skill in all_skills:
            if is_hot_skill_versioned(skill, years):
                hot_skills_found += 1
                found_hot_skills.append(skill)

        # Cap at 6
        score = min(6, hot_skills_found)

        years_checked = years if years else list(HOT_SKILLS_VERSIONS.keys())
        logger.debug(
            f"Market relevance calc: hot_skills_found={hot_skills_found}, "
            f"found={found_hot_skills}, years={years_checked}, score={score}"
        )

        return score

    def extract_evidence_score(
        self,
        llm_response: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Extract evidence score from LLM response.

        The evidence score represents how well skills are demonstrated
        in the CV's experience section, as evaluated by the LLM.

        Args:
            llm_response: Optional LLM analysis response containing criteria.
                         Expected format: {"criteria": {"skills": 0-100}}

        Returns:
            Integer score from 0 to 6.
            Returns 3 (middle score) if LLM response is missing or invalid.
        """
        if not llm_response:
            logger.debug(
                "No LLM response provided, using default evidence score of 3")
            return 3

        try:
            # Get skills score from LLM criteria (0-100)
            criteria = llm_response.get("criteria", {})
            if not isinstance(criteria, dict):
                logger.debug(
                    "Invalid criteria format, using default evidence score of 3")
                return 3

            llm_skills_score = criteria.get("skills", 50)

            # Handle non-numeric values
            if not isinstance(llm_skills_score, (int, float)):
                logger.debug(f"Invalid skills score type: {
                             type(llm_skills_score)}")
                return 3

            # Normalize to 0-6 range
            evidence_score = round(float(llm_skills_score) * 6 / 100)
            evidence_score = min(6, max(0, evidence_score))

            logger.debug(
                f"Evidence score extracted: llm_skills={llm_skills_score}, "
                f"normalized={evidence_score}"
            )

            return evidence_score

        except Exception as e:
            logger.warning(f"Error extracting evidence score: {
                           e}, using default of 3")
            return 3

    def _generate_recommendations(
        self,
        extracted_skills: Dict[str, List[str]],
        scores: Dict[str, int]
    ) -> List[str]:
        """
        Generate recommendations based on skill gaps and scores.

        Recommendation rules:
        - If completeness_score < 4: Add more technical skills
        - If no hot skills found: Learn in-demand skills
        - If missing category: Add skills in missing category
        - If evidence_score < 3: Provide more concrete examples
        - If categorization unbalanced: Balance skills across areas

        Args:
            extracted_skills: Dict mapping categories to lists of skill names.
            scores: Dict containing all sub-scores.

        Returns:
            List of 1-5 relevant recommendations, most important first.
        """
        recommendations: List[str] = []

        # Flatten skills for hot skill check
        all_skills: List[str] = []
        for skills in extracted_skills.values():
            all_skills.extend(skills)

        # Check completeness
        if scores.get("completeness_score", 0) < 4:
            recommendations.append(
                "Consider adding more technical skills to your CV to demonstrate "
                "broader expertise."
            )

        # Check for hot skills
        hot_skills_count = sum(
            1 for skill in all_skills if is_hot_skill(skill))
        if hot_skills_count == 0:
            # Get some example hot skills
            example_hot_skills = []
            for category, skills in HOT_SKILLS_2024.items():
                example_hot_skills.extend(skills[:2])
            example_str = ", ".join(example_hot_skills[:5])
            recommendations.append(
                f"Consider learning in-demand skills like {
                    example_str} to improve "
                f"market relevance."
            )

        # Check for missing main categories
        missing_categories: List[str] = []
        for category in MAIN_CATEGORIES:
            if category not in extracted_skills or len(extracted_skills[category]) == 0:
                # Format category name for display
                display_name = category.replace("_", " ").title()
                missing_categories.append(display_name)

        if missing_categories and len(missing_categories) <= 3:
            missing_str = ", ".join(missing_categories[:2])
            recommendations.append(
                f"Add skills in {
                    missing_str} to show broader technical expertise."
            )

        # Check evidence score
        if scores.get("evidence_score", 3) < 3:
            recommendations.append(
                "Provide more concrete examples of skill usage in your work "
                "experience section."
            )

        # Check categorization balance
        total_skills = len(all_skills)
        if total_skills > 0:
            for skills in extracted_skills.values():
                if len(skills) > total_skills * 0.5:
                    recommendations.append(
                        "Balance your skills across different technical areas "
                        "for a more well-rounded profile."
                    )
                    break

        # Limit to 5 recommendations
        return recommendations[:5]


class SkillMatcher:
    """
    Skill matching utility for comparing CV skills with JD requirements.
    
    This class provides functionality to match candidate skills against
    job description requirements, calculating match rates and identifying
    skill gaps. It uses SkillExtractor for parsing JD text.
    
    Attributes:
        _extractor: SkillExtractor instance for parsing JD requirements.
        
    Example:
        >>> matcher = SkillMatcher()
        >>> cv_skills = {"programming_languages": ["python", "javascript"]}
        >>> jd_text = "Looking for Python developer with React experience"
        >>> result = matcher.match_skills(cv_skills, jd_text)
        >>> print(result["skill_match_rate"])
        0.5
    """
    
    def __init__(self) -> None:
        """Initialize SkillMatcher with SkillExtractor dependency."""
        logger.debug("Initializing SkillMatcher...")
        self._extractor = SkillExtractor()
        logger.debug("SkillMatcher initialized successfully")
    
    def match_skills(
        self,
        cv_skills: Dict[str, List[str]],
        jd_text: str
    ) -> SkillMatchResult:
        """
        Match CV skills against JD requirements.
        
        Extracts skills from JD text, normalizes both CV and JD skills,
        then calculates matched, missing, and extra skills by category.
        
        Args:
            cv_skills: Categorized CV skills (Dict[category, List[skill_names]]).
            jd_text: Job description text to extract requirements from.
            
        Returns:
            SkillMatchResult containing:
                - matched_skills: Skills present in both CV and JD
                - missing_skills: JD requirements not in CV (skill gaps)
                - extra_skills: CV skills not required by JD
                - skill_match_rate: Percentage of JD requirements met (0.0-1.0)
                - jd_requirements: All skills extracted from JD
                - cv_skills: All skills from CV (as provided)
                
        Example:
            >>> matcher = SkillMatcher()
            >>> cv_skills = {
            ...     "programming_languages": ["python", "java"],
            ...     "frameworks": ["django"]
            ... }
            >>> jd_text = "Python developer with Django and React"
            >>> result = matcher.match_skills(cv_skills, jd_text)
            >>> result["skill_match_rate"]
            0.67  # 2 out of 3 JD requirements matched
        """
        logger.info(f"Starting skill match: CV has {sum(len(s) for s in cv_skills.values())} skills, "
                    f"JD text length: {len(jd_text)} chars")
        
        # 1. Extract skills from JD text
        jd_requirements = self._extractor.extract_skills(jd_text)
        logger.debug(f"Extracted JD requirements: {jd_requirements}")
        
        # 2. Initialize result structures (maintain category organization)
        matched_skills: Dict[str, List[str]] = {}
        missing_skills: Dict[str, List[str]] = {}
        extra_skills: Dict[str, List[str]] = {}
        
        # 3. Process each category
        for category in jd_requirements.keys():
            # Convert to sets for set operations
            cv_set = set(cv_skills.get(category, []))
            jd_set = set(jd_requirements.get(category, []))
            
            # Calculate matches, missing, and extras
            matched = cv_set & jd_set  # intersection
            missing = jd_set - cv_set  # in JD but not in CV
            extra = cv_set - jd_set    # in CV but not in JD
            
            # Store as sorted lists (only if non-empty)
            if matched:
                matched_skills[category] = sorted(list(matched))
            if missing:
                missing_skills[category] = sorted(list(missing))
            if extra:
                extra_skills[category] = sorted(list(extra))
            
            logger.debug(
                f"Category '{category}': matched={len(matched)}, "
                f"missing={len(missing)}, extra={len(extra)}"
            )
        
        # 4. Calculate skill match rate
        total_jd_requirements = sum(len(skills) for skills in jd_requirements.values())
        total_matched = sum(len(skills) for skills in matched_skills.values())
        
        if total_jd_requirements > 0:
            skill_match_rate = total_matched / total_jd_requirements
        else:
            skill_match_rate = 0.0
        
        logger.info(
            f"Match complete: rate={skill_match_rate:.2%}, "
            f"matched={total_matched}/{total_jd_requirements}, "
            f"missing={sum(len(s) for s in missing_skills.values())}, "
            f"extra={sum(len(s) for s in extra_skills.values())}"
        )
        
        # 5. Build and return result
        result: SkillMatchResult = {
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "extra_skills": extra_skills,
            "skill_match_rate": round(skill_match_rate, 4),  # Round to 4 decimal places
            "jd_requirements": jd_requirements,
            "cv_skills": cv_skills,
        }
        
        return result


# Create singleton instance for easy import
skill_scorer = SkillScorer()
