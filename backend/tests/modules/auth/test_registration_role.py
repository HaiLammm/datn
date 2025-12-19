"""
Tests for registration with role functionality.

These tests verify that the registration endpoint correctly handles
role assignment and validates role restrictions.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.main import app
from app.core.database import get_db
from app.modules.users.schemas import UserCreate, UserRole


# ============================================================================
# Tests for UserCreate schema role validation
# ============================================================================

class TestUserCreateRoleValidation:
    """Tests for the UserCreate schema role validation."""
    
    def test_user_create_with_job_seeker_role(self):
        """Test creating user with job_seeker role."""
        user = UserCreate(
            email="test@example.com",
            password="password123",
            role="job_seeker"
        )
        assert user.role == "job_seeker"
    
    def test_user_create_with_recruiter_role(self):
        """Test creating user with recruiter role."""
        user = UserCreate(
            email="test@example.com",
            password="password123",
            role="recruiter"
        )
        assert user.role == "recruiter"
    
    def test_user_create_default_role_is_job_seeker(self):
        """Test that default role is job_seeker when not specified."""
        user = UserCreate(
            email="test@example.com",
            password="password123"
        )
        assert user.role == "job_seeker"
    
    def test_user_create_with_admin_role_fails(self):
        """Test that creating user with admin role raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                email="test@example.com",
                password="password123",
                role="admin"
            )
        
        # Check error message
        errors = exc_info.value.errors()
        assert len(errors) > 0
        # The error can come from either the Literal type or the validator
        # Just verify an error was raised for role
        assert any("role" in str(error.get("loc", [])) or "admin" in str(error).lower() for error in errors)
    
    def test_user_create_with_invalid_role_fails(self):
        """Test that creating user with invalid role raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                email="test@example.com",
                password="password123",
                role="invalid_role"
            )
        
        errors = exc_info.value.errors()
        assert len(errors) > 0


# ============================================================================
# Tests for registration endpoint role handling
# ============================================================================

class TestRegistrationEndpointWithRole:
    """Tests for the /auth/register endpoint role handling."""
    
    @pytest.fixture
    def mock_db_session(self) -> AsyncMock:
        """Create a mock database session."""
        mock_session = AsyncMock()
        mock_session.execute = AsyncMock()
        mock_session.commit = AsyncMock()
        mock_session.rollback = AsyncMock()
        mock_session.close = AsyncMock()
        return mock_session
    
    def test_register_with_job_seeker_role_success(self, mock_db_session: AsyncMock):
        """Test successful registration with job_seeker role."""
        from app.modules.auth.services import AuthService
        
        app.dependency_overrides[get_db] = lambda: mock_db_session
        
        # Mock the auth service
        with patch.object(AuthService, 'register_user') as mock_register:
            mock_user = MagicMock()
            mock_user.email = "newuser@example.com"
            mock_user.full_name = "New User"
            mock_user.role = "job_seeker"
            mock_register.return_value = (mock_user, "123456")
            
            with TestClient(app) as client:
                response = client.post(
                    "/api/v1/auth/register",
                    json={
                        "email": "newuser@example.com",
                        "password": "password123",
                        "full_name": "New User",
                        "role": "job_seeker"
                    }
                )
                
                assert response.status_code == 201
                assert "msg" in response.json()
                
                # Verify register_user was called with correct role
                call_args = mock_register.call_args
                user_in = call_args.kwargs.get('user_in') or call_args.args[0]
                assert user_in.role == "job_seeker"
        
        app.dependency_overrides.clear()
    
    def test_register_with_recruiter_role_success(self, mock_db_session: AsyncMock):
        """Test successful registration with recruiter role."""
        from app.modules.auth.services import AuthService
        
        app.dependency_overrides[get_db] = lambda: mock_db_session
        
        with patch.object(AuthService, 'register_user') as mock_register:
            mock_user = MagicMock()
            mock_user.email = "recruiter@example.com"
            mock_user.full_name = "Recruiter User"
            mock_user.role = "recruiter"
            mock_register.return_value = (mock_user, "123456")
            
            with TestClient(app) as client:
                response = client.post(
                    "/api/v1/auth/register",
                    json={
                        "email": "recruiter@example.com",
                        "password": "password123",
                        "full_name": "Recruiter User",
                        "role": "recruiter"
                    }
                )
                
                assert response.status_code == 201
                
                # Verify register_user was called with correct role
                call_args = mock_register.call_args
                user_in = call_args.kwargs.get('user_in') or call_args.args[0]
                assert user_in.role == "recruiter"
        
        app.dependency_overrides.clear()
    
    def test_register_without_role_defaults_to_job_seeker(self, mock_db_session: AsyncMock):
        """Test that registration without role defaults to job_seeker."""
        from app.modules.auth.services import AuthService
        
        app.dependency_overrides[get_db] = lambda: mock_db_session
        
        with patch.object(AuthService, 'register_user') as mock_register:
            mock_user = MagicMock()
            mock_user.email = "default@example.com"
            mock_user.full_name = "Default User"
            mock_user.role = "job_seeker"
            mock_register.return_value = (mock_user, "123456")
            
            with TestClient(app) as client:
                response = client.post(
                    "/api/v1/auth/register",
                    json={
                        "email": "default@example.com",
                        "password": "password123",
                        "full_name": "Default User"
                        # No role specified
                    }
                )
                
                assert response.status_code == 201
                
                # Verify register_user was called with default role
                call_args = mock_register.call_args
                user_in = call_args.kwargs.get('user_in') or call_args.args[0]
                assert user_in.role == "job_seeker"
        
        app.dependency_overrides.clear()
    
    def test_register_with_admin_role_fails(self, mock_db_session: AsyncMock):
        """Test that registration with admin role is rejected."""
        app.dependency_overrides[get_db] = lambda: mock_db_session
        
        with TestClient(app) as client:
            response = client.post(
                "/api/v1/auth/register",
                json={
                    "email": "admin@example.com",
                    "password": "password123",
                    "full_name": "Admin User",
                    "role": "admin"
                }
            )
            
            # Should get 422 validation error
            assert response.status_code == 422
            
            # Check that error is about the role
            error_detail = response.json()
            assert "detail" in error_detail
        
        app.dependency_overrides.clear()
    
    def test_register_with_invalid_role_fails(self, mock_db_session: AsyncMock):
        """Test that registration with invalid role is rejected."""
        app.dependency_overrides[get_db] = lambda: mock_db_session
        
        with TestClient(app) as client:
            response = client.post(
                "/api/v1/auth/register",
                json={
                    "email": "invalid@example.com",
                    "password": "password123",
                    "full_name": "Invalid Role User",
                    "role": "super_user"
                }
            )
            
            # Should get 422 validation error
            assert response.status_code == 422
        
        app.dependency_overrides.clear()


# ============================================================================
# Tests for JWT token including role
# ============================================================================

class TestJWTTokenWithRole:
    """Tests for JWT token containing role claim."""
    
    @pytest.fixture
    def mock_db_session(self) -> AsyncMock:
        """Create a mock database session."""
        mock_session = AsyncMock()
        mock_session.execute = AsyncMock()
        mock_session.commit = AsyncMock()
        mock_session.rollback = AsyncMock()
        mock_session.close = AsyncMock()
        return mock_session
    
    def test_login_returns_jwt_with_role(self, mock_db_session: AsyncMock):
        """Test that login returns JWT token containing role claim."""
        from app.modules.auth.services import AuthService
        from app.modules.users.models import User as DBUser
        from jose import jwt
        from app.core.config import settings
        from app.core.security import ALGORITHM
        
        app.dependency_overrides[get_db] = lambda: mock_db_session
        
        # Create a mock user
        mock_user = MagicMock(spec=DBUser)
        mock_user.id = 1
        mock_user.email = "user@example.com"
        mock_user.hashed_password = "hashed"
        mock_user.role = "recruiter"
        mock_user.is_active = True
        
        with patch.object(AuthService, 'authenticate_user', return_value=mock_user):
            with TestClient(app) as client:
                response = client.post(
                    "/api/v1/auth/login",
                    json={
                        "email": "user@example.com",
                        "password": "password123"
                    }
                )
                
                assert response.status_code == 200
                data = response.json()
                assert "access_token" in data
                
                # Decode the token and verify role is included
                token = data["access_token"]
                payload = jwt.decode(
                    token, 
                    settings.SECRET_KEY, 
                    algorithms=[ALGORITHM]
                )
                
                assert "role" in payload
                assert payload["role"] == "recruiter"
                assert payload["sub"] == "user@example.com"
        
        app.dependency_overrides.clear()
    
    def test_login_with_job_seeker_includes_correct_role(self, mock_db_session: AsyncMock):
        """Test that login with job_seeker includes correct role in JWT."""
        from app.modules.auth.services import AuthService
        from app.modules.users.models import User as DBUser
        from jose import jwt
        from app.core.config import settings
        from app.core.security import ALGORITHM
        
        app.dependency_overrides[get_db] = lambda: mock_db_session
        
        mock_user = MagicMock(spec=DBUser)
        mock_user.id = 2
        mock_user.email = "jobseeker@example.com"
        mock_user.hashed_password = "hashed"
        mock_user.role = "job_seeker"
        mock_user.is_active = True
        
        with patch.object(AuthService, 'authenticate_user', return_value=mock_user):
            with TestClient(app) as client:
                response = client.post(
                    "/api/v1/auth/login",
                    json={
                        "email": "jobseeker@example.com",
                        "password": "password123"
                    }
                )
                
                assert response.status_code == 200
                data = response.json()
                
                token = data["access_token"]
                payload = jwt.decode(
                    token, 
                    settings.SECRET_KEY, 
                    algorithms=[ALGORITHM]
                )
                
                assert payload["role"] == "job_seeker"
        
        app.dependency_overrides.clear()
    
    def test_login_with_admin_includes_correct_role(self, mock_db_session: AsyncMock):
        """Test that login with admin includes correct role in JWT."""
        from app.modules.auth.services import AuthService
        from app.modules.users.models import User as DBUser
        from jose import jwt
        from app.core.config import settings
        from app.core.security import ALGORITHM
        
        app.dependency_overrides[get_db] = lambda: mock_db_session
        
        mock_user = MagicMock(spec=DBUser)
        mock_user.id = 3
        mock_user.email = "admin@example.com"
        mock_user.hashed_password = "hashed"
        mock_user.role = "admin"
        mock_user.is_active = True
        
        with patch.object(AuthService, 'authenticate_user', return_value=mock_user):
            with TestClient(app) as client:
                response = client.post(
                    "/api/v1/auth/login",
                    json={
                        "email": "admin@example.com",
                        "password": "password123"
                    }
                )
                
                assert response.status_code == 200
                data = response.json()
                
                token = data["access_token"]
                payload = jwt.decode(
                    token, 
                    settings.SECRET_KEY, 
                    algorithms=[ALGORITHM]
                )
                
                assert payload["role"] == "admin"
        
        app.dependency_overrides.clear()
