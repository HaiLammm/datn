import uuid
import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient

from app.main import app
from app.core.database import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.users.models import User
from app.modules.cv.models import CV
from app.modules.ai.models import CVAnalysis, AnalysisStatus


@pytest.fixture
def mock_user():
    """Create a mock user for testing."""
    return User(id=1, email="test@example.com", hashed_password="hashed")


@pytest.fixture
def mock_cv(mock_user):
    """Create a mock CV for testing."""
    return CV(
        id=uuid.uuid4(),
        user_id=mock_user.id,
        filename="test_cv.pdf",
        file_path="/path/to/test_cv.pdf",
        uploaded_at=datetime.utcnow(),
        is_active=True
    )


@pytest.fixture
def mock_analysis(mock_cv):
    """Create a mock CV analysis for testing."""
    return CVAnalysis(
        id=uuid.uuid4(),
        cv_id=mock_cv.id,
        status=AnalysisStatus.COMPLETED,
        ai_score=85,
        ai_summary="Experienced software engineer with strong skills.",
        ai_feedback={
            "criteria": {"completeness": 80, "experience": 90, "skills": 85, "professionalism": 75},
            "experience_breakdown": {"total_years": 5, "key_roles": ["Engineer"], "industries": ["Tech"]},
            "strengths": ["Strong technical skills", "Good communication"],
            "improvements": ["Add more projects", "Include certifications"],
            "formatting_feedback": ["Use bullet points", "Consistent formatting"],
            "ats_hints": ["Include relevant keywords", "Standard section headers"]
        },
        extracted_skills=["Python", "React", "FastAPI", "PostgreSQL"],
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )


@pytest.fixture
def mock_db_session():
    """Create a mock database session."""
    return AsyncMock()


@pytest.fixture
def test_client(mock_user, mock_db_session):
    """Create a test client with mocked dependencies."""
    app.dependency_overrides[get_db] = lambda: mock_db_session
    app.dependency_overrides[get_current_user] = lambda: mock_user

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
def unauthenticated_client(mock_db_session):
    """Create a test client without authentication."""
    app.dependency_overrides[get_db] = lambda: mock_db_session
    # Don't override get_current_user - it will raise 401

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


class TestGetCVAnalysis:
    """Tests for GET /api/v1/ai/cvs/{cv_id}/analysis endpoint."""

    def test_get_analysis_success(self, test_client, mock_db_session, mock_cv, mock_analysis):
        """Test successful retrieval of CV analysis."""
        # Mock CV ownership check
        mock_cv_result = MagicMock()
        mock_cv_result.scalar_one_or_none.return_value = mock_cv

        # Mock analysis retrieval
        mock_analysis_result = MagicMock()
        mock_analysis_result.scalar_one_or_none.return_value = mock_analysis

        mock_db_session.execute.side_effect = [mock_cv_result, mock_analysis_result]

        response = test_client.get(f"/api/v1/ai/cvs/{mock_cv.id}/analysis")

        assert response.status_code == 200
        data = response.json()
        assert data["ai_score"] == 85
        assert data["status"] == "COMPLETED"
        assert "Python" in data["extracted_skills"]
        # Check computed fields are present
        assert "experience_breakdown" in data
        assert "formatting_feedback" in data
        assert "ats_hints" in data
        assert "strengths" in data
        assert "improvements" in data
        assert "criteria_explanation" in data

    def test_get_analysis_cv_not_found(self, test_client, mock_db_session):
        """Test 404 when CV not found."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result

        response = test_client.get(f"/api/v1/ai/cvs/{uuid.uuid4()}/analysis")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_get_analysis_not_found(self, test_client, mock_db_session, mock_cv):
        """Test 404 when analysis not found for existing CV."""
        # CV exists
        mock_cv_result = MagicMock()
        mock_cv_result.scalar_one_or_none.return_value = mock_cv

        # But analysis doesn't exist
        mock_analysis_result = MagicMock()
        mock_analysis_result.scalar_one_or_none.return_value = None

        mock_db_session.execute.side_effect = [mock_cv_result, mock_analysis_result]

        response = test_client.get(f"/api/v1/ai/cvs/{mock_cv.id}/analysis")

        assert response.status_code == 404


class TestGetCVAnalysisStatus:
    """Tests for GET /api/v1/ai/cvs/{cv_id}/status endpoint."""

    def test_get_status_completed(self, test_client, mock_db_session, mock_cv):
        """Test getting COMPLETED status."""
        mock_cv_result = MagicMock()
        mock_cv_result.scalar_one_or_none.return_value = mock_cv

        mock_status_result = MagicMock()
        mock_status_result.scalar_one_or_none.return_value = AnalysisStatus.COMPLETED

        mock_db_session.execute.side_effect = [mock_cv_result, mock_status_result]

        response = test_client.get(f"/api/v1/ai/cvs/{mock_cv.id}/status")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "COMPLETED"

    def test_get_status_processing(self, test_client, mock_db_session, mock_cv):
        """Test getting PROCESSING status."""
        mock_cv_result = MagicMock()
        mock_cv_result.scalar_one_or_none.return_value = mock_cv

        mock_status_result = MagicMock()
        mock_status_result.scalar_one_or_none.return_value = AnalysisStatus.PROCESSING

        mock_db_session.execute.side_effect = [mock_cv_result, mock_status_result]

        response = test_client.get(f"/api/v1/ai/cvs/{mock_cv.id}/status")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "PROCESSING"

    def test_get_status_pending_when_no_analysis(self, test_client, mock_db_session, mock_cv):
        """Test getting PENDING status when no analysis record exists."""
        mock_cv_result = MagicMock()
        mock_cv_result.scalar_one_or_none.return_value = mock_cv

        mock_status_result = MagicMock()
        mock_status_result.scalar_one_or_none.return_value = None

        mock_db_session.execute.side_effect = [mock_cv_result, mock_status_result]

        response = test_client.get(f"/api/v1/ai/cvs/{mock_cv.id}/status")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "PENDING"
        assert data["message"] == "Analysis not started"

    def test_get_status_cv_not_found(self, test_client, mock_db_session):
        """Test 404 when CV not found."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result

        response = test_client.get(f"/api/v1/ai/cvs/{uuid.uuid4()}/status")

        assert response.status_code == 404


class TestCVListEndpoint:
    """Tests for GET /api/v1/cvs endpoint."""

    def test_list_cvs_success(self, mock_user, mock_db_session, mock_cv, mock_analysis):
        """Test successful retrieval of CV list with status (uses eager loading)."""
        from app.modules.auth.dependencies import rate_limit_cv_upload

        app.dependency_overrides[get_db] = lambda: mock_db_session
        app.dependency_overrides[get_current_user] = lambda: mock_user
        app.dependency_overrides[rate_limit_cv_upload] = lambda: mock_user

        # Set up the analyses relationship on the mock CV (eager loaded)
        mock_cv.analyses = [mock_analysis]

        # Mock single query with eager-loaded analyses
        mock_cv_result = MagicMock()
        mock_cv_result.scalars.return_value.all.return_value = [mock_cv]
        mock_db_session.execute.return_value = mock_cv_result

        with TestClient(app) as client:
            response = client.get("/api/v1/cvs")

        app.dependency_overrides.clear()

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["filename"] == "test_cv.pdf"
        assert data[0]["analysis_status"] == "COMPLETED"

    def test_list_cvs_with_pending_analysis(self, mock_user, mock_db_session, mock_cv):
        """Test CV list when analysis has no record (defaults to PENDING)."""
        from app.modules.auth.dependencies import rate_limit_cv_upload

        app.dependency_overrides[get_db] = lambda: mock_db_session
        app.dependency_overrides[get_current_user] = lambda: mock_user
        app.dependency_overrides[rate_limit_cv_upload] = lambda: mock_user

        # CV with no analyses (empty list)
        mock_cv.analyses = []

        mock_cv_result = MagicMock()
        mock_cv_result.scalars.return_value.all.return_value = [mock_cv]
        mock_db_session.execute.return_value = mock_cv_result

        with TestClient(app) as client:
            response = client.get("/api/v1/cvs")

        app.dependency_overrides.clear()

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["analysis_status"] == "PENDING"

    def test_list_cvs_empty(self, mock_user, mock_db_session):
        """Test empty CV list."""
        from app.modules.auth.dependencies import rate_limit_cv_upload

        app.dependency_overrides[get_db] = lambda: mock_db_session
        app.dependency_overrides[get_current_user] = lambda: mock_user
        app.dependency_overrides[rate_limit_cv_upload] = lambda: mock_user

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db_session.execute.return_value = mock_result

        with TestClient(app) as client:
            response = client.get("/api/v1/cvs")

        app.dependency_overrides.clear()

        assert response.status_code == 200
        data = response.json()
        assert data == []
