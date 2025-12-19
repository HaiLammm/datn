"""Unit tests for get_user_stats service function."""

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.modules.ai.models import AnalysisStatus, CVAnalysis
from app.modules.cv.models import CV
from app.modules.users.services import get_user_stats


@pytest.fixture
def mock_db():
    """Create a mock async database session."""
    return AsyncMock()


def create_mock_cv(user_id: int, analyses: list) -> MagicMock:
    """Helper to create a mock CV with analyses."""
    cv = MagicMock(spec=CV)
    cv.id = uuid.uuid4()
    cv.user_id = user_id
    cv.is_active = True
    cv.analyses = analyses
    return cv


def create_mock_analysis(
    status: AnalysisStatus,
    ai_score: int | None = None,
    extracted_skills: list[str] | None = None,
) -> MagicMock:
    """Helper to create a mock CVAnalysis."""
    analysis = MagicMock(spec=CVAnalysis)
    analysis.status = status
    analysis.ai_score = ai_score
    analysis.extracted_skills = extracted_skills
    return analysis


class TestGetUserStats:
    """Tests for get_user_stats service function."""

    @pytest.mark.asyncio
    async def test_returns_correct_total_cvs_count(self, mock_db: AsyncMock):
        """Test: Returns correct total CVs count."""
        user_id = 1
        cvs = [
            create_mock_cv(user_id, []),
            create_mock_cv(user_id, []),
            create_mock_cv(user_id, []),
        ]

        # Mock the execute result
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = cvs
        mock_db.execute.return_value = mock_result

        stats = await get_user_stats(mock_db, user_id)

        assert stats["total_cvs"] == 3

    @pytest.mark.asyncio
    async def test_calculates_average_score_correctly(self, mock_db: AsyncMock):
        """Test: Calculates average score correctly (only COMPLETED analyses)."""
        user_id = 1
        analyses = [
            create_mock_analysis(AnalysisStatus.COMPLETED, ai_score=80),
            create_mock_analysis(AnalysisStatus.COMPLETED, ai_score=90),
            create_mock_analysis(AnalysisStatus.PENDING, ai_score=None),  # Ignored
        ]
        cvs = [create_mock_cv(user_id, analyses)]

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = cvs
        mock_db.execute.return_value = mock_result

        stats = await get_user_stats(mock_db, user_id)

        # Average of 80 and 90 = 85.0
        assert stats["average_score"] == 85.0

    @pytest.mark.asyncio
    async def test_returns_best_score_correctly(self, mock_db: AsyncMock):
        """Test: Returns best (max) score correctly."""
        user_id = 1
        analyses = [
            create_mock_analysis(AnalysisStatus.COMPLETED, ai_score=70),
            create_mock_analysis(AnalysisStatus.COMPLETED, ai_score=95),
            create_mock_analysis(AnalysisStatus.COMPLETED, ai_score=82),
        ]
        cvs = [create_mock_cv(user_id, analyses)]

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = cvs
        mock_db.execute.return_value = mock_result

        stats = await get_user_stats(mock_db, user_id)

        assert stats["best_score"] == 95

    @pytest.mark.asyncio
    async def test_aggregates_unique_skills_correctly(self, mock_db: AsyncMock):
        """Test: Aggregates unique skills correctly across all CVs."""
        user_id = 1
        analyses1 = [
            create_mock_analysis(
                AnalysisStatus.COMPLETED, ai_score=80, extracted_skills=["Python", "SQL"]
            ),
        ]
        analyses2 = [
            create_mock_analysis(
                AnalysisStatus.COMPLETED, ai_score=85, extracted_skills=["Python", "JavaScript"]
            ),
        ]
        cvs = [
            create_mock_cv(user_id, analyses1),
            create_mock_cv(user_id, analyses2),
        ]

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = cvs
        mock_db.execute.return_value = mock_result

        stats = await get_user_stats(mock_db, user_id)

        # Unique skills: Python, SQL, JavaScript = 3
        assert stats["total_unique_skills"] == 3

    @pytest.mark.asyncio
    async def test_returns_top_5_skills_by_frequency(self, mock_db: AsyncMock):
        """Test: Returns top 5 skills by frequency (not alphabetically)."""
        user_id = 1
        # Create skills with different frequencies
        skills = [
            "Python",  # appears 4 times
            "Python",
            "Python",
            "Python",
            "JavaScript",  # appears 3 times
            "JavaScript",
            "JavaScript",
            "SQL",  # appears 2 times
            "SQL",
            "React",  # appears 1 time
            "Docker",  # appears 1 time
            "AWS",  # appears 1 time (should be 6th, excluded)
        ]
        analyses = [
            create_mock_analysis(
                AnalysisStatus.COMPLETED, ai_score=80, extracted_skills=skills
            ),
        ]
        cvs = [create_mock_cv(user_id, analyses)]

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = cvs
        mock_db.execute.return_value = mock_result

        stats = await get_user_stats(mock_db, user_id)

        # Top 5 by frequency: Python(4), JavaScript(3), SQL(2), then any of React/Docker/AWS
        assert len(stats["top_skills"]) == 5
        assert stats["top_skills"][0] == "Python"
        assert stats["top_skills"][1] == "JavaScript"
        assert stats["top_skills"][2] == "SQL"
        # The remaining two could be any of React, Docker, AWS (same frequency)

    @pytest.mark.asyncio
    async def test_handles_user_with_no_cvs(self, mock_db: AsyncMock):
        """Test: Handles user with no CVs (returns zeros/empty)."""
        user_id = 1
        cvs = []  # No CVs

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = cvs
        mock_db.execute.return_value = mock_result

        stats = await get_user_stats(mock_db, user_id)

        assert stats["total_cvs"] == 0
        assert stats["average_score"] is None
        assert stats["best_score"] is None
        assert stats["total_unique_skills"] == 0
        assert stats["top_skills"] == []

    @pytest.mark.asyncio
    async def test_handles_cvs_with_no_completed_analyses(self, mock_db: AsyncMock):
        """Test: Handles user with CVs but no completed analyses."""
        user_id = 1
        analyses = [
            create_mock_analysis(AnalysisStatus.PENDING, ai_score=None),
            create_mock_analysis(AnalysisStatus.PROCESSING, ai_score=None),
            create_mock_analysis(AnalysisStatus.FAILED, ai_score=None),
        ]
        cvs = [create_mock_cv(user_id, analyses)]

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = cvs
        mock_db.execute.return_value = mock_result

        stats = await get_user_stats(mock_db, user_id)

        assert stats["total_cvs"] == 1
        assert stats["average_score"] is None
        assert stats["best_score"] is None
        assert stats["total_unique_skills"] == 0
        assert stats["top_skills"] == []

    @pytest.mark.asyncio
    async def test_handles_cvs_with_null_extracted_skills(self, mock_db: AsyncMock):
        """Test: Handles CVs with null extracted_skills gracefully."""
        user_id = 1
        analyses = [
            create_mock_analysis(
                AnalysisStatus.COMPLETED, ai_score=85, extracted_skills=None
            ),
            create_mock_analysis(
                AnalysisStatus.COMPLETED, ai_score=75, extracted_skills=["Python"]
            ),
        ]
        cvs = [create_mock_cv(user_id, analyses)]

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = cvs
        mock_db.execute.return_value = mock_result

        stats = await get_user_stats(mock_db, user_id)

        # Should handle null gracefully and still count Python
        assert stats["average_score"] == 80.0
        assert stats["best_score"] == 85
        assert stats["total_unique_skills"] == 1
        assert stats["top_skills"] == ["Python"]

    @pytest.mark.asyncio
    async def test_rounds_average_to_one_decimal(self, mock_db: AsyncMock):
        """Test: Average score is rounded to 1 decimal place."""
        user_id = 1
        analyses = [
            create_mock_analysis(AnalysisStatus.COMPLETED, ai_score=82),
            create_mock_analysis(AnalysisStatus.COMPLETED, ai_score=77),
            create_mock_analysis(AnalysisStatus.COMPLETED, ai_score=91),
        ]
        cvs = [create_mock_cv(user_id, analyses)]

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = cvs
        mock_db.execute.return_value = mock_result

        stats = await get_user_stats(mock_db, user_id)

        # (82 + 77 + 91) / 3 = 83.333... -> rounded to 83.3
        assert stats["average_score"] == 83.3
