import pytest
import pytest_asyncio
import uuid
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone
from typing import AsyncGenerator

from httpx import AsyncClient, ASGITransport
from app.main import app
from app.modules.users.models import User as DBUser
from app.core.database import get_db
from app.modules.auth.dependencies import (
    get_current_user,
    require_job_seeker,
    rate_limit_cv_upload,
)

# --- Fixtures ---

@pytest.fixture
def test_job_seeker() -> DBUser:
    """Create a test user with job_seeker role."""
    return DBUser(
        id=2,
        email="seeker@example.com",
        hashed_password="hashedpassword",
        role="job_seeker",
        is_active=True,
    )

@pytest_asyncio.fixture
async def job_seeker_client(test_job_seeker: DBUser, mock_db_session: AsyncMock) -> AsyncGenerator[AsyncClient, None]:
    """
    Async client authenticated as a job seeker.
    Overrides dependencies to return the job seeker user.
    """
    app.dependency_overrides[get_db] = lambda: mock_db_session
    app.dependency_overrides[get_current_user] = lambda: test_job_seeker
    app.dependency_overrides[require_job_seeker] = lambda: test_job_seeker
    app.dependency_overrides[rate_limit_cv_upload] = lambda: test_job_seeker

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
def mock_application():
    """Create a mock Application object."""
    mock_app = MagicMock()
    mock_app.id = uuid.uuid4()
    mock_app.job_id = uuid.uuid4()
    mock_app.user_id = 2  # Match test_job_seeker id
    mock_app.cv_id = uuid.uuid4()
    mock_app.cover_letter = "I am interested."
    mock_app.status = "pending"
    mock_app.created_at = datetime.now(timezone.utc)
    mock_app.updated_at = datetime.now(timezone.utc)
    return mock_app


# --- Tests ---

class TestApplyJobEndpoint:
    """Tests for POST /api/v1/jobs/{job_id}/apply endpoint."""

    @pytest.mark.asyncio
    async def test_apply_job_success(
        self, job_seeker_client: AsyncClient, mock_application
    ):
        """Test successful job application."""
        job_id = mock_application.job_id
        cv_id = mock_application.cv_id

        with patch(
            "app.modules.jobs.router.job_service.create_application",
            new_callable=AsyncMock,
            return_value=mock_application,
        ) as mock_create_app:
            response = await job_seeker_client.post(
                f"/api/v1/jobs/{job_id}/apply",
                json={
                    "cv_id": str(cv_id),
                    "cover_letter": "I am interested.",
                },
            )

            assert response.status_code == 201
            data = response.json()
            assert data["id"] == str(mock_application.id)
            assert data["status"] == "pending"
            assert data["cover_letter"] == "I am interested."
            
            mock_create_app.assert_called_once()
            call_kwargs = mock_create_app.call_args.kwargs
            assert str(call_kwargs["job_id"]) == str(job_id)
            assert str(call_kwargs["cv_id"]) == str(cv_id)
            assert call_kwargs["user_id"] == 2  # job seeker id

    @pytest.mark.asyncio
    async def test_apply_job_duplicate(
        self, job_seeker_client: AsyncClient
    ):
        """Test application fails if already applied (duplicate)."""
        job_id = uuid.uuid4()
        cv_id = uuid.uuid4()

        with patch(
            "app.modules.jobs.router.job_service.create_application",
            new_callable=AsyncMock,
            side_effect=ValueError("You have already applied to this job"),
        ):
            response = await job_seeker_client.post(
                f"/api/v1/jobs/{job_id}/apply",
                json={
                    "cv_id": str(cv_id),
                },
            )

            assert response.status_code == 400
            data = response.json()
            assert data["detail"] == "You have already applied to this job"

    @pytest.mark.asyncio
    async def test_apply_job_invalid_cv(
        self, job_seeker_client: AsyncClient
    ):
        """Test application fails if CV does not exist or belong to user."""
        job_id = uuid.uuid4()
        cv_id = uuid.uuid4()

        with patch(
            "app.modules.jobs.router.job_service.create_application",
            new_callable=AsyncMock,
            side_effect=ValueError("CV not found or does not belong to user"),
        ):
            response = await job_seeker_client.post(
                f"/api/v1/jobs/{job_id}/apply",
                json={
                    "cv_id": str(cv_id),
                },
            )

            assert response.status_code == 400
            data = response.json()
            assert data["detail"] == "CV not found or does not belong to user"

    @pytest.mark.asyncio
    async def test_apply_job_job_not_found(
        self, job_seeker_client: AsyncClient
    ):
        """Test application fails if Job not found."""
        job_id = uuid.uuid4()
        cv_id = uuid.uuid4()

        with patch(
            "app.modules.jobs.router.job_service.create_application",
            new_callable=AsyncMock,
            side_effect=ValueError("Job not found"),
        ):
            response = await job_seeker_client.post(
                f"/api/v1/jobs/{job_id}/apply",
                json={
                    "cv_id": str(cv_id),
                },
            )

            assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_apply_job_unauthenticated(
        self, unauthenticated_async_client: AsyncClient
    ):
        """Test unauthenticated application fails."""
        job_id = uuid.uuid4()
        cv_id = uuid.uuid4()

        response = await unauthenticated_async_client.post(
            f"/api/v1/jobs/{job_id}/apply",
            json={
                "cv_id": str(cv_id),
            },
        )
        assert response.status_code in [401, 403]


class TestGetJobDetailEndpoint:
    """Tests for GET /api/v1/jobs/{job_id} endpoint (Public Access)."""

    @pytest.mark.asyncio
    async def test_get_job_detail_success(
        self, unauthenticated_async_client: AsyncClient
    ):
        """Test getting job detail functionality."""
        job_id = uuid.uuid4()
        mock_jd = MagicMock()
        mock_jd.id = job_id
        mock_jd.title = "Frontend Engineer"
        mock_jd.description = "React specialist needed"
        mock_jd.uploaded_at = datetime.utcnow()
        mock_jd.is_active = True
        mock_jd.location_type = "remote"
        # Add attributes required by JobDescriptionResponse
        mock_jd.user_id = 99
        mock_jd.required_skills = ["React"]
        mock_jd.min_experience_years = 2
        mock_jd.salary_min = 500
        mock_jd.salary_max = 1000
        mock_jd.parse_status = "completed"
        mock_jd.parsed_requirements = None

        with patch(
            "app.modules.jobs.router.job_service.get_public_job",
            new_callable=AsyncMock,
            return_value=mock_jd,
        ):
            response = await unauthenticated_async_client.get(f"/api/v1/jobs/{job_id}")

            assert response.status_code == 200
            data = response.json()
            assert data["id"] == str(job_id)
            assert data["title"] == "Frontend Engineer"

    @pytest.mark.asyncio
    async def test_get_job_detail_not_found(
        self, unauthenticated_async_client: AsyncClient
    ):
        """Test failure when job not found."""
        job_id = uuid.uuid4()

        with patch(
            "app.modules.jobs.router.job_service.get_public_job",
            new_callable=AsyncMock,
            return_value=None,
        ):
            response = await unauthenticated_async_client.get(f"/api/v1/jobs/{job_id}")

            assert response.status_code == 404
