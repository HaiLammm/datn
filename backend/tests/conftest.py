from typing import AsyncGenerator
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.core.database import Base, get_db
from app.main import app
from app.modules.auth.dependencies import get_current_user
from app.modules.users.models import User as DBUser  # Import User model

# Create a test database URL
TEST_DATABASE_URL = f"postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/test_{settings.DB_NAME}"

# Create a test engine
test_engine = create_async_engine(TEST_DATABASE_URL, echo=True)

# Create a test session local
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=test_engine, class_=AsyncSession
)


@pytest_asyncio.fixture(scope="session")
async def setup_test_db_session():
    # Drop and create tables before the session starts
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    # No need to drop tables again if we drop and create at the beginning of the session.


# Fixture to provide a test user
@pytest.fixture(scope="session")
def test_user() -> DBUser:
    return DBUser(
        id="00000000-0000-0000-0000-000000000001",
        email="test@example.com",
        hashed_password="hashedpassword",
    )


# Fixture to override get_db dependency to use a test session with transaction
@pytest_asyncio.fixture(scope="module")
async def override_get_db(setup_test_db_session) -> AsyncGenerator[AsyncSession, None]:
    async with TestingSessionLocal() as session:
        # Begin a transaction and roll it back after each test
        async with session.begin():
            yield session


# Fixture for the async HTTP client
@pytest_asyncio.fixture(scope="module")
async def client(
    override_get_db: AsyncSession, test_user: DBUser
) -> AsyncGenerator[TestClient, None]:
    from app.modules.auth.dependencies import rate_limit_cv_upload

    app.dependency_overrides[get_db] = lambda: override_get_db
    app.dependency_overrides[get_current_user] = lambda: test_user # Override current user
    app.dependency_overrides[rate_limit_cv_upload] = lambda: test_user # Override rate limiting
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()