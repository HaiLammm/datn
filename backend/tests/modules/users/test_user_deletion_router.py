"""Integration tests for /users/me deletion endpoint."""

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
from app.modules.ai.models import CVAnalysis


@pytest.fixture
def test_user_job_seeker() -> DBUser:
    """Create a test job_seeker user."""
    user = MagicMock(spec=DBUser)
    user.id = 1
    user.email = "job_seeker@example.com"
    user.hashed_password = "hashedpassword"
    user.is_active = True
    user.role = "job_seeker"
    return user


@pytest.fixture
def test_user_recruiter() -> DBUser:
    """Create a test recruiter user."""
    user = MagicMock(spec=DBUser)
    user.id = 2
    user.email = "recruiter@example.com"
    user.hashed_password = "hashedpassword"
    user.is_active = True
    user.role = "recruiter"
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


def create_mock_cv(user_id: int, analyses: list | None = None) -> MagicMock:
    """Helper to create a mock CV with analyses."""
    cv = MagicMock(spec=CV)
    cv.id = uuid.uuid4()
    cv.user_id = user_id
    cv.file_path = "/tmp/test_cv.pdf"
    cv.analyses = analyses or []
    return cv


def create_mock_analysis(cv_id: uuid.UUID) -> MagicMock:
    """Helper to create a mock CVAnalysis."""
    analysis = MagicMock(spec=CVAnalysis)
    analysis.id = uuid.uuid4()
    analysis.cv_id = cv_id
    return analysis


class TestUserDeletionEndpoint:
    """Integration tests for DELETE /api/v1/users/me."""

    @pytest_asyncio.fixture
    async def authenticated_job_seeker_client(
        self, test_user_job_seeker: DBUser, mock_db_session: AsyncMock
    ):
        """Create authenticated async client for job_seeker."""
        # Mock user's CVs and analyses
        analysis = create_mock_analysis(uuid.uuid4())
        cvs = [create_mock_cv(test_user_job_seeker.id, [analysis])]

        # Mock the select query
        mock_select_result = MagicMock()
        mock_select_result.scalars.return_value.all.return_value = cvs
        mock_db_session.execute.return_value = mock_select_result

        app.dependency_overrides[get_db] = lambda: mock_db_session
        app.dependency_overrides[get_current_user] = lambda: test_user_job_seeker

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            yield ac

        app.dependency_overrides.clear()

    @pytest_asyncio.fixture
    async def authenticated_recruiter_client(
        self, test_user_recruiter: DBUser, mock_db_session: AsyncMock
    ):
        """Create authenticated async client for recruiter."""
        # Mock user's CVs and analyses
        analysis = create_mock_analysis(uuid.uuid4())
        cvs = [create_mock_cv(test_user_recruiter.id, [analysis])]

        mock_select_result = MagicMock()
        mock_select_result.scalars.return_value.all.return_value = cvs
        mock_db_session.execute.return_value = mock_select_result

        app.dependency_overrides[get_db] = lambda: mock_db_session
        app.dependency_overrides[get_current_user] = lambda: test_user_recruiter

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
    async def test_returns_204_for_authenticated_job_seeker(
        self, authenticated_job_seeker_client: AsyncClient
    ):
        """Test: Returns 204 for authenticated job_seeker."""
        with patch("os.path.exists", return_value=False):  # No files to delete
            response = await authenticated_job_seeker_client.delete("/api/v1/users/me")

        assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_returns_204_for_authenticated_recruiter(
        self, authenticated_recruiter_client: AsyncClient
    ):
        """Test: Returns 204 for authenticated recruiter."""
        with patch("os.path.exists", return_value=False):
            response = await authenticated_recruiter_client.delete("/api/v1/users/me")

        assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_returns_401_for_unauthenticated_request(
        self, unauthenticated_client: AsyncClient
    ):
        """Test: Returns 401 for unauthenticated request."""
        response = await unauthenticated_client.delete("/api/v1/users/me")

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_calls_delete_user_account_with_correct_user_id(
        self, authenticated_job_seeker_client: AsyncClient, mock_db_session: AsyncMock
    ):
        """Test: Calls delete_user_account service with correct user ID."""
        with patch("app.modules.users.services.delete_user_account") as mock_delete, \
             patch("os.path.exists", return_value=False):
            
            response = await authenticated_job_seeker_client.delete("/api/v1/users/me")

            assert response.status_code == 204
            mock_delete.assert_called_once_with(mock_db_session, 1)  # user.id = 1

