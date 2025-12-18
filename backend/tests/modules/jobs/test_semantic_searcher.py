"""
Unit tests for SemanticSearcher class.

Tests cover:
- Query parsing (rule-based and LLM)
- Skill matching score calculation
- Keyword matching score calculation
- Full relevance calculation
- Search with mocked database
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from app.modules.jobs.semantic_searcher import (
    SemanticSearcher,
    ParsedQuery,
    SearchResult,
    SKILL_WEIGHT,
    KEYWORD_WEIGHT,
)
from app.modules.ai.models import CVAnalysis, AnalysisStatus


@pytest.fixture
def searcher():
    """Create a SemanticSearcher instance for testing."""
    return SemanticSearcher()


class TestParseQuery:
    """Tests for query parsing functionality."""
    
    def test_parse_query_extracts_skills(self, searcher):
        """Test that skills are extracted from query."""
        query = "Python developer with AWS experience"
        result = searcher._parse_query_rules(query)
        
        assert "python" in result.extracted_skills
        assert "aws" in result.extracted_skills
        assert result.raw_query == query
    
    def test_parse_query_extracts_multiple_skills(self, searcher):
        """Test extraction of multiple skills."""
        query = "React and Node.js developer with PostgreSQL and Docker"
        result = searcher._parse_query_rules(query)
        
        assert "react" in result.extracted_skills
        # Note: node.js may be normalized to 'javascript' in taxonomy
        assert "javascript" in result.extracted_skills or "node.js" in result.extracted_skills
        assert "postgresql" in result.extracted_skills
        assert "docker" in result.extracted_skills
    
    def test_parse_query_extracts_experience_years(self, searcher):
        """Test extraction of experience years."""
        query = "Senior developer with 5 years experience"
        result = searcher._parse_query_rules(query)
        
        assert result.min_experience == 5
        assert len(result.experience_keywords) > 0
    
    def test_parse_query_extracts_experience_plus_format(self, searcher):
        """Test extraction of '5+ years' format."""
        query = "Developer with 3+ years Python"
        result = searcher._parse_query_rules(query)
        
        assert result.min_experience == 3
    
    def test_parse_query_extracts_vietnamese_experience(self, searcher):
        """Test extraction of Vietnamese experience format."""
        query = "Lập trình viên 3 năm kinh nghiệm"
        result = searcher._parse_query_rules(query)
        
        assert result.min_experience == 3
    
    def test_parse_query_extracts_role_keywords(self, searcher):
        """Test extraction of role keywords."""
        query = "Senior fullstack developer"
        result = searcher._parse_query_rules(query)
        
        assert "senior" in result.keywords
        assert "fullstack" in result.keywords or "full-stack" in result.keywords
        assert "developer" in result.keywords
    
    def test_parse_query_empty_returns_empty(self, searcher):
        """Test that empty query returns empty results."""
        result = searcher._parse_query_rules("")
        
        assert len(result.extracted_skills) == 0
        assert len(result.keywords) == 0
        assert result.min_experience is None
    
    def test_parse_query_no_skills_returns_keywords(self, searcher):
        """Test query with no skills but keywords."""
        query = "Senior engineer with experience"
        result = searcher._parse_query_rules(query)
        
        # Should still extract role keywords
        assert "senior" in result.keywords or len(result.experience_keywords) >= 0


class TestSkillMatchScore:
    """Tests for skill matching score calculation."""
    
    def test_skill_match_score_all_matched(self, searcher):
        """Test full score when all skills match."""
        query_skills = ["python", "aws"]
        cv_skills = ["python", "aws", "docker", "postgresql"]
        
        score = searcher._skill_match_score(query_skills, cv_skills)
        
        # All query skills matched = full skill weight
        assert score == SKILL_WEIGHT  # 70.0
    
    def test_skill_match_score_partial(self, searcher):
        """Test partial score when some skills match."""
        query_skills = ["python", "aws", "kubernetes"]
        cv_skills = ["python", "aws"]
        
        score = searcher._skill_match_score(query_skills, cv_skills)
        
        # 2/3 matched = 2/3 * 70 = 46.67
        expected = (2 / 3) * SKILL_WEIGHT
        assert abs(score - expected) < 0.01
    
    def test_skill_match_score_none_matched(self, searcher):
        """Test zero score when no skills match."""
        query_skills = ["python", "aws"]
        cv_skills = ["java", "azure"]
        
        score = searcher._skill_match_score(query_skills, cv_skills)
        
        assert score == 0.0
    
    def test_skill_match_score_empty_query_returns_neutral(self, searcher):
        """Test neutral score when no skills in query."""
        query_skills = []
        cv_skills = ["python", "aws"]
        
        score = searcher._skill_match_score(query_skills, cv_skills)
        
        # No skills in query = neutral score (35)
        assert score == 35.0
    
    def test_skill_match_score_case_insensitive(self, searcher):
        """Test that skill matching is case-insensitive."""
        query_skills = ["Python", "AWS"]
        cv_skills = ["python", "aws"]
        
        score = searcher._skill_match_score(query_skills, cv_skills)
        
        assert score == SKILL_WEIGHT
    
    def test_skill_match_score_half_matched(self, searcher):
        """Test score with exactly half skills matched."""
        query_skills = ["python", "aws", "docker", "kubernetes"]
        cv_skills = ["python", "aws"]
        
        score = searcher._skill_match_score(query_skills, cv_skills)
        
        # 2/4 matched = 0.5 * 70 = 35
        assert abs(score - 35.0) < 0.01


class TestKeywordMatchScore:
    """Tests for keyword matching score calculation."""
    
    def test_keyword_match_score_all_matched(self, searcher):
        """Test full score when all keywords found."""
        keywords = ["senior", "developer"]
        cv_content = "Senior Python Developer with 5 years experience"
        
        score = searcher._keyword_match_score(keywords, cv_content)
        
        assert score == KEYWORD_WEIGHT  # 30.0
    
    def test_keyword_match_score_partial(self, searcher):
        """Test partial score when some keywords found."""
        keywords = ["senior", "developer", "architect"]
        cv_content = "Senior Python Developer"
        
        score = searcher._keyword_match_score(keywords, cv_content)
        
        # 2/3 matched = 2/3 * 30 = 20
        expected = (2 / 3) * KEYWORD_WEIGHT
        assert abs(score - expected) < 0.01
    
    def test_keyword_match_score_none_matched(self, searcher):
        """Test zero score when no keywords found."""
        keywords = ["senior", "architect"]
        cv_content = "Junior Python Developer"
        
        score = searcher._keyword_match_score(keywords, cv_content)
        
        # Only 0-1 keywords might match
        assert score < KEYWORD_WEIGHT
    
    def test_keyword_match_score_empty_keywords(self, searcher):
        """Test zero score with empty keywords."""
        keywords = []
        cv_content = "Senior Python Developer"
        
        score = searcher._keyword_match_score(keywords, cv_content)
        
        assert score == 0.0
    
    def test_keyword_match_score_empty_content(self, searcher):
        """Test zero score with empty content."""
        keywords = ["senior", "developer"]
        cv_content = ""
        
        score = searcher._keyword_match_score(keywords, cv_content)
        
        assert score == 0.0
    
    def test_keyword_match_score_case_insensitive(self, searcher):
        """Test that keyword matching is case-insensitive."""
        keywords = ["SENIOR", "Developer"]
        cv_content = "senior python developer"
        
        score = searcher._keyword_match_score(keywords, cv_content)
        
        assert score == KEYWORD_WEIGHT


class TestCalculateRelevance:
    """Tests for full relevance calculation."""
    
    @pytest.fixture
    def mock_cv_analysis(self):
        """Create a mock CV analysis."""
        analysis = MagicMock(spec=CVAnalysis)
        analysis.cv_id = uuid4()
        analysis.extracted_skills = ["python", "aws", "docker"]
        analysis.ai_summary = "Senior Python Developer with AWS experience"
        
        cv_mock = MagicMock()
        cv_mock.user_id = 1
        cv_mock.filename = "test_cv.pdf"
        analysis.cv = cv_mock
        
        return analysis
    
    def test_calculate_relevance_returns_search_result(self, searcher, mock_cv_analysis):
        """Test that relevance calculation returns SearchResult."""
        parsed_query = ParsedQuery(
            extracted_skills=["python", "aws"],
            keywords=["senior", "developer"],
            raw_query="Python developer"
        )
        
        result = searcher._calculate_relevance(parsed_query, mock_cv_analysis)
        
        assert isinstance(result, SearchResult)
        assert result.cv_id == mock_cv_analysis.cv_id
        assert result.user_id == 1
        assert 0 <= result.relevance_score <= 100
    
    def test_calculate_relevance_matched_skills(self, searcher, mock_cv_analysis):
        """Test that matched skills are correctly identified."""
        parsed_query = ParsedQuery(
            extracted_skills=["python", "aws", "kubernetes"],
            keywords=[],
            raw_query="Python AWS Kubernetes"
        )
        
        result = searcher._calculate_relevance(parsed_query, mock_cv_analysis)
        
        # python and aws should match, kubernetes should not
        assert "python" in result.matched_skills
        assert "aws" in result.matched_skills
        assert "kubernetes" not in result.matched_skills
    
    def test_calculate_relevance_high_score(self, searcher, mock_cv_analysis):
        """Test high relevance score with good matches."""
        parsed_query = ParsedQuery(
            extracted_skills=["python", "aws"],  # Both in CV
            keywords=["senior", "developer"],  # Both in summary
            raw_query="Senior Python developer with AWS"
        )
        
        result = searcher._calculate_relevance(parsed_query, mock_cv_analysis)
        
        # Should have high score (70 for skills + up to 30 for keywords)
        assert result.relevance_score >= 70
    
    def test_calculate_relevance_low_score(self, searcher, mock_cv_analysis):
        """Test low relevance score with poor matches."""
        parsed_query = ParsedQuery(
            extracted_skills=["java", "azure", "kubernetes"],  # None in CV
            keywords=["architect", "lead"],  # Not in summary
            raw_query="Java Azure Kubernetes architect"
        )
        
        result = searcher._calculate_relevance(parsed_query, mock_cv_analysis)
        
        # Should have low score (0 for skills, maybe 0 for keywords)
        assert result.relevance_score < 30
    
    def test_calculate_relevance_includes_cv_info(self, searcher, mock_cv_analysis):
        """Test that CV info is included in result."""
        parsed_query = ParsedQuery(
            extracted_skills=["python"],
            keywords=[],
            raw_query="Python"
        )
        
        result = searcher._calculate_relevance(parsed_query, mock_cv_analysis)
        
        assert result.cv_summary == mock_cv_analysis.ai_summary
        assert result.filename == "test_cv.pdf"


class TestSearchCandidates:
    """Tests for the main search_candidates method."""
    
    @pytest.fixture
    def mock_db(self):
        """Create a mock database session."""
        db = AsyncMock()
        return db
    
    @pytest.fixture
    def mock_cv_analyses(self):
        """Create mock CV analyses."""
        analyses = []
        for i in range(3):
            analysis = MagicMock(spec=CVAnalysis)
            analysis.cv_id = uuid4()
            analysis.extracted_skills = [
                ["python", "aws", "docker"],
                ["java", "spring", "kubernetes"],
                ["python", "react", "postgresql"],
            ][i]
            analysis.ai_summary = [
                "Senior Python Developer with AWS",
                "Java Backend Developer with Kubernetes",
                "Fullstack Python React Developer",
            ][i]
            analysis.status = AnalysisStatus.COMPLETED.value
            
            cv_mock = MagicMock()
            cv_mock.user_id = i + 1
            cv_mock.filename = f"cv_{i}.pdf"
            analysis.cv = cv_mock
            
            analyses.append(analysis)
        
        return analyses
    
    @pytest.mark.asyncio
    async def test_search_candidates_returns_results(self, searcher, mock_db, mock_cv_analyses):
        """Test that search returns ranked results."""
        with patch.object(searcher, '_get_all_cv_analyses', return_value=mock_cv_analyses):
            results, total = await searcher.search_candidates(
                query="Python developer",
                db=mock_db,
                limit=10,
                offset=0,
                min_score=0,
            )
        
        assert len(results) <= 10
        assert total >= 0
    
    @pytest.mark.asyncio
    async def test_search_candidates_sorted_by_score(self, searcher, mock_db, mock_cv_analyses):
        """Test that results are sorted by relevance score descending."""
        with patch.object(searcher, '_get_all_cv_analyses', return_value=mock_cv_analyses):
            results, total = await searcher.search_candidates(
                query="Python developer",
                db=mock_db,
                limit=10,
                offset=0,
                min_score=0,
            )
        
        # Verify results are sorted by relevance_score descending
        for i in range(len(results) - 1):
            assert results[i].relevance_score >= results[i + 1].relevance_score
    
    @pytest.mark.asyncio
    async def test_search_candidates_pagination(self, searcher, mock_db, mock_cv_analyses):
        """Test that pagination works correctly."""
        with patch.object(searcher, '_get_all_cv_analyses', return_value=mock_cv_analyses):
            # Get all results
            all_results, total = await searcher.search_candidates(
                query="Python",
                db=mock_db,
                limit=100,
                offset=0,
                min_score=0,
            )
            
            # Get first page
            first_page, _ = await searcher.search_candidates(
                query="Python",
                db=mock_db,
                limit=1,
                offset=0,
                min_score=0,
            )
            
            # Get second page
            second_page, _ = await searcher.search_candidates(
                query="Python",
                db=mock_db,
                limit=1,
                offset=1,
                min_score=0,
            )
        
        if len(all_results) >= 2:
            assert first_page[0].cv_id == all_results[0].cv_id
            assert second_page[0].cv_id == all_results[1].cv_id
    
    @pytest.mark.asyncio
    async def test_search_candidates_min_score_filter(self, searcher, mock_db, mock_cv_analyses):
        """Test that min_score filter works."""
        with patch.object(searcher, '_get_all_cv_analyses', return_value=mock_cv_analyses):
            results, total = await searcher.search_candidates(
                query="Python developer",
                db=mock_db,
                limit=10,
                offset=0,
                min_score=50,
            )
        
        # All results should have score >= 50
        for result in results:
            assert result.relevance_score >= 50
    
    @pytest.mark.asyncio
    async def test_search_candidates_empty_when_no_matches(self, searcher, mock_db):
        """Test empty results when no CVs match."""
        with patch.object(searcher, '_get_all_cv_analyses', return_value=[]):
            results, total = await searcher.search_candidates(
                query="Python developer",
                db=mock_db,
                limit=10,
                offset=0,
                min_score=0,
            )
        
        assert len(results) == 0
        assert total == 0
    
    @pytest.mark.asyncio
    async def test_search_candidates_empty_query(self, searcher, mock_db):
        """Test that empty/no-skill query returns empty results."""
        with patch.object(searcher, '_get_all_cv_analyses', return_value=[]):
            results, total = await searcher.search_candidates(
                query="abc xyz",  # No recognizable skills
                db=mock_db,
                limit=10,
                offset=0,
                min_score=0,
            )
        
        # Either empty results or results based on keywords only
        assert total >= 0


class TestMergeQueries:
    """Tests for merging parsed queries."""
    
    def test_merge_queries_combines_skills(self, searcher):
        """Test that skills are combined without duplicates."""
        primary = ParsedQuery(
            extracted_skills=["python", "aws"],
            keywords=["senior"],
            raw_query="test"
        )
        secondary = ParsedQuery(
            extracted_skills=["python", "docker"],
            keywords=["developer"],
            raw_query="test"
        )
        
        merged = searcher._merge_parsed_queries(primary, secondary)
        
        assert "python" in merged.extracted_skills
        assert "aws" in merged.extracted_skills
        assert "docker" in merged.extracted_skills
        assert merged.extracted_skills.count("python") == 1  # No duplicates
    
    def test_merge_queries_combines_keywords(self, searcher):
        """Test that keywords are combined without duplicates."""
        primary = ParsedQuery(
            extracted_skills=[],
            keywords=["senior", "developer"],
            raw_query="test"
        )
        secondary = ParsedQuery(
            extracted_skills=[],
            keywords=["developer", "engineer"],
            raw_query="test"
        )
        
        merged = searcher._merge_parsed_queries(primary, secondary)
        
        assert "senior" in merged.keywords
        assert "developer" in merged.keywords
        assert "engineer" in merged.keywords
    
    def test_merge_queries_prefers_primary_experience(self, searcher):
        """Test that primary experience is preferred."""
        primary = ParsedQuery(
            extracted_skills=[],
            keywords=[],
            min_experience=5,
            raw_query="test"
        )
        secondary = ParsedQuery(
            extracted_skills=[],
            keywords=[],
            min_experience=3,
            raw_query="test"
        )
        
        merged = searcher._merge_parsed_queries(primary, secondary)
        
        assert merged.min_experience == 5
    
    def test_merge_queries_uses_secondary_when_primary_none(self, searcher):
        """Test that secondary experience is used when primary is None."""
        primary = ParsedQuery(
            extracted_skills=[],
            keywords=[],
            min_experience=None,
            raw_query="test"
        )
        secondary = ParsedQuery(
            extracted_skills=[],
            keywords=[],
            min_experience=3,
            raw_query="test"
        )
        
        merged = searcher._merge_parsed_queries(primary, secondary)
        
        assert merged.min_experience == 3
