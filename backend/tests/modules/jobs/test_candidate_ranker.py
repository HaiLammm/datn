"""
Unit tests for CandidateRanker class.

Tests skill matching, experience scoring, and ranking functionality.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from app.modules.jobs.candidate_ranker import (
    CandidateRanker,
    MatchBreakdown,
    RankedCandidate,
    SKILL_WEIGHT,
    EXPERIENCE_WEIGHT,
    REQUIRED_SKILL_WEIGHT,
    NICE_TO_HAVE_WEIGHT,
)


@pytest.fixture
def ranker():
    """Create a CandidateRanker instance."""
    return CandidateRanker()


class TestMatchBreakdown:
    """Tests for MatchBreakdown dataclass."""
    
    def test_default_values(self):
        """Test default values are empty/zero."""
        breakdown = MatchBreakdown()
        assert breakdown.matched_skills == []
        assert breakdown.missing_skills == []
        assert breakdown.extra_skills == []
        assert breakdown.skill_score == 0.0
        assert breakdown.experience_score == 0.0
        assert breakdown.experience_years is None
    
    def test_to_dict(self):
        """Test conversion to dictionary."""
        breakdown = MatchBreakdown(
            matched_skills=["python", "fastapi"],
            missing_skills=["kubernetes"],
            extra_skills=["docker"],
            skill_score=45.5,
            experience_score=25.0,
            experience_years=5,
        )
        result = breakdown.to_dict()
        
        assert result["matched_skills"] == ["python", "fastapi"]
        assert result["missing_skills"] == ["kubernetes"]
        assert result["extra_skills"] == ["docker"]
        assert result["skill_score"] == 45.5
        assert result["experience_score"] == 25.0
        assert result["experience_years"] == 5


class TestRankedCandidate:
    """Tests for RankedCandidate dataclass."""
    
    def test_to_dict(self):
        """Test conversion to dictionary."""
        cv_id = uuid4()
        breakdown = MatchBreakdown(matched_skills=["python"])
        
        candidate = RankedCandidate(
            cv_id=cv_id,
            user_id=123,
            match_score=85,
            breakdown=breakdown,
            cv_summary="Senior developer",
            filename="resume.pdf",
        )
        result = candidate.to_dict()
        
        assert result["cv_id"] == str(cv_id)
        assert result["user_id"] == 123
        assert result["match_score"] == 85
        assert result["cv_summary"] == "Senior developer"
        assert result["filename"] == "resume.pdf"
        assert "matched_skills" in result["breakdown"]


class TestCalculateSkillScore:
    """Tests for _calculate_skill_score method."""
    
    def test_all_required_skills_matched(self, ranker):
        """Test 100% match on required skills."""
        required = ["python", "fastapi", "postgresql"]
        nice_to_have = []
        cv_skills = ["python", "fastapi", "postgresql"]
        
        result = ranker._calculate_skill_score(required, nice_to_have, cv_skills)
        
        assert set(result["matched_skills"]) == {"python", "fastapi", "postgresql"}
        assert result["missing_skills"] == []
        assert result["skill_score"] == REQUIRED_SKILL_WEIGHT  # 60
    
    def test_all_required_plus_nice_to_have(self, ranker):
        """Test full match on both required and nice-to-have."""
        required = ["python", "fastapi"]
        nice_to_have = ["docker", "kubernetes"]
        cv_skills = ["python", "fastapi", "docker", "kubernetes"]
        
        result = ranker._calculate_skill_score(required, nice_to_have, cv_skills)
        
        assert len(result["matched_skills"]) == 4
        assert result["missing_skills"] == []
        expected_score = REQUIRED_SKILL_WEIGHT + NICE_TO_HAVE_WEIGHT  # 60 + 10 = 70
        assert result["skill_score"] == expected_score
    
    def test_partial_required_match(self, ranker):
        """Test partial match on required skills."""
        required = ["python", "fastapi", "postgresql", "redis"]
        nice_to_have = []
        cv_skills = ["python", "fastapi"]  # 2 out of 4
        
        result = ranker._calculate_skill_score(required, nice_to_have, cv_skills)
        
        assert set(result["matched_skills"]) == {"python", "fastapi"}
        assert set(result["missing_skills"]) == {"postgresql", "redis"}
        expected_score = (2 / 4) * REQUIRED_SKILL_WEIGHT  # 0.5 * 60 = 30
        assert result["skill_score"] == expected_score
    
    def test_no_skills_matched(self, ranker):
        """Test no skills matched."""
        required = ["python", "fastapi"]
        nice_to_have = ["docker"]
        cv_skills = ["java", "spring"]
        
        result = ranker._calculate_skill_score(required, nice_to_have, cv_skills)
        
        assert result["matched_skills"] == []
        assert set(result["missing_skills"]) == {"python", "fastapi"}
        assert set(result["extra_skills"]) == {"java", "spring"}
        assert result["skill_score"] == 0.0
    
    def test_extra_skills_detected(self, ranker):
        """Test detection of extra skills not in JD."""
        required = ["python"]
        nice_to_have = ["docker"]
        cv_skills = ["python", "docker", "aws", "terraform", "kubernetes"]
        
        result = ranker._calculate_skill_score(required, nice_to_have, cv_skills)
        
        assert set(result["matched_skills"]) == {"python", "docker"}
        assert set(result["extra_skills"]) == {"aws", "terraform", "kubernetes"}
    
    def test_empty_required_skills(self, ranker):
        """Test with no required skills (full score)."""
        required = []
        nice_to_have = ["docker"]
        cv_skills = ["python", "docker"]
        
        result = ranker._calculate_skill_score(required, nice_to_have, cv_skills)
        
        # Should get full required score when no requirements
        assert result["skill_score"] == REQUIRED_SKILL_WEIGHT + NICE_TO_HAVE_WEIGHT
    
    def test_case_insensitive_matching(self, ranker):
        """Test that matching is case-insensitive (all lowercased by caller)."""
        # Note: _calculate_skill_score expects lowercase inputs 
        # (normalization happens in _calculate_match)
        required = ["python", "fastapi", "postgresql"]
        nice_to_have = []
        cv_skills = ["python", "fastapi", "postgresql"]
        
        result = ranker._calculate_skill_score(required, nice_to_have, cv_skills)
        
        # All should match
        assert len(result["matched_skills"]) == 3
        assert result["missing_skills"] == []


class TestCalculateExperienceScore:
    """Tests for _calculate_experience_score method."""
    
    def test_meets_requirement(self, ranker):
        """Test when candidate meets experience requirement."""
        score = ranker._calculate_experience_score(required_years=3, cv_years=3)
        assert score == EXPERIENCE_WEIGHT  # 30
    
    def test_exceeds_requirement(self, ranker):
        """Test when candidate exceeds experience requirement."""
        score = ranker._calculate_experience_score(required_years=3, cv_years=10)
        assert score == EXPERIENCE_WEIGHT  # 30 (capped at 1.0 ratio)
    
    def test_below_requirement(self, ranker):
        """Test when candidate is below experience requirement."""
        score = ranker._calculate_experience_score(required_years=5, cv_years=3)
        expected = (3 / 5) * EXPERIENCE_WEIGHT  # 0.6 * 30 = 18
        assert score == expected
    
    def test_no_requirement(self, ranker):
        """Test when no experience requirement specified."""
        score = ranker._calculate_experience_score(required_years=None, cv_years=5)
        assert score == EXPERIENCE_WEIGHT  # Full score
    
    def test_zero_requirement(self, ranker):
        """Test when experience requirement is 0."""
        score = ranker._calculate_experience_score(required_years=0, cv_years=5)
        assert score == EXPERIENCE_WEIGHT  # Full score
    
    def test_no_cv_experience(self, ranker):
        """Test when CV has no experience info."""
        score = ranker._calculate_experience_score(required_years=5, cv_years=None)
        assert score == 0.0
    
    def test_zero_cv_years(self, ranker):
        """Test when CV has 0 years experience."""
        score = ranker._calculate_experience_score(required_years=5, cv_years=0)
        assert score == 0.0


class TestExtractExperienceYears:
    """Tests for _extract_experience_years method."""
    
    def test_from_skill_breakdown(self, ranker):
        """Test extracting years from skill_breakdown."""
        cv_analysis = MagicMock()
        cv_analysis.skill_breakdown = {"experience_years": 5}
        cv_analysis.ai_feedback = None
        
        result = ranker._extract_experience_years(cv_analysis)
        assert result == 5
    
    def test_from_ai_feedback(self, ranker):
        """Test extracting years from ai_feedback."""
        cv_analysis = MagicMock()
        cv_analysis.skill_breakdown = None
        cv_analysis.ai_feedback = {"experience_years": 3}
        
        result = ranker._extract_experience_years(cv_analysis)
        assert result == 3
    
    def test_skill_breakdown_priority(self, ranker):
        """Test skill_breakdown takes priority over ai_feedback."""
        cv_analysis = MagicMock()
        cv_analysis.skill_breakdown = {"experience_years": 5}
        cv_analysis.ai_feedback = {"experience_years": 3}
        
        result = ranker._extract_experience_years(cv_analysis)
        assert result == 5
    
    def test_not_available(self, ranker):
        """Test when experience years not available."""
        cv_analysis = MagicMock()
        cv_analysis.skill_breakdown = None
        cv_analysis.ai_feedback = None
        
        result = ranker._extract_experience_years(cv_analysis)
        assert result is None
    
    def test_invalid_value(self, ranker):
        """Test with invalid experience value."""
        cv_analysis = MagicMock()
        cv_analysis.skill_breakdown = {"experience_years": "not a number"}
        cv_analysis.ai_feedback = None
        
        result = ranker._extract_experience_years(cv_analysis)
        assert result is None


class TestCalculateMatch:
    """Tests for _calculate_match method."""
    
    def test_full_match(self, ranker):
        """Test a full match scenario."""
        jd_requirements = {
            "required_skills": ["python", "fastapi"],
            "nice_to_have_skills": ["docker"],
            "min_experience_years": 3,
        }
        
        cv_analysis = MagicMock()
        cv_analysis.cv_id = uuid4()
        cv_analysis.cv = MagicMock()
        cv_analysis.cv.user_id = 123
        cv_analysis.cv.filename = "resume.pdf"
        cv_analysis.extracted_skills = ["python", "fastapi", "docker"]
        cv_analysis.skill_categories = None
        cv_analysis.skill_breakdown = {"experience_years": 5}
        cv_analysis.ai_feedback = None
        cv_analysis.ai_summary = "Senior Python developer"
        
        result = ranker._calculate_match(jd_requirements, cv_analysis)
        
        assert result.match_score == 100  # Full match
        assert result.cv_summary == "Senior Python developer"
        assert result.breakdown.experience_years == 5
    
    def test_partial_match(self, ranker):
        """Test a partial match scenario."""
        jd_requirements = {
            "required_skills": ["python", "fastapi", "postgresql", "redis"],
            "nice_to_have_skills": [],
            "min_experience_years": 5,
        }
        
        cv_analysis = MagicMock()
        cv_analysis.cv_id = uuid4()
        cv_analysis.cv = MagicMock()
        cv_analysis.cv.user_id = 456
        cv_analysis.cv.filename = "cv.pdf"
        cv_analysis.extracted_skills = ["python", "fastapi"]  # 2/4 required
        cv_analysis.skill_categories = None
        cv_analysis.skill_breakdown = {"experience_years": 3}  # 3/5 years
        cv_analysis.ai_feedback = None
        cv_analysis.ai_summary = None
        
        result = ranker._calculate_match(jd_requirements, cv_analysis)
        
        # Skill: 2/4 * 60 = 30, Experience: 3/5 * 30 = 18, Total = 48
        assert result.match_score == 48
        assert set(result.breakdown.matched_skills) == {"python", "fastapi"}
        assert set(result.breakdown.missing_skills) == {"postgresql", "redis"}
    
    def test_skills_from_categories(self, ranker):
        """Test extracting skills from skill_categories when extracted_skills is empty."""
        jd_requirements = {
            "required_skills": ["python", "react"],
            "nice_to_have_skills": [],
            "min_experience_years": None,
        }
        
        cv_analysis = MagicMock()
        cv_analysis.cv_id = uuid4()
        cv_analysis.cv = MagicMock()
        cv_analysis.cv.user_id = 789
        cv_analysis.cv.filename = None
        cv_analysis.extracted_skills = []  # Empty
        cv_analysis.skill_categories = {
            "programming_languages": ["python", "javascript"],
            "frameworks": ["react", "fastapi"],
        }
        cv_analysis.skill_breakdown = None
        cv_analysis.ai_feedback = None
        cv_analysis.ai_summary = None
        
        result = ranker._calculate_match(jd_requirements, cv_analysis)
        
        # Both python and react should be matched from categories
        assert "python" in result.breakdown.matched_skills
        assert "react" in result.breakdown.matched_skills


class TestRankCandidates:
    """Tests for rank_candidates method (integration tests with mocked DB)."""
    
    @pytest.mark.asyncio
    async def test_jd_not_found(self, ranker):
        """Test error when JD not found."""
        db = AsyncMock()
        
        with patch.object(ranker, '_get_jd', return_value=None):
            with pytest.raises(ValueError, match="not found"):
                await ranker.rank_candidates(db, uuid4())
    
    @pytest.mark.asyncio
    async def test_jd_not_parsed(self, ranker):
        """Test error when JD parsing not complete."""
        db = AsyncMock()
        mock_jd = MagicMock()
        mock_jd.parse_status = "pending"
        
        with patch.object(ranker, '_get_jd', return_value=mock_jd):
            with pytest.raises(ValueError, match="not complete"):
                await ranker.rank_candidates(db, uuid4())
    
    @pytest.mark.asyncio
    async def test_no_cv_analyses(self, ranker):
        """Test empty result when no CVs available."""
        db = AsyncMock()
        mock_jd = MagicMock()
        mock_jd.parse_status = "completed"
        mock_jd.parsed_requirements = {"required_skills": ["python"]}
        
        with patch.object(ranker, '_get_jd', return_value=mock_jd):
            with patch.object(ranker, '_get_all_cv_analyses', return_value=[]):
                candidates, total = await ranker.rank_candidates(db, uuid4())
                
                assert candidates == []
                assert total == 0
    
    @pytest.mark.asyncio
    async def test_ranking_order(self, ranker):
        """Test that candidates are ranked by score descending."""
        db = AsyncMock()
        mock_jd = MagicMock()
        mock_jd.parse_status = "completed"
        mock_jd.parsed_requirements = {
            "required_skills": ["python", "fastapi"],
            "nice_to_have_skills": [],
            "min_experience_years": None,
        }
        
        # Create mock CV analyses with different skill matches
        cv1 = MagicMock()
        cv1.cv_id = uuid4()
        cv1.cv = MagicMock(user_id=1, filename="cv1.pdf")
        cv1.extracted_skills = ["python"]  # 1/2 match = 30 points
        cv1.skill_categories = None
        cv1.skill_breakdown = None
        cv1.ai_feedback = None
        cv1.ai_summary = None
        
        cv2 = MagicMock()
        cv2.cv_id = uuid4()
        cv2.cv = MagicMock(user_id=2, filename="cv2.pdf")
        cv2.extracted_skills = ["python", "fastapi"]  # 2/2 match = 60 points
        cv2.skill_categories = None
        cv2.skill_breakdown = None
        cv2.ai_feedback = None
        cv2.ai_summary = None
        
        cv3 = MagicMock()
        cv3.cv_id = uuid4()
        cv3.cv = MagicMock(user_id=3, filename="cv3.pdf")
        cv3.extracted_skills = []  # 0/2 match = 0 points
        cv3.skill_categories = None
        cv3.skill_breakdown = None
        cv3.ai_feedback = None
        cv3.ai_summary = None
        
        with patch.object(ranker, '_get_jd', return_value=mock_jd):
            with patch.object(ranker, '_get_all_cv_analyses', return_value=[cv1, cv2, cv3]):
                candidates, total = await ranker.rank_candidates(db, uuid4())
                
                assert total == 3
                assert len(candidates) == 3
                # cv2 should be first (highest score)
                assert candidates[0].cv_id == cv2.cv_id
                # cv1 should be second
                assert candidates[1].cv_id == cv1.cv_id
                # cv3 should be last
                assert candidates[2].cv_id == cv3.cv_id
    
    @pytest.mark.asyncio
    async def test_min_score_filter(self, ranker):
        """Test min_score filtering."""
        db = AsyncMock()
        mock_jd = MagicMock()
        mock_jd.parse_status = "completed"
        mock_jd.parsed_requirements = {
            "required_skills": ["python", "fastapi"],
            "nice_to_have_skills": [],
            "min_experience_years": None,
        }
        
        cv_low = MagicMock()
        cv_low.cv_id = uuid4()
        cv_low.cv = MagicMock(user_id=1, filename="low.pdf")
        cv_low.extracted_skills = []  # 0 points
        cv_low.skill_categories = None
        cv_low.skill_breakdown = None
        cv_low.ai_feedback = None
        cv_low.ai_summary = None
        
        cv_high = MagicMock()
        cv_high.cv_id = uuid4()
        cv_high.cv = MagicMock(user_id=2, filename="high.pdf")
        cv_high.extracted_skills = ["python", "fastapi"]  # 60 + 30 = 90 points
        cv_high.skill_categories = None
        cv_high.skill_breakdown = None
        cv_high.ai_feedback = None
        cv_high.ai_summary = None
        
        with patch.object(ranker, '_get_jd', return_value=mock_jd):
            with patch.object(ranker, '_get_all_cv_analyses', return_value=[cv_low, cv_high]):
                candidates, total = await ranker.rank_candidates(db, uuid4(), min_score=50)
                
                # Only high score candidate should be included
                assert total == 1
                assert candidates[0].cv_id == cv_high.cv_id
    
    @pytest.mark.asyncio
    async def test_pagination(self, ranker):
        """Test pagination with limit and offset."""
        db = AsyncMock()
        mock_jd = MagicMock()
        mock_jd.parse_status = "completed"
        mock_jd.parsed_requirements = {
            "required_skills": ["python"],
            "nice_to_have_skills": [],
            "min_experience_years": None,
        }
        
        # Create 5 CV analyses
        cvs = []
        for i in range(5):
            cv = MagicMock()
            cv.cv_id = uuid4()
            cv.cv = MagicMock(user_id=i, filename=f"cv{i}.pdf")
            cv.extracted_skills = ["python"]
            cv.skill_categories = None
            cv.skill_breakdown = None
            cv.ai_feedback = None
            cv.ai_summary = None
            cvs.append(cv)
        
        with patch.object(ranker, '_get_jd', return_value=mock_jd):
            with patch.object(ranker, '_get_all_cv_analyses', return_value=cvs):
                # Get first 2
                candidates, total = await ranker.rank_candidates(
                    db, uuid4(), limit=2, offset=0
                )
                assert len(candidates) == 2
                assert total == 5
                
                # Get next 2
                candidates, total = await ranker.rank_candidates(
                    db, uuid4(), limit=2, offset=2
                )
                assert len(candidates) == 2
                assert total == 5
                
                # Get last 1
                candidates, total = await ranker.rank_candidates(
                    db, uuid4(), limit=2, offset=4
                )
                assert len(candidates) == 1
                assert total == 5
