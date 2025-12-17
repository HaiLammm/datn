"""
Unit tests for SkillScorer - Hybrid skill scoring engine.

Tests cover:
- Completeness score calculation
- Categorization score calculation
- Market relevance score calculation
- Evidence score extraction from LLM response
- Main calculate_skill_score method
- Recommendations generation
- Deterministic behavior verification
"""

import pytest
from typing import Dict, List

from app.modules.ai.skill_scorer import SkillScorer, SkillScoreResult


@pytest.fixture
def scorer():
    """Reset singleton and return fresh SkillScorer instance."""
    SkillScorer._instance = None
    return SkillScorer()


# =============================================================================
# Completeness Score Tests
# =============================================================================

class TestCalculateCompleteness:
    """Tests for _calculate_completeness method."""
    
    def test_completeness_zero_skills_returns_zero(self, scorer):
        """Empty skills should return 0."""
        result = scorer._calculate_completeness({})
        assert result == 0
    
    def test_completeness_empty_categories_returns_zero(self, scorer):
        """Categories with empty lists should return 0."""
        result = scorer._calculate_completeness({
            "programming_languages": [],
            "frameworks": [],
        })
        assert result == 0
    
    def test_completeness_one_skill_returns_one(self, scorer):
        """1 skill should return 1 point."""
        result = scorer._calculate_completeness({
            "programming_languages": ["python"],
        })
        assert result == 1
    
    def test_completeness_two_skills_returns_one(self, scorer):
        """2 skills should return 1 point."""
        result = scorer._calculate_completeness({
            "programming_languages": ["python", "javascript"],
        })
        assert result == 1
    
    def test_completeness_three_to_four_skills_returns_two(self, scorer):
        """3-4 skills should return 2 points."""
        result = scorer._calculate_completeness({
            "programming_languages": ["python", "javascript", "typescript"],
        })
        assert result == 2
        
        result = scorer._calculate_completeness({
            "programming_languages": ["python", "javascript", "typescript", "java"],
        })
        assert result == 2
    
    def test_completeness_five_skills_returns_three(self, scorer):
        """5 skills should return 3 points."""
        result = scorer._calculate_completeness({
            "programming_languages": ["python", "javascript", "typescript"],
            "frameworks": ["react", "fastapi"],
        })
        assert result == 3
    
    def test_completeness_six_to_eight_skills_returns_four(self, scorer):
        """6-8 skills should return 4 points."""
        result = scorer._calculate_completeness({
            "programming_languages": ["python", "javascript", "typescript"],
            "frameworks": ["react", "fastapi", "nextjs"],
        })
        assert result == 4
    
    def test_completeness_nine_to_ten_skills_returns_five(self, scorer):
        """9-10 skills should return 5 points."""
        result = scorer._calculate_completeness({
            "programming_languages": ["python", "javascript", "typescript"],
            "frameworks": ["react", "fastapi", "nextjs"],
            "databases": ["postgresql", "mongodb", "redis"],
        })
        assert result == 5
    
    def test_completeness_eleven_to_fifteen_skills_returns_six(self, scorer):
        """11-15 skills should return 6 points."""
        result = scorer._calculate_completeness({
            "programming_languages": ["python", "javascript", "typescript", "java"],
            "frameworks": ["react", "fastapi", "nextjs", "django"],
            "databases": ["postgresql", "mongodb", "redis"],
        })
        assert result == 6
    
    def test_completeness_many_skills_with_diversity_returns_seven(self, scorer):
        """16+ skills with 3+ categories should return 7 points."""
        result = scorer._calculate_completeness({
            "programming_languages": ["python", "javascript", "typescript", "java", "go"],
            "frameworks": ["react", "fastapi", "nextjs", "django", "flask"],
            "databases": ["postgresql", "mongodb", "redis", "mysql"],
            "devops": ["docker", "kubernetes"],
        })
        assert result == 7
    
    def test_completeness_many_skills_without_diversity_returns_six(self, scorer):
        """16+ skills without 3+ categories should return 6 points."""
        result = scorer._calculate_completeness({
            "programming_languages": [
                "python", "javascript", "typescript", "java", "go",
                "rust", "ruby", "php", "scala", "kotlin",
                "swift", "dart", "perl", "r", "shell", "sql"
            ],
        })
        # Only 1 category, should be 6 not 7
        assert result == 6


# =============================================================================
# Categorization Score Tests
# =============================================================================

class TestCalculateCategorization:
    """Tests for _calculate_categorization method."""
    
    def test_categorization_empty_returns_zero(self, scorer):
        """Empty skills should return 0."""
        result = scorer._calculate_categorization({})
        assert result == 0
    
    def test_categorization_single_category(self, scorer):
        """Single category should return 1 point (no balance bonus)."""
        result = scorer._calculate_categorization({
            "programming_languages": ["python", "javascript"],
        })
        assert result == 1
    
    def test_categorization_two_categories_balanced(self, scorer):
        """Two balanced categories should return 3 points (2 + 1 bonus)."""
        result = scorer._calculate_categorization({
            "programming_languages": ["python", "javascript"],
            "frameworks": ["react", "fastapi"],
        })
        assert result == 3
    
    def test_categorization_two_categories_unbalanced(self, scorer):
        """Two unbalanced categories should return 2 points (no bonus)."""
        result = scorer._calculate_categorization({
            "programming_languages": ["python", "javascript", "typescript", "java", "go"],
            "frameworks": ["react"],
        })
        # 5 vs 1, unbalanced (83% > 50%)
        assert result == 2
    
    def test_categorization_all_main_categories(self, scorer):
        """All 5 main categories balanced should return 6 points."""
        result = scorer._calculate_categorization({
            "programming_languages": ["python"],
            "frameworks": ["react"],
            "databases": ["postgresql"],
            "devops": ["docker"],
            "soft_skills": ["communication"],
        })
        assert result == 6  # 5 categories + 1 balance bonus
    
    def test_categorization_ignores_non_main_categories(self, scorer):
        """Non-main categories (other) should not count toward score."""
        result = scorer._calculate_categorization({
            "other": ["custom skill 1", "custom skill 2", "custom skill 3"],
        })
        # 'other' is not in MAIN_CATEGORIES
        assert result == 0
    
    def test_categorization_three_categories_balanced(self, scorer):
        """Three balanced categories should return 4 points."""
        result = scorer._calculate_categorization({
            "programming_languages": ["python", "javascript"],
            "frameworks": ["react", "fastapi"],
            "databases": ["postgresql", "mongodb"],
        })
        assert result == 4  # 3 categories + 1 balance bonus


# =============================================================================
# Market Relevance Score Tests
# =============================================================================

class TestCalculateMarketRelevance:
    """Tests for _calculate_market_relevance method."""
    
    def test_market_relevance_no_hot_skills(self, scorer):
        """No hot skills should return 0."""
        result = scorer._calculate_market_relevance({
            "programming_languages": ["perl", "cobol"],
        })
        assert result == 0
    
    def test_market_relevance_one_hot_skill(self, scorer):
        """One hot skill should return 1 point."""
        result = scorer._calculate_market_relevance({
            "programming_languages": ["python"],
        })
        assert result == 1
    
    def test_market_relevance_some_hot_skills(self, scorer):
        """Multiple hot skills should return corresponding points."""
        result = scorer._calculate_market_relevance({
            "programming_languages": ["python", "typescript"],
            "frameworks": ["react"],
        })
        # python, typescript, react are all hot skills
        assert result == 3
    
    def test_market_relevance_max_score(self, scorer):
        """Should cap at 6 points even with more hot skills."""
        result = scorer._calculate_market_relevance({
            "programming_languages": ["python", "typescript", "go", "rust"],
            "frameworks": ["react", "nextjs", "fastapi"],
            "devops": ["docker", "kubernetes", "aws"],
        })
        # Many hot skills, but capped at 6
        assert result == 6
    
    def test_market_relevance_mixed_skills(self, scorer):
        """Mix of hot and non-hot skills should only count hot ones."""
        result = scorer._calculate_market_relevance({
            "programming_languages": ["python", "perl", "cobol"],  # python is hot
            "frameworks": ["react", "jquery"],  # react is hot
        })
        assert result == 2


# =============================================================================
# Evidence Score Extraction Tests
# =============================================================================

class TestExtractEvidenceScore:
    """Tests for extract_evidence_score method."""
    
    def test_evidence_no_llm_response_returns_default(self, scorer):
        """No LLM response should return default score of 3."""
        result = scorer.extract_evidence_score(None)
        assert result == 3
    
    def test_evidence_empty_llm_response_returns_default(self, scorer):
        """Empty LLM response should return default score of 3."""
        result = scorer.extract_evidence_score({})
        assert result == 3
    
    def test_evidence_missing_criteria_returns_default(self, scorer):
        """Missing criteria key should return default score of 3."""
        result = scorer.extract_evidence_score({"other": "data"})
        assert result == 3
    
    def test_evidence_missing_skills_uses_default_fifty(self, scorer):
        """Missing skills in criteria should use 50 as default."""
        result = scorer.extract_evidence_score({"criteria": {}})
        assert result == 3  # 50 * 6 / 100 = 3
    
    def test_evidence_zero_score(self, scorer):
        """0 LLM skills score should return 0."""
        result = scorer.extract_evidence_score({"criteria": {"skills": 0}})
        assert result == 0
    
    def test_evidence_low_score(self, scorer):
        """Low LLM skills score should return proportionally low score."""
        result = scorer.extract_evidence_score({"criteria": {"skills": 25}})
        assert result == 2  # 25 * 6 / 100 = 1.5, rounds to 2
    
    def test_evidence_medium_score(self, scorer):
        """Medium LLM skills score should return medium score."""
        result = scorer.extract_evidence_score({"criteria": {"skills": 50}})
        assert result == 3  # 50 * 6 / 100 = 3
    
    def test_evidence_high_score(self, scorer):
        """High LLM skills score should return high score."""
        result = scorer.extract_evidence_score({"criteria": {"skills": 85}})
        assert result == 5  # 85 * 6 / 100 = 5.1, rounds to 5
    
    def test_evidence_max_score(self, scorer):
        """100 LLM skills score should return 6."""
        result = scorer.extract_evidence_score({"criteria": {"skills": 100}})
        assert result == 6
    
    def test_evidence_over_max_caps_at_six(self, scorer):
        """Over 100 should still cap at 6."""
        result = scorer.extract_evidence_score({"criteria": {"skills": 150}})
        assert result == 6
    
    def test_evidence_invalid_criteria_type_returns_default(self, scorer):
        """Invalid criteria type should return default."""
        result = scorer.extract_evidence_score({"criteria": "invalid"})
        assert result == 3
    
    def test_evidence_invalid_skills_type_returns_default(self, scorer):
        """Invalid skills type should return default."""
        result = scorer.extract_evidence_score({"criteria": {"skills": "invalid"}})
        assert result == 3
    
    def test_evidence_float_score(self, scorer):
        """Float LLM skills score should work correctly."""
        result = scorer.extract_evidence_score({"criteria": {"skills": 75.5}})
        assert result == 5  # 75.5 * 6 / 100 = 4.53, rounds to 5


# =============================================================================
# Calculate Skill Score Tests
# =============================================================================

class TestCalculateSkillScore:
    """Tests for calculate_skill_score main method."""
    
    def test_returns_complete_result(self, scorer):
        """Should return all required fields."""
        sample_cv = "Experienced Python developer with React, PostgreSQL, Docker skills."
        result = scorer.calculate_skill_score(sample_cv)
        
        assert "completeness_score" in result
        assert "categorization_score" in result
        assert "evidence_score" in result
        assert "market_relevance_score" in result
        assert "total_score" in result
        assert "skill_categories" in result
        assert "recommendations" in result
    
    def test_total_is_sum_of_parts(self, scorer):
        """Total score should equal sum of sub-scores."""
        sample_cv = "Python developer with React and PostgreSQL experience. Docker, AWS, Kubernetes."
        result = scorer.calculate_skill_score(sample_cv)
        
        expected_total = (
            result["completeness_score"] +
            result["categorization_score"] +
            result["evidence_score"] +
            result["market_relevance_score"]
        )
        assert result["total_score"] == expected_total
    
    def test_deterministic_without_llm(self, scorer):
        """Same input should always produce same output (rule-based components)."""
        sample_cv = "Python developer with React and PostgreSQL experience. Docker, AWS, Kubernetes."
        
        result1 = scorer.calculate_skill_score(sample_cv)
        result2 = scorer.calculate_skill_score(sample_cv)
        
        # All rule-based scores must be identical
        assert result1["completeness_score"] == result2["completeness_score"]
        assert result1["categorization_score"] == result2["categorization_score"]
        assert result1["market_relevance_score"] == result2["market_relevance_score"]
        assert result1["evidence_score"] == result2["evidence_score"]
        assert result1["total_score"] == result2["total_score"]
    
    def test_with_llm_response(self, scorer):
        """Should use LLM response for evidence score."""
        sample_cv = "Python developer"
        llm_response = {"criteria": {"skills": 80}}
        
        result = scorer.calculate_skill_score(sample_cv, llm_response)
        
        # Evidence score should be derived from LLM (80 * 6 / 100 = 4.8 ≈ 5)
        assert result["evidence_score"] == 5
    
    def test_without_llm_response(self, scorer):
        """Should use default evidence score when no LLM response."""
        sample_cv = "Python developer"
        
        result = scorer.calculate_skill_score(sample_cv)
        
        # Evidence score should be default (3)
        assert result["evidence_score"] == 3
    
    def test_empty_cv_returns_low_scores(self, scorer):
        """Empty or minimal CV should return low scores."""
        result = scorer.calculate_skill_score("")
        
        assert result["completeness_score"] == 0
        assert result["categorization_score"] == 0
        assert result["market_relevance_score"] == 0
        # Evidence defaults to 3
        assert result["evidence_score"] == 3
        assert result["total_score"] == 3
    
    def test_skill_categories_populated(self, scorer):
        """skill_categories should contain extracted skills."""
        sample_cv = "Python and JavaScript developer using React and PostgreSQL"
        result = scorer.calculate_skill_score(sample_cv)
        
        assert isinstance(result["skill_categories"], dict)
        # Should have found at least some skills
        total_skills = sum(len(s) for s in result["skill_categories"].values())
        assert total_skills > 0
    
    def test_recommendations_is_list(self, scorer):
        """recommendations should be a list."""
        sample_cv = "Python developer"
        result = scorer.calculate_skill_score(sample_cv)
        
        assert isinstance(result["recommendations"], list)


# =============================================================================
# Recommendations Generation Tests
# =============================================================================

class TestGenerateRecommendations:
    """Tests for _generate_recommendations method."""
    
    def test_recommendations_for_low_completeness(self, scorer):
        """Low completeness should trigger skills recommendation."""
        skills: Dict[str, List[str]] = {"programming_languages": ["python"]}
        scores = {
            "completeness_score": 1,
            "categorization_score": 1,
            "evidence_score": 4,
            "market_relevance_score": 1,
        }
        
        result = scorer._generate_recommendations(skills, scores)
        
        assert any("more technical skills" in r.lower() for r in result)
    
    def test_recommendations_for_missing_hot_skills(self, scorer):
        """No hot skills should trigger hot skills recommendation."""
        skills: Dict[str, List[str]] = {"programming_languages": ["perl", "cobol"]}
        scores = {
            "completeness_score": 5,
            "categorization_score": 4,
            "evidence_score": 4,
            "market_relevance_score": 0,
        }
        
        result = scorer._generate_recommendations(skills, scores)
        
        assert any("in-demand" in r.lower() or "learning" in r.lower() for r in result)
    
    def test_recommendations_for_missing_categories(self, scorer):
        """Missing main categories (1-3) should trigger category recommendation."""
        # Cover most categories, leaving 2-3 missing - triggers recommendation
        skills: Dict[str, List[str]] = {
            "programming_languages": ["python", "javascript"],
            "frameworks": ["react"],
            "databases": ["postgresql"],
            "devops": ["docker"],
            "infrastructure": ["windows server"],
            "networking": ["tcp/ip"],
            # Missing: compliance, soft_skills, ai_ml (only 3 missing)
        }
        scores = {
            "completeness_score": 5,
            "categorization_score": 5,
            "evidence_score": 4,
            "market_relevance_score": 2,
        }
        
        result = scorer._generate_recommendations(skills, scores)
        
        # Should recommend adding skills in missing categories
        assert any("add skills" in r.lower() or "broader" in r.lower() for r in result)
    
    def test_recommendations_for_low_evidence(self, scorer):
        """Low evidence score should trigger experience recommendation."""
        skills: Dict[str, List[str]] = {
            "programming_languages": ["python", "javascript"],
            "frameworks": ["react", "fastapi"],
        }
        scores = {
            "completeness_score": 5,
            "categorization_score": 4,
            "evidence_score": 2,
            "market_relevance_score": 3,
        }
        
        result = scorer._generate_recommendations(skills, scores)
        
        assert any("experience" in r.lower() or "examples" in r.lower() for r in result)
    
    def test_recommendations_for_unbalanced_skills(self, scorer):
        """Unbalanced skills should trigger balance recommendation."""
        # 10 programming languages, 1 framework = unbalanced
        skills: Dict[str, List[str]] = {
            "programming_languages": [
                "python", "javascript", "typescript", "java", "go",
                "rust", "ruby", "php", "scala", "kotlin"
            ],
            "frameworks": ["react"],
        }
        scores = {
            "completeness_score": 6,
            "categorization_score": 2,
            "evidence_score": 4,
            "market_relevance_score": 4,
        }
        
        result = scorer._generate_recommendations(skills, scores)
        
        assert any("balance" in r.lower() for r in result)
    
    def test_recommendations_max_five(self, scorer):
        """Should return at most 5 recommendations."""
        # Worst case: all recommendations should trigger
        skills: Dict[str, List[str]] = {"programming_languages": ["perl"]}
        scores = {
            "completeness_score": 1,
            "categorization_score": 1,
            "evidence_score": 1,
            "market_relevance_score": 0,
        }
        
        result = scorer._generate_recommendations(skills, scores)
        
        assert len(result) <= 5
    
    def test_recommendations_empty_for_perfect_score(self, scorer):
        """High scores should return fewer or no recommendations."""
        skills: Dict[str, List[str]] = {
            "programming_languages": ["python", "typescript", "go"],
            "frameworks": ["react", "fastapi", "nextjs"],
            "databases": ["postgresql", "mongodb", "redis"],
            "devops": ["docker", "kubernetes", "aws"],
            "soft_skills": ["communication", "teamwork"],
        }
        scores = {
            "completeness_score": 7,
            "categorization_score": 6,
            "evidence_score": 6,
            "market_relevance_score": 6,
        }
        
        result = scorer._generate_recommendations(skills, scores)
        
        # With perfect scores, should have very few recommendations
        assert len(result) <= 2


# =============================================================================
# Singleton Pattern Tests
# =============================================================================

class TestSingletonPattern:
    """Tests for SkillScorer singleton pattern."""
    
    def test_singleton_returns_same_instance(self):
        """Multiple instantiations should return same instance."""
        SkillScorer._instance = None
        scorer1 = SkillScorer()
        scorer2 = SkillScorer()
        
        assert scorer1 is scorer2
    
    def test_singleton_extractor_initialized(self, scorer):
        """Singleton should have extractor initialized."""
        assert hasattr(scorer, "_extractor")
        assert scorer._extractor is not None
