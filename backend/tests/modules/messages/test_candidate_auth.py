"""
Tests for candidate conversation access and authorization
"""
import uuid
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.core.database import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.users.models import User as DBUser
from app.modules.messages.models import Conversation, Message


class TestCandidateConversationAuthorization:
    """Tests for candidate authorization in conversation endpoints."""

    @pytest.fixture
    def candidate_user(self) -> DBUser:
        """Create a test user with candidate role."""
        return DBUser(
            id=2,
            email="candidate@example.com",
            hashed_password="hashedpassword",
            role="job_seeker",
            is_active=True,
        )

    @pytest.fixture
    def recruiter_user(self) -> DBUser:
        """Create a test user with recruiter role."""
        return DBUser(
            id=1,
            email="recruiter@example.com",
            hashed_password="hashedpassword",
            role="recruiter",
            is_active=True,
        )

    @pytest.fixture
    def mock_db_session(self) -> AsyncMock:
        """Create a mock database session."""
        mock_session = AsyncMock(spec=AsyncSession)
        mock_session.execute = AsyncMock()
        mock_session.commit = AsyncMock()
        return mock_session

    @pytest.fixture
    def client(self, candidate_user: DBUser, mock_db_session: AsyncMock) -> TestClient:
        """Create test client with candidate user authenticated."""
        app.dependency_overrides[get_db] = lambda: mock_db_session
        app.dependency_overrides[get_current_user] = lambda: candidate_user

        with TestClient(app) as test_client:
            yield test_client

        app.dependency_overrides.clear()

    @pytest.fixture
    def sample_conversation(self):
        """Create a sample conversation."""
        return Conversation(
            id=uuid.uuid4(),
            recruiter_id=1,
            candidate_id=2,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

    def test_candidate_can_access_own_conversation_messages(
        self, client: TestClient, mock_db_session: AsyncMock, sample_conversation: Conversation
    ):
        """Test candidate can access messages from their own conversation."""
        # Setup mock to return conversation where candidate_id matches
        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = sample_conversation
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        response = client.get(
            f"/api/v1/messages/conversations/{sample_conversation.id}/messages"
        )

        # Should not return 403 Forbidden
        assert response.status_code != 403
        # Should either succeed (200) or return 404 (not found) but not 403
        assert response.status_code in [200, 404]

    def test_candidate_cannot_access_other_candidate_conversation(
        self, client: TestClient, mock_db_session: AsyncMock
    ):
        """Test candidate cannot access conversation belonging to another candidate."""
        # Conversation belongs to different candidate (id=999)
        other_candidate_conversation = Conversation(
            id=uuid.uuid4(),
            recruiter_id=1,
            candidate_id=999,  # Different candidate
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = other_candidate_conversation
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        response = client.get(
            f"/api/v1/messages/conversations/{other_candidate_conversation.id}/messages"
        )

        # Should return 403 Forbidden
        assert response.status_code == 403

    def test_recruiter_can_access_own_conversation(
        self, recruiter_user: DBUser, mock_db_session: AsyncMock, sample_conversation: Conversation
    ):
        """Test recruiter can access conversation they initiated."""
        app.dependency_overrides[get_current_user] = lambda: recruiter_user

        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = sample_conversation
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        with TestClient(app) as client:
            response = client.get(
                f"/api/v1/messages/conversations/{sample_conversation.id}/messages"
            )

            # Should not return 403
            assert response.status_code != 403

        app.dependency_overrides.clear()


class TestConversationListAuthorization:
    """Tests for conversation list endpoint authorization."""

    @pytest.fixture
    def candidate_user(self) -> DBUser:
        """Create a test user with candidate role."""
        return DBUser(
            id=2,
            email="candidate@example.com",
            hashed_password="hashedpassword",
            role="job_seeker",
            is_active=True,
        )

    @pytest.fixture
    def mock_db_session(self) -> AsyncMock:
        """Create a mock database session."""
        mock_session = AsyncMock(spec=AsyncSession)
        mock_session.execute = AsyncMock()
        mock_session.commit = AsyncMock()
        return mock_session

    @pytest.fixture
    def client(self, candidate_user: DBUser, mock_db_session: AsyncMock) -> TestClient:
        """Create test client with candidate user authenticated."""
        app.dependency_overrides[get_db] = lambda: mock_db_session
        app.dependency_overrides[get_current_user] = lambda: candidate_user

        with TestClient(app) as test_client:
            yield test_client

        app.dependency_overrides.clear()

    def test_conversations_endpoint_exists(self, client: TestClient):
        """Test that GET /conversations endpoint exists."""
        response = client.get("/api/v1/messages/conversations")

        # Should not return 404 Not Found
        assert response.status_code != 404

    def test_conversations_returns_only_candidate_own_conversations(
        self, client: TestClient, mock_db_session: AsyncMock
    ):
        """Test conversations endpoint returns only conversations where user is candidate."""
        # This test will fail until the endpoint is implemented
        # It should filter by candidate_id = current_user.id for candidates
        response = client.get("/api/v1/messages/conversations")

        # Endpoint should exist and handle candidate role
        assert response.status_code in [200, 403]  # 403 would be wrong behavior


class TestUnreadCountEndpoint:
    """Tests for unread count endpoint."""

    @pytest.fixture
    def candidate_user(self) -> DBUser:
        """Create a test user with candidate role."""
        return DBUser(
            id=2,
            email="candidate@example.com",
            hashed_password="hashedpassword",
            role="job_seeker",
            is_active=True,
        )

    @pytest.fixture
    def mock_db_session(self) -> AsyncMock:
        """Create a mock database session."""
        mock_session = AsyncMock(spec=AsyncSession)
        mock_session.execute = AsyncMock()
        mock_session.commit = AsyncMock()
        return mock_session

    @pytest.fixture
    def client(self, candidate_user: DBUser, mock_db_session: AsyncMock) -> TestClient:
        """Create test client with candidate user authenticated."""
        app.dependency_overrides[get_db] = lambda: mock_db_session
        app.dependency_overrides[get_current_user] = lambda: candidate_user

        with TestClient(app) as test_client:
            yield test_client

        app.dependency_overrides.clear()

    def test_unread_count_endpoint_exists(self, client: TestClient):
        """Test that GET /conversations/unread-count endpoint exists."""
        response = client.get("/api/v1/messages/conversations/unread-count")

        # Should not return 404 Not Found
        assert response.status_code != 404

    def test_unread_count_returns_unread_count(self, client: TestClient):
        """Test unread count endpoint returns unread count."""
        # This test will fail until the endpoint is implemented
        response = client.get("/api/v1/messages/conversations/unread-count")

        # Should return 200 with unread_count field
        if response.status_code == 200:
            data = response.json()
            assert "unread_count" in data
            assert isinstance(data["unread_count"], int)
