"""
Tests for CV visibility features (Story 3.8).

This module tests:
1. CV visibility update endpoint (PATCH /api/v1/cvs/{cv_id}/visibility)
2. Recruiter CV access endpoint (GET /api/v1/jobs/jd/{jd_id}/candidates/{cv_id})
3. Recruiter CV file access endpoint (GET /api/v1/jobs/jd/{jd_id}/candidates/{cv_id}/file)
"""

import pytest
import uuid
import os
import tempfile
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timezone
from pathlib import Path

from fastapi.testclient import TestClient
from fastapi import HTTPException

from app.modules.users.models import User as DBUser
from app.modules.cv.models import CV


# ============================================================================
# PATCH /api/v1/cvs/{cv_id}/visibility Tests
# ============================================================================


@pytest.mark.asyncio
async def test_update_visibility_to_public(client: TestClient, test_user: DBUser, mock_db_session: AsyncMock):
    """Test updating CV visibility from private to public."""
    cv_id = uuid.uuid4()
    
    # Create mock CV owned by test user
    mock_cv = MagicMock()
    mock_cv.id = cv_id
    mock_cv.user_id = test_user.id
    mock_cv.filename = "test_cv.pdf"
    mock_cv.file_path = "/tmp/test_cv.pdf"
    mock_cv.uploaded_at = datetime.now(timezone.utc)
    mock_cv.is_active = True
    mock_cv.is_public = False  # Before update
    mock_cv.analyses = []  # No analyses
    
    # Setup mock db.execute to return the CV
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_cv
    mock_db_session.execute.return_value = mock_result
    
    response = client.patch(
        f"/api/v1/cvs/{cv_id}/visibility",
        json={"is_public": True}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["is_public"] is True


@pytest.mark.asyncio
async def test_update_visibility_to_private(client: TestClient, test_user: DBUser, mock_db_session: AsyncMock):
    """Test updating CV visibility from public to private."""
    cv_id = uuid.uuid4()
    
    mock_cv = MagicMock()
    mock_cv.id = cv_id
    mock_cv.user_id = test_user.id
    mock_cv.filename = "test_cv.pdf"
    mock_cv.file_path = "/tmp/test_cv.pdf"
    mock_cv.uploaded_at = datetime.now(timezone.utc)
    mock_cv.is_active = True
    mock_cv.is_public = True  # Before update
    mock_cv.analyses = []  # No analyses
    
    # Setup mock db.execute to return the CV
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_cv
    mock_db_session.execute.return_value = mock_result
    
    response = client.patch(
        f"/api/v1/cvs/{cv_id}/visibility",
        json={"is_public": False}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["is_public"] is False


@pytest.mark.asyncio
async def test_update_visibility_cv_not_found(client: TestClient, test_user: DBUser, mock_db_session: AsyncMock):
    """Test updating visibility for non-existent CV returns 404."""
    cv_id = uuid.uuid4()
    
    # Setup mock db.execute to return None (CV not found)
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db_session.execute.return_value = mock_result
    
    response = client.patch(
        f"/api/v1/cvs/{cv_id}/visibility",
        json={"is_public": True}
    )
    
    assert response.status_code == 404
    assert response.json()["detail"] == "CV not found"


@pytest.mark.asyncio
async def test_update_visibility_not_owner(client: TestClient, test_user: DBUser, mock_db_session: AsyncMock):
    """Test updating visibility for CV owned by another user returns 403."""
    cv_id = uuid.uuid4()
    
    # Create mock CV owned by a different user
    mock_cv = MagicMock()
    mock_cv.id = cv_id
    mock_cv.user_id = 999  # Different user ID
    mock_cv.filename = "test_cv.pdf"
    mock_cv.file_path = "/tmp/test_cv.pdf"
    mock_cv.uploaded_at = datetime.now(timezone.utc)
    mock_cv.is_active = True
    mock_cv.is_public = False
    mock_cv.analyses = []
    
    # Setup mock db.execute to return the CV
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_cv
    mock_db_session.execute.return_value = mock_result
    
    response = client.patch(
        f"/api/v1/cvs/{cv_id}/visibility",
        json={"is_public": True}
    )
    
    assert response.status_code == 403
    assert "permission" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_update_visibility_unauthorized():
    """Test updating visibility without authentication returns 401."""
    from fastapi.testclient import TestClient
    from app.main import app
    
    cv_id = uuid.uuid4()
    
    # Clear all overrides for unauthenticated test
    app.dependency_overrides = {}
    
    with TestClient(app) as unauthenticated_client:
        response = unauthenticated_client.patch(
            f"/api/v1/cvs/{cv_id}/visibility",
            json={"is_public": True}
        )
        
        assert response.status_code == 401
        assert response.json()["detail"] == "Not authenticated"


@pytest.mark.asyncio
async def test_update_visibility_invalid_body(client: TestClient, test_user: DBUser):
    """Test updating visibility with invalid body returns 422."""
    cv_id = uuid.uuid4()
    
    response = client.patch(
        f"/api/v1/cvs/{cv_id}/visibility",
        json={"is_public": "not-a-boolean"}  # Invalid type
    )
    
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_visibility_missing_field(client: TestClient, test_user: DBUser):
    """Test updating visibility with missing is_public field returns 422."""
    cv_id = uuid.uuid4()
    
    response = client.patch(
        f"/api/v1/cvs/{cv_id}/visibility",
        json={}  # Missing is_public
    )
    
    assert response.status_code == 422


# ============================================================================
# GET /api/v1/jobs/jd/{jd_id}/candidates/{cv_id} Tests
# ============================================================================


@pytest.mark.asyncio
async def test_recruiter_access_public_cv(client: TestClient, test_user: DBUser, mock_db_session: AsyncMock):
    """Test recruiter can access public CV details."""
    jd_id = uuid.uuid4()
    cv_id = uuid.uuid4()
    
    with patch("app.modules.jobs.router.job_service.get_job_description") as mock_get_jd, \
         patch("app.modules.jobs.router.candidate_ranker.rank_candidates") as mock_rank, \
         patch("app.modules.jobs.router.select") as mock_select:
        
        # Mock JD exists and belongs to user
        mock_jd = MagicMock()
        mock_jd.id = jd_id
        mock_jd.user_id = test_user.id
        mock_get_jd.return_value = mock_jd
        
        # Mock CV exists and is public
        mock_cv = MagicMock()
        mock_cv.id = cv_id
        mock_cv.is_public = True
        mock_cv.filename = "public_cv.pdf"
        mock_cv.uploaded_at = datetime.now(timezone.utc)
        mock_cv.analyses = []
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_cv
        mock_db_session.execute.return_value = mock_result
        
        # Mock candidate ranking (CV was matched with JD)
        mock_candidate = MagicMock()
        mock_candidate.cv_id = cv_id
        mock_candidate.match_score = 85
        mock_candidate.breakdown = MagicMock()
        mock_candidate.breakdown.matched_skills = ["Python", "FastAPI"]
        mock_rank.return_value = ([mock_candidate], 1)
        
        response = client.get(f"/api/v1/jobs/jd/{jd_id}/candidates/{cv_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["cv_id"] == str(cv_id)
        assert data["filename"] == "public_cv.pdf"
        assert data["match_score"] == 85


@pytest.mark.asyncio
async def test_recruiter_access_private_cv_forbidden(client: TestClient, test_user: DBUser, mock_db_session: AsyncMock):
    """Test recruiter cannot access private CV details - returns 403."""
    jd_id = uuid.uuid4()
    cv_id = uuid.uuid4()
    
    with patch("app.modules.jobs.router.job_service.get_job_description") as mock_get_jd, \
         patch("app.modules.jobs.router.select") as mock_select:
        
        # Mock JD exists and belongs to user
        mock_jd = MagicMock()
        mock_jd.id = jd_id
        mock_jd.user_id = test_user.id
        mock_get_jd.return_value = mock_jd
        
        # Mock CV exists but is PRIVATE
        mock_cv = MagicMock()
        mock_cv.id = cv_id
        mock_cv.is_public = False  # Private CV
        mock_cv.filename = "private_cv.pdf"
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_cv
        mock_db_session.execute.return_value = mock_result
        
        response = client.get(f"/api/v1/jobs/jd/{jd_id}/candidates/{cv_id}")
        
        assert response.status_code == 403
        assert "private" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_recruiter_access_jd_not_found(client: TestClient, test_user: DBUser, mock_db_session: AsyncMock):
    """Test accessing CV for non-existent JD returns 404."""
    jd_id = uuid.uuid4()
    cv_id = uuid.uuid4()
    
    with patch("app.modules.jobs.router.job_service.get_job_description") as mock_get_jd:
        mock_get_jd.return_value = None  # JD not found
        
        response = client.get(f"/api/v1/jobs/jd/{jd_id}/candidates/{cv_id}")
        
        assert response.status_code == 404
        assert "job description" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_recruiter_access_cv_not_found(client: TestClient, test_user: DBUser, mock_db_session: AsyncMock):
    """Test accessing non-existent CV returns 404."""
    jd_id = uuid.uuid4()
    cv_id = uuid.uuid4()
    
    with patch("app.modules.jobs.router.job_service.get_job_description") as mock_get_jd, \
         patch("app.modules.jobs.router.select") as mock_select:
        
        # Mock JD exists
        mock_jd = MagicMock()
        mock_jd.id = jd_id
        mock_jd.user_id = test_user.id
        mock_get_jd.return_value = mock_jd
        
        # Mock CV not found
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result
        
        response = client.get(f"/api/v1/jobs/jd/{jd_id}/candidates/{cv_id}")
        
        assert response.status_code == 404


@pytest.mark.asyncio
async def test_recruiter_access_unauthorized():
    """Test accessing CV details without authentication returns 401."""
    from fastapi.testclient import TestClient
    from app.main import app
    
    jd_id = uuid.uuid4()
    cv_id = uuid.uuid4()
    
    # Clear all overrides
    app.dependency_overrides = {}
    
    with TestClient(app) as unauthenticated_client:
        response = unauthenticated_client.get(f"/api/v1/jobs/jd/{jd_id}/candidates/{cv_id}")
        
        assert response.status_code == 401
        assert response.json()["detail"] == "Not authenticated"


# ============================================================================
# GET /api/v1/jobs/jd/{jd_id}/candidates/{cv_id}/file Tests
# ============================================================================


@pytest.mark.asyncio
async def test_recruiter_access_public_cv_file_inline(client: TestClient, test_user: DBUser, mock_db_session: AsyncMock):
    """Test recruiter can access public CV file for inline preview."""
    jd_id = uuid.uuid4()
    cv_id = uuid.uuid4()
    
    # Create a temporary PDF file for testing
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_file:
        tmp_file.write(b"%PDF-1.4 test content")
        tmp_file_path = tmp_file.name
        relative_path = os.path.basename(tmp_file_path)
    
    try:
        with patch("app.modules.jobs.router.job_service.get_job_description") as mock_get_jd, \
             patch("app.modules.jobs.router.candidate_ranker.rank_candidates") as mock_rank, \
             patch("app.modules.jobs.router.select") as mock_select, \
             patch("app.modules.jobs.router.settings") as mock_settings:
            
            # Mock JD exists and belongs to user
            mock_jd = MagicMock()
            mock_jd.id = jd_id
            mock_jd.user_id = test_user.id
            mock_get_jd.return_value = mock_jd
            
            # Mock CV exists and is public
            mock_cv = MagicMock()
            mock_cv.id = cv_id
            mock_cv.is_public = True
            mock_cv.filename = "public_cv.pdf"
            mock_cv.file_path = relative_path
            
            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = mock_cv
            mock_db_session.execute.return_value = mock_result
            
            # Mock candidate ranking (CV was matched with JD)
            mock_candidate = MagicMock()
            mock_candidate.cv_id = cv_id
            mock_candidate.match_score = 85
            mock_candidate.breakdown = MagicMock()
            mock_candidate.breakdown.matched_skills = ["Python"]
            mock_rank.return_value = ([mock_candidate], 1)
            
            # Mock settings to point to temp directory
            mock_settings.CV_STORAGE_PATH = Path(os.path.dirname(tmp_file_path))
            
            response = client.get(f"/api/v1/jobs/jd/{jd_id}/candidates/{cv_id}/file")
            
            assert response.status_code == 200
            assert response.headers["content-type"] == "application/pdf"
            assert "inline" in response.headers.get("content-disposition", "")
    finally:
        os.unlink(tmp_file_path)


@pytest.mark.asyncio
async def test_recruiter_access_public_cv_file_download(client: TestClient, test_user: DBUser, mock_db_session: AsyncMock):
    """Test recruiter can download public CV file with ?download=true."""
    jd_id = uuid.uuid4()
    cv_id = uuid.uuid4()
    
    # Create a temporary PDF file for testing
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_file:
        tmp_file.write(b"%PDF-1.4 test download content")
        tmp_file_path = tmp_file.name
        relative_path = os.path.basename(tmp_file_path)
    
    try:
        with patch("app.modules.jobs.router.job_service.get_job_description") as mock_get_jd, \
             patch("app.modules.jobs.router.candidate_ranker.rank_candidates") as mock_rank, \
             patch("app.modules.jobs.router.select") as mock_select, \
             patch("app.modules.jobs.router.settings") as mock_settings:
            
            # Mock JD exists and belongs to user
            mock_jd = MagicMock()
            mock_jd.id = jd_id
            mock_jd.user_id = test_user.id
            mock_get_jd.return_value = mock_jd
            
            # Mock CV exists and is public
            mock_cv = MagicMock()
            mock_cv.id = cv_id
            mock_cv.is_public = True
            mock_cv.filename = "download_cv.pdf"
            mock_cv.file_path = relative_path
            
            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = mock_cv
            mock_db_session.execute.return_value = mock_result
            
            # Mock candidate ranking
            mock_candidate = MagicMock()
            mock_candidate.cv_id = cv_id
            mock_candidate.match_score = 90
            mock_candidate.breakdown = MagicMock()
            mock_candidate.breakdown.matched_skills = ["Python", "FastAPI"]
            mock_rank.return_value = ([mock_candidate], 1)
            
            # Mock settings
            mock_settings.CV_STORAGE_PATH = Path(os.path.dirname(tmp_file_path))
            
            response = client.get(f"/api/v1/jobs/jd/{jd_id}/candidates/{cv_id}/file?download=true")
            
            assert response.status_code == 200
            assert "attachment" in response.headers.get("content-disposition", "")
            assert 'filename="download_cv.pdf"' in response.headers.get("content-disposition", "")
    finally:
        os.unlink(tmp_file_path)


@pytest.mark.asyncio
async def test_recruiter_access_private_cv_file_forbidden(client: TestClient, test_user: DBUser, mock_db_session: AsyncMock):
    """Test recruiter cannot access private CV file - returns 403."""
    jd_id = uuid.uuid4()
    cv_id = uuid.uuid4()
    
    with patch("app.modules.jobs.router.job_service.get_job_description") as mock_get_jd, \
         patch("app.modules.jobs.router.select") as mock_select:
        
        # Mock JD exists and belongs to user
        mock_jd = MagicMock()
        mock_jd.id = jd_id
        mock_jd.user_id = test_user.id
        mock_get_jd.return_value = mock_jd
        
        # Mock CV exists but is PRIVATE
        mock_cv = MagicMock()
        mock_cv.id = cv_id
        mock_cv.is_public = False  # Private CV
        mock_cv.filename = "private_cv.pdf"
        mock_cv.file_path = "some_path.pdf"
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_cv
        mock_db_session.execute.return_value = mock_result
        
        response = client.get(f"/api/v1/jobs/jd/{jd_id}/candidates/{cv_id}/file")
        
        assert response.status_code == 403
        assert "private" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_recruiter_access_file_jd_not_found(client: TestClient, test_user: DBUser, mock_db_session: AsyncMock):
    """Test accessing CV file for non-existent JD returns 404."""
    jd_id = uuid.uuid4()
    cv_id = uuid.uuid4()
    
    with patch("app.modules.jobs.router.job_service.get_job_description") as mock_get_jd:
        mock_get_jd.return_value = None  # JD not found
        
        response = client.get(f"/api/v1/jobs/jd/{jd_id}/candidates/{cv_id}/file")
        
        assert response.status_code == 404
        assert "job description" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_recruiter_access_file_cv_not_matched(client: TestClient, test_user: DBUser, mock_db_session: AsyncMock):
    """Test accessing file for CV not matched with JD returns 404."""
    jd_id = uuid.uuid4()
    cv_id = uuid.uuid4()
    
    with patch("app.modules.jobs.router.job_service.get_job_description") as mock_get_jd, \
         patch("app.modules.jobs.router.candidate_ranker.rank_candidates") as mock_rank, \
         patch("app.modules.jobs.router.select") as mock_select:
        
        # Mock JD exists
        mock_jd = MagicMock()
        mock_jd.id = jd_id
        mock_jd.user_id = test_user.id
        mock_get_jd.return_value = mock_jd
        
        # Mock CV exists and is public
        mock_cv = MagicMock()
        mock_cv.id = cv_id
        mock_cv.is_public = True
        mock_cv.filename = "test_cv.pdf"
        mock_cv.file_path = "test_path.pdf"
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_cv
        mock_db_session.execute.return_value = mock_result
        
        # Mock ranking - this CV not in results (not matched with JD)
        mock_rank.return_value = ([], 0)  # Empty results
        
        response = client.get(f"/api/v1/jobs/jd/{jd_id}/candidates/{cv_id}/file")
        
        assert response.status_code == 404
        assert "candidate not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_recruiter_access_file_unauthorized():
    """Test accessing CV file without authentication returns 401."""
    from fastapi.testclient import TestClient
    from app.main import app
    
    jd_id = uuid.uuid4()
    cv_id = uuid.uuid4()
    
    # Clear all overrides
    app.dependency_overrides = {}
    
    with TestClient(app) as unauthenticated_client:
        response = unauthenticated_client.get(f"/api/v1/jobs/jd/{jd_id}/candidates/{cv_id}/file")
        
        assert response.status_code == 401
        assert response.json()["detail"] == "Not authenticated"
