from typing import AsyncGenerator
import uuid
import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.main import app
from app.modules.auth.dependencies import get_current_user
from app.modules.users.models import User as DBUser
from app.modules.cv.models import CV


# Fixture to provide a test user
@pytest.fixture(scope="session")
def test_user() -> DBUser:
    return DBUser(
        id=1,  # User.id is Integer, not UUID
        email="test@example.com",
        hashed_password="hashedpassword",
    )


# Mock database session fixture
@pytest.fixture
def mock_db_session() -> AsyncMock:
    """Create a mock database session."""
    mock_session = AsyncMock(spec=AsyncSession)
    mock_session.execute = AsyncMock()
    mock_session.commit = AsyncMock()
    mock_session.rollback = AsyncMock()
    mock_session.close = AsyncMock()
    return mock_session


# Fixture for the sync HTTP client (TestClient) - uses mocked DB
@pytest.fixture
def client(test_user: DBUser, mock_db_session: AsyncMock) -> TestClient:
    from app.modules.auth.dependencies import rate_limit_cv_upload

    app.dependency_overrides[get_db] = lambda: mock_db_session
    app.dependency_overrides[get_current_user] = lambda: test_user
    app.dependency_overrides[rate_limit_cv_upload] = lambda: test_user
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


# Fixture for async HTTP client (authenticated)
@pytest_asyncio.fixture
async def async_client(test_user: DBUser, mock_db_session: AsyncMock) -> AsyncGenerator[AsyncClient, None]:
    from app.modules.auth.dependencies import rate_limit_cv_upload

    app.dependency_overrides[get_db] = lambda: mock_db_session
    app.dependency_overrides[get_current_user] = lambda: test_user
    app.dependency_overrides[rate_limit_cv_upload] = lambda: test_user
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


# Fixture for async HTTP client (unauthenticated)
@pytest_asyncio.fixture
async def unauthenticated_async_client(mock_db_session: AsyncMock) -> AsyncGenerator[AsyncClient, None]:
    # Only override DB, not auth - so requests will be unauthenticated
    app.dependency_overrides[get_db] = lambda: mock_db_session
    # Remove any auth overrides
    app.dependency_overrides.pop(get_current_user, None)
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


# Fixture to create test user and CV
@pytest.fixture
def create_test_user_and_cv(test_user: DBUser):
    """Create a test user and CV for testing."""
    test_cv = CV(
        id=uuid.uuid4(),
        user_id=test_user.id,  # Now an int
        filename="test_cv.pdf",
        file_path="/tmp/test_cv.pdf",
        uploaded_at=datetime.now(timezone.utc),
        is_active=True,
    )
    return test_user, test_cv