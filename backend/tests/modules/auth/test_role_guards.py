"""
Tests for Role-Based Access Control (RBAC) dependencies.

These tests verify that the role guard dependencies correctly enforce
role-based access control on API endpoints.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.core.database import get_db
from app.modules.auth.dependencies import (
    get_current_user,
    get_current_active_user,
    require_role,
    require_admin,
    require_job_seeker,
    require_recruiter,
)
from app.modules.users.models import User as DBUser


# ============================================================================
# Fixtures for different user roles
# ============================================================================

@pytest.fixture
def admin_user() -> DBUser:
    """Create an admin user for testing."""
    user = DBUser(
        id=1,
        email="admin@example.com",
        hashed_password="hashedpassword",
        role="admin",
        is_active=True,
    )
    return user


@pytest.fixture
def job_seeker_user() -> DBUser:
    """Create a job seeker user for testing."""
    user = DBUser(
        id=2,
        email="jobseeker@example.com",
        hashed_password="hashedpassword",
        role="job_seeker",
        is_active=True,
    )
    return user


@pytest.fixture
def recruiter_user() -> DBUser:
    """Create a recruiter user for testing."""
    user = DBUser(
        id=3,
        email="recruiter@example.com",
        hashed_password="hashedpassword",
        role="recruiter",
        is_active=True,
    )
    return user


@pytest.fixture
def inactive_user() -> DBUser:
    """Create an inactive user for testing."""
    user = DBUser(
        id=4,
        email="inactive@example.com",
        hashed_password="hashedpassword",
        role="job_seeker",
        is_active=False,
    )
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


# ============================================================================
# Test require_role factory function
# ============================================================================

class TestRequireRoleFactory:
    """Tests for the require_role factory function."""
    
    @pytest.mark.asyncio
    async def test_require_role_allows_matching_role(self, job_seeker_user: DBUser):
        """Test that require_role allows a user with a matching role."""
        role_guard = require_role(['job_seeker'])
        
        # Mock get_current_active_user to return our test user
        with patch('app.modules.auth.dependencies.get_current_active_user') as mock_get_user:
            # The role_guard calls get_current_active_user as a dependency
            # We need to test the guard function directly
            result = await role_guard(current_user=job_seeker_user)
            assert result == job_seeker_user
    
    @pytest.mark.asyncio
    async def test_require_role_denies_non_matching_role(self, recruiter_user: DBUser):
        """Test that require_role denies a user with a non-matching role."""
        role_guard = require_role(['job_seeker'])
        
        with pytest.raises(HTTPException) as exc_info:
            await role_guard(current_user=recruiter_user)
        
        assert exc_info.value.status_code == 403
        assert "Access denied" in str(exc_info.value.detail)
        assert "job_seeker" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_require_role_allows_admin_bypass(self, admin_user: DBUser):
        """Test that admin users bypass all role checks."""
        # Even if admin is not in allowed_roles, admin should pass
        role_guard = require_role(['job_seeker'])
        
        result = await role_guard(current_user=admin_user)
        assert result == admin_user
    
    @pytest.mark.asyncio
    async def test_require_role_allows_multiple_roles(self, recruiter_user: DBUser):
        """Test that require_role allows any of multiple specified roles."""
        role_guard = require_role(['job_seeker', 'recruiter'])
        
        result = await role_guard(current_user=recruiter_user)
        assert result == recruiter_user


# ============================================================================
# Test pre-built role guards
# ============================================================================

class TestRequireAdmin:
    """Tests for the require_admin dependency."""
    
    @pytest.mark.asyncio
    async def test_require_admin_allows_admin(self, admin_user: DBUser):
        """Test that require_admin allows admin users."""
        result = await require_admin(current_user=admin_user)
        assert result == admin_user
    
    @pytest.mark.asyncio
    async def test_require_admin_denies_job_seeker(self, job_seeker_user: DBUser):
        """Test that require_admin denies job_seeker users."""
        with pytest.raises(HTTPException) as exc_info:
            await require_admin(current_user=job_seeker_user)
        
        assert exc_info.value.status_code == 403
        assert "Access denied" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_require_admin_denies_recruiter(self, recruiter_user: DBUser):
        """Test that require_admin denies recruiter users."""
        with pytest.raises(HTTPException) as exc_info:
            await require_admin(current_user=recruiter_user)
        
        assert exc_info.value.status_code == 403


class TestRequireJobSeeker:
    """Tests for the require_job_seeker dependency."""
    
    @pytest.mark.asyncio
    async def test_require_job_seeker_allows_job_seeker(self, job_seeker_user: DBUser):
        """Test that require_job_seeker allows job_seeker users."""
        result = await require_job_seeker(current_user=job_seeker_user)
        assert result == job_seeker_user
    
    @pytest.mark.asyncio
    async def test_require_job_seeker_allows_admin(self, admin_user: DBUser):
        """Test that require_job_seeker allows admin users (admin bypass)."""
        result = await require_job_seeker(current_user=admin_user)
        assert result == admin_user
    
    @pytest.mark.asyncio
    async def test_require_job_seeker_denies_recruiter(self, recruiter_user: DBUser):
        """Test that require_job_seeker denies recruiter users."""
        with pytest.raises(HTTPException) as exc_info:
            await require_job_seeker(current_user=recruiter_user)
        
        assert exc_info.value.status_code == 403
        assert "Access denied" in str(exc_info.value.detail)


class TestRequireRecruiter:
    """Tests for the require_recruiter dependency."""
    
    @pytest.mark.asyncio
    async def test_require_recruiter_allows_recruiter(self, recruiter_user: DBUser):
        """Test that require_recruiter allows recruiter users."""
        result = await require_recruiter(current_user=recruiter_user)
        assert result == recruiter_user
    
    @pytest.mark.asyncio
    async def test_require_recruiter_allows_admin(self, admin_user: DBUser):
        """Test that require_recruiter allows admin users (admin bypass)."""
        result = await require_recruiter(current_user=admin_user)
        assert result == admin_user
    
    @pytest.mark.asyncio
    async def test_require_recruiter_denies_job_seeker(self, job_seeker_user: DBUser):
        """Test that require_recruiter denies job_seeker users."""
        with pytest.raises(HTTPException) as exc_info:
            await require_recruiter(current_user=job_seeker_user)
        
        assert exc_info.value.status_code == 403
        assert "Access denied" in str(exc_info.value.detail)


# ============================================================================
# Integration tests with API endpoints
# ============================================================================

class TestCVRouteProtection:
    """Tests for CV routes being protected by require_job_seeker."""
    
    def test_cv_routes_accessible_by_job_seeker(
        self, job_seeker_user: DBUser, mock_db_session: AsyncMock
    ):
        """Test that job_seeker can access CV routes."""
        from app.modules.auth.dependencies import rate_limit_cv_upload
        
        app.dependency_overrides[get_db] = lambda: mock_db_session
        app.dependency_overrides[get_current_user] = lambda: job_seeker_user
        app.dependency_overrides[get_current_active_user] = lambda: job_seeker_user
        app.dependency_overrides[rate_limit_cv_upload] = lambda: job_seeker_user
        
        # Mock the database query to return empty list
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db_session.execute.return_value = mock_result
        
        with TestClient(app) as client:
            response = client.get("/api/v1/cvs/")
            assert response.status_code == 200
        
        app.dependency_overrides.clear()
    
    def test_cv_routes_accessible_by_admin(
        self, admin_user: DBUser, mock_db_session: AsyncMock
    ):
        """Test that admin can access CV routes."""
        from app.modules.auth.dependencies import rate_limit_cv_upload
        
        app.dependency_overrides[get_db] = lambda: mock_db_session
        app.dependency_overrides[get_current_user] = lambda: admin_user
        app.dependency_overrides[get_current_active_user] = lambda: admin_user
        app.dependency_overrides[rate_limit_cv_upload] = lambda: admin_user
        
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db_session.execute.return_value = mock_result
        
        with TestClient(app) as client:
            response = client.get("/api/v1/cvs/")
            assert response.status_code == 200
        
        app.dependency_overrides.clear()
    
    def test_cv_routes_denied_to_recruiter(
        self, recruiter_user: DBUser, mock_db_session: AsyncMock
    ):
        """Test that recruiter cannot access CV routes (gets 403)."""
        from app.modules.auth.dependencies import rate_limit_cv_upload
        
        app.dependency_overrides[get_db] = lambda: mock_db_session
        app.dependency_overrides[get_current_user] = lambda: recruiter_user
        app.dependency_overrides[get_current_active_user] = lambda: recruiter_user
        # Don't override rate_limit - it uses require_job_seeker internally
        
        with TestClient(app) as client:
            response = client.get("/api/v1/cvs/")
            assert response.status_code == 403
            assert "Access denied" in response.json()["detail"]
        
        app.dependency_overrides.clear()


class TestJobRouteProtection:
    """Tests for Job routes being protected by require_recruiter."""
    
    def test_job_routes_accessible_by_recruiter(
        self, recruiter_user: DBUser, mock_db_session: AsyncMock
    ):
        """Test that recruiter can access Job routes."""
        app.dependency_overrides[get_db] = lambda: mock_db_session
        app.dependency_overrides[get_current_user] = lambda: recruiter_user
        app.dependency_overrides[get_current_active_user] = lambda: recruiter_user
        
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db_session.execute.return_value = mock_result
        
        with TestClient(app) as client:
            # Use /jd endpoint which is the actual listing endpoint
            response = client.get("/api/v1/jobs/jd")
            assert response.status_code == 200
        
        app.dependency_overrides.clear()
    
    def test_job_routes_accessible_by_admin(
        self, admin_user: DBUser, mock_db_session: AsyncMock
    ):
        """Test that admin can access Job routes."""
        app.dependency_overrides[get_db] = lambda: mock_db_session
        app.dependency_overrides[get_current_user] = lambda: admin_user
        app.dependency_overrides[get_current_active_user] = lambda: admin_user
        
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db_session.execute.return_value = mock_result
        
        with TestClient(app) as client:
            response = client.get("/api/v1/jobs/jd")
            assert response.status_code == 200
        
        app.dependency_overrides.clear()
    
    def test_job_routes_denied_to_job_seeker(
        self, job_seeker_user: DBUser, mock_db_session: AsyncMock
    ):
        """Test that job_seeker cannot access Job routes (gets 403)."""
        app.dependency_overrides[get_db] = lambda: mock_db_session
        app.dependency_overrides[get_current_user] = lambda: job_seeker_user
        app.dependency_overrides[get_current_active_user] = lambda: job_seeker_user
        
        with TestClient(app) as client:
            response = client.get("/api/v1/jobs/jd")
            assert response.status_code == 403
            assert "Access denied" in response.json()["detail"]
        
        app.dependency_overrides.clear()


class TestAdminRouteProtection:
    """Tests for Admin routes being protected by require_admin."""
    
    def test_admin_routes_accessible_by_admin(
        self, admin_user: DBUser, mock_db_session: AsyncMock
    ):
        """Test that admin can access Admin routes."""
        app.dependency_overrides[get_db] = lambda: mock_db_session
        app.dependency_overrides[get_current_user] = lambda: admin_user
        app.dependency_overrides[get_current_active_user] = lambda: admin_user
        
        mock_result = MagicMock()
        mock_result.scalar.return_value = 10
        mock_db_session.execute.return_value = mock_result
        
        with TestClient(app) as client:
            response = client.get("/api/v1/admin/stats")
            assert response.status_code == 200
        
        app.dependency_overrides.clear()
    
    def test_admin_routes_denied_to_job_seeker(
        self, job_seeker_user: DBUser, mock_db_session: AsyncMock
    ):
        """Test that job_seeker cannot access Admin routes (gets 403)."""
        app.dependency_overrides[get_db] = lambda: mock_db_session
        app.dependency_overrides[get_current_user] = lambda: job_seeker_user
        app.dependency_overrides[get_current_active_user] = lambda: job_seeker_user
        
        with TestClient(app) as client:
            response = client.get("/api/v1/admin/stats")
            assert response.status_code == 403
        
        app.dependency_overrides.clear()
    
    def test_admin_routes_denied_to_recruiter(
        self, recruiter_user: DBUser, mock_db_session: AsyncMock
    ):
        """Test that recruiter cannot access Admin routes (gets 403)."""
        app.dependency_overrides[get_db] = lambda: mock_db_session
        app.dependency_overrides[get_current_user] = lambda: recruiter_user
        app.dependency_overrides[get_current_active_user] = lambda: recruiter_user
        
        with TestClient(app) as client:
            response = client.get("/api/v1/admin/stats")
            assert response.status_code == 403
        
        app.dependency_overrides.clear()
