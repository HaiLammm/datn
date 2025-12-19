"""Integration tests for /users/me/stats endpoint."""

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from app.core.database import get_db
from app.main import app
from app.modules.auth.dependencies import get_current_user
from app.modules.users.models import User as DBUser
from app.modules.cv.models import CV
from app.modules.ai.models import AnalysisStatus, CVAnalysis


@pytest.fixture
def test_user() -> DBUser:
    """Create a test user."""
    user = MagicMock(spec=DBUser)
    user.id = 1
    user.email = "test@example.com"
    user.hashed_password = "hashedpassword"
    user.is_active = True
    user.role = "job_seeker"
    return user


@pytest.fixture
def mock_db_session() -> AsyncMock:
    """Create a mock database session."""
    mock_session = AsyncMock()
    mock_session.execute = AsyncMock()
    mock_session.commit = AsyncMock()
    mock_session.rollback = AsyncMock()
    mock_session.close = AsyncMock()
    return mock_session


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


class TestUserStatsEndpoint:
    """Integration tests for GET /api/v1/users/me/stats."""

    @pytest_asyncio.fixture
    async def authenticated_client(
        self, test_user: DBUser, mock_db_session: AsyncMock
    ):
        """Create authenticated async client."""
        # Mock CVs with analyses
        analyses = [
            create_mock_analysis(
                AnalysisStatus.COMPLETED, ai_score=85, extracted_skills=["Python", "SQL"]
            ),
        ]
        cvs = [create_mock_cv(test_user.id, analyses)]

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = cvs
        mock_db_session.execute.return_value = mock_result

        app.dependency_overrides[get_db] = lambda: mock_db_session
        app.dependency_overrides[get_current_user] = lambda: test_user

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            yield ac

        app.dependency_overrides.clear()

    @pytest_asyncio.fixture
    async def unauthenticated_client(self, mock_db_session: AsyncMock):
        """Create unauthenticated async client."""
        app.dependency_overrides[get_db] = lambda: mock_db_session
        # Remove auth override so requests are unauthenticated
        app.dependency_overrides.pop(get_current_user, None)

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            yield ac

        app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_returns_200_for_authenticated_user(
        self, authenticated_client: AsyncClient
    ):
        """Test: Returns 200 with valid stats for authenticated user."""
        response = await authenticated_client.get("/api/v1/users/me/stats")

        assert response.status_code == 200
        data = response.json()
        assert "total_cvs" in data
        assert "average_score" in data
        assert "best_score" in data
        assert "total_unique_skills" in data
        assert "top_skills" in data

    @pytest.mark.asyncio
    async def test_returns_401_for_unauthenticated_request(
        self, unauthenticated_client: AsyncClient
    ):
        """Test: Returns 401 for unauthenticated request."""
        response = await unauthenticated_client.get("/api/v1/users/me/stats")

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_response_matches_schema(self, authenticated_client: AsyncClient):
        """Test: Returns correct data structure (schema validation)."""
        response = await authenticated_client.get("/api/v1/users/me/stats")

        assert response.status_code == 200
        data = response.json()

        # Validate types
        assert isinstance(data["total_cvs"], int)
        assert data["average_score"] is None or isinstance(data["average_score"], (int, float))
        assert data["best_score"] is None or isinstance(data["best_score"], int)
        assert isinstance(data["total_unique_skills"], int)
        assert isinstance(data["top_skills"], list)
        assert all(isinstance(skill, str) for skill in data["top_skills"])

    @pytest.mark.asyncio
    async def test_returns_stats_for_user_with_cvs(
        self, authenticated_client: AsyncClient
    ):
        """Test: Returns proper stats for user with CVs and completed analyses."""
        response = await authenticated_client.get("/api/v1/users/me/stats")

        assert response.status_code == 200
        data = response.json()

        # Based on our mock setup (1 CV, score 85, skills Python & SQL)
        assert data["total_cvs"] == 1
        assert data["average_score"] == 85.0
        assert data["best_score"] == 85
        assert data["total_unique_skills"] == 2
        assert set(data["top_skills"]) == {"Python", "SQL"}


class TestUserStatsEndpointEmptyUser:
    """Tests for new user with no CVs."""

    @pytest_asyncio.fixture
    async def new_user_client(self, test_user: DBUser, mock_db_session: AsyncMock):
        """Create client for user with no CVs."""
        # Mock empty CVs list
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db_session.execute.return_value = mock_result

        app.dependency_overrides[get_db] = lambda: mock_db_session
        app.dependency_overrides[get_current_user] = lambda: test_user

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            yield ac

        app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_returns_empty_stats_for_new_user(
        self, new_user_client: AsyncClient
    ):
        """Test: Returns empty stats structure for new user (no CVs)."""
        response = await new_user_client.get("/api/v1/users/me/stats")

        assert response.status_code == 200
        data = response.json()

        assert data["total_cvs"] == 0
        assert data["average_score"] is None
        assert data["best_score"] is None
        assert data["total_unique_skills"] == 0
        assert data["top_skills"] == []
