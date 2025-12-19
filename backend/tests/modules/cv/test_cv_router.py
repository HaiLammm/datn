import pytest
import uuid
from unittest.mock import AsyncMock, patch, MagicMock

from fastapi.testclient import TestClient
from httpx import AsyncClient

from app.core.config import settings
from app.modules.users.models import User as DBUser
from app.modules.cv.models import CV


@pytest.mark.asyncio
async def test_upload_cv_valid_pdf(client: TestClient, test_user: DBUser):
    """Test uploading a valid PDF file."""
    # Mock the create_cv service
    with patch("app.modules.cv.router.create_cv") as mock_create_cv:
        mock_cv = MagicMock()
        mock_cv.id = "00000000-0000-0000-0000-000000000002"
        mock_cv.user_id = test_user.id  # Use int from test_user
        mock_cv.filename = "test_cv.pdf"
        mock_cv.file_path = f"{settings.CV_STORAGE_PATH}/test_cv.pdf"
        mock_cv.uploaded_at = "2025-01-01T00:00:00"
        mock_cv.is_active = True
        
        mock_create_cv.return_value = mock_cv

        # Create a dummy PDF file
        pdf_content = b"%PDF-1.4\n1 0 obj<</Type/Catalog>>endobj\nxref\n0 2\n0000000000 65535 f\n0000000009 00000 n\ntrailer<</Size 2/Root 1 0 R>>startxref\n15\n%%EOF"
        files = {"file": ("test_cv.pdf", pdf_content, "application/pdf")}
        response = client.post("/api/v1/cvs/", files=files)

        assert response.status_code == 201
        assert response.json()["filename"] == "test_cv.pdf"
        mock_create_cv.assert_called_once()


@pytest.mark.asyncio
async def test_upload_cv_invalid_file_type(client: TestClient):
    """Test uploading an invalid file type."""
    # Create a dummy text file
    txt_content = b"This is a text file, not a PDF or DOCX."
    files = {"file": ("test.txt", txt_content, "text/plain")}
    response = client.post("/api/v1/cvs/", files=files)

    assert response.status_code == 400
    assert "Chỉ chấp nhận file PDF hoặc DOCX." in response.json()["detail"]


@pytest.mark.asyncio
async def test_upload_cv_unauthenticated():
    """Test uploading without authentication."""
    from fastapi.testclient import TestClient
    from app.main import app
    
    # Use fresh client without auth overrides
    app.dependency_overrides = {}
    
    with TestClient(app) as unauthenticated_client:
        pdf_content = b"%PDF-1.4\n..."
        files = {"file": ("test_cv.pdf", pdf_content, "application/pdf")}
        response = unauthenticated_client.post("/api/v1/cvs/", files=files)
        
        assert response.status_code == 401
        assert response.json()["detail"] == "Not authenticated"


@pytest.mark.asyncio
async def test_read_root(client: TestClient):
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the API"}


@pytest.mark.asyncio
async def test_list_user_cvs(client: TestClient, mock_db_session: AsyncMock):
    """Test listing user CVs returns empty list when no CVs exist."""
    # Mock the database to return empty result
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    mock_db_session.execute.return_value = mock_result
    
    response = client.get("/api/v1/cvs/")
    assert response.status_code == 200
    assert response.json() == []


# ============================================================================
# DELETE /api/v1/cvs/{cv_id} Tests
# ============================================================================


@pytest.mark.asyncio
async def test_delete_cv_success(client: TestClient, test_user: DBUser, mock_db_session: AsyncMock):
    """Test successful CV deletion returns 204 No Content."""
    cv_id = uuid.uuid4()
    
    with patch("app.modules.cv.router.delete_cv") as mock_delete_cv:
        mock_delete_cv.return_value = None  # delete_cv returns None on success
        
        response = client.delete(f"/api/v1/cvs/{cv_id}")
        
        assert response.status_code == 204
        assert response.content == b""  # No content body
        mock_delete_cv.assert_called_once()
        # Verify the cv_id argument
        call_args = mock_delete_cv.call_args
        assert call_args.kwargs["cv_id"] == cv_id


@pytest.mark.asyncio
async def test_delete_cv_not_found(client: TestClient, test_user: DBUser, mock_db_session: AsyncMock):
    """Test deleting non-existent CV returns 404 Not Found."""
    from fastapi import HTTPException
    
    cv_id = uuid.uuid4()
    
    with patch("app.modules.cv.router.delete_cv") as mock_delete_cv:
        # Simulate 404 from service
        mock_delete_cv.side_effect = HTTPException(status_code=404, detail="CV not found")
        
        response = client.delete(f"/api/v1/cvs/{cv_id}")
        
        assert response.status_code == 404
        assert response.json()["detail"] == "CV not found"


@pytest.mark.asyncio
async def test_delete_cv_not_owner(client: TestClient, test_user: DBUser, mock_db_session: AsyncMock):
    """Test deleting CV owned by another user returns 404 (to prevent info disclosure)."""
    from fastapi import HTTPException
    
    cv_id = uuid.uuid4()
    
    with patch("app.modules.cv.router.delete_cv") as mock_delete_cv:
        # Service returns 404 for CV owned by another user (info disclosure prevention)
        mock_delete_cv.side_effect = HTTPException(status_code=404, detail="CV not found")
        
        response = client.delete(f"/api/v1/cvs/{cv_id}")
        
        assert response.status_code == 404
        assert response.json()["detail"] == "CV not found"


@pytest.mark.asyncio
async def test_delete_cv_unauthorized():
    """Test deleting CV without authentication returns 401 Unauthorized."""
    from fastapi.testclient import TestClient
    from app.main import app
    
    cv_id = uuid.uuid4()
    
    # Use fresh client without auth overrides
    app.dependency_overrides = {}
    
    with TestClient(app) as unauthenticated_client:
        response = unauthenticated_client.delete(f"/api/v1/cvs/{cv_id}")
        
        assert response.status_code == 401
        assert response.json()["detail"] == "Not authenticated"


@pytest.mark.asyncio
async def test_delete_cv_invalid_uuid(client: TestClient):
    """Test deleting CV with invalid UUID returns 422 Unprocessable Entity."""
    response = client.delete("/api/v1/cvs/not-a-uuid")
    
    assert response.status_code == 422  # Validation error


# ============================================================================
# GET /api/v1/cvs/{cv_id}/download Tests
# ============================================================================


@pytest.mark.asyncio
async def test_download_cv_success_pdf(client: TestClient, test_user: DBUser, mock_db_session: AsyncMock, tmp_path):
    """Test downloading a PDF CV returns file with correct content-type."""
    cv_id = uuid.uuid4()
    
    # Create a temporary PDF file
    pdf_file = tmp_path / "test_cv.pdf"
    pdf_content = b"%PDF-1.4\ntest content"
    pdf_file.write_bytes(pdf_content)
    
    with patch("app.modules.cv.router.get_cv_for_download") as mock_get_cv:
        mock_cv = MagicMock()
        mock_cv.id = cv_id
        mock_cv.user_id = test_user.id
        mock_cv.filename = "my_resume.pdf"
        mock_cv.file_path = str(pdf_file)
        
        mock_get_cv.return_value = mock_cv
        
        response = client.get(f"/api/v1/cvs/{cv_id}/download")
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"
        assert 'filename="my_resume.pdf"' in response.headers.get("content-disposition", "")
        assert response.content == pdf_content


@pytest.mark.asyncio
async def test_download_cv_success_docx(client: TestClient, test_user: DBUser, mock_db_session: AsyncMock, tmp_path):
    """Test downloading a DOCX CV returns file with correct content-type."""
    cv_id = uuid.uuid4()
    
    # Create a temporary DOCX file (just bytes for testing)
    docx_file = tmp_path / "test_cv.docx"
    docx_content = b"PK\x03\x04docx content"  # DOCX files start with PK (zip)
    docx_file.write_bytes(docx_content)
    
    with patch("app.modules.cv.router.get_cv_for_download") as mock_get_cv:
        mock_cv = MagicMock()
        mock_cv.id = cv_id
        mock_cv.user_id = test_user.id
        mock_cv.filename = "my_resume.docx"
        mock_cv.file_path = str(docx_file)
        
        mock_get_cv.return_value = mock_cv
        
        response = client.get(f"/api/v1/cvs/{cv_id}/download")
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        assert 'filename="my_resume.docx"' in response.headers.get("content-disposition", "")


@pytest.mark.asyncio
async def test_download_cv_not_found(client: TestClient, test_user: DBUser, mock_db_session: AsyncMock):
    """Test downloading non-existent CV returns 404 Not Found."""
    from fastapi import HTTPException
    
    cv_id = uuid.uuid4()
    
    with patch("app.modules.cv.router.get_cv_for_download") as mock_get_cv:
        mock_get_cv.side_effect = HTTPException(status_code=404, detail="CV not found")
        
        response = client.get(f"/api/v1/cvs/{cv_id}/download")
        
        assert response.status_code == 404
        assert response.json()["detail"] == "CV not found"


@pytest.mark.asyncio
async def test_download_cv_not_owner(client: TestClient, test_user: DBUser, mock_db_session: AsyncMock):
    """Test downloading CV owned by another user returns 403 Forbidden."""
    from fastapi import HTTPException
    
    cv_id = uuid.uuid4()
    
    with patch("app.modules.cv.router.get_cv_for_download") as mock_get_cv:
        mock_get_cv.side_effect = HTTPException(
            status_code=403, 
            detail="You do not have permission to download this CV"
        )
        
        response = client.get(f"/api/v1/cvs/{cv_id}/download")
        
        assert response.status_code == 403
        assert response.json()["detail"] == "You do not have permission to download this CV"


@pytest.mark.asyncio
async def test_download_cv_file_missing(client: TestClient, test_user: DBUser, mock_db_session: AsyncMock):
    """Test downloading CV when file is missing from disk returns 404."""
    from fastapi import HTTPException
    
    cv_id = uuid.uuid4()
    
    with patch("app.modules.cv.router.get_cv_for_download") as mock_get_cv:
        mock_get_cv.side_effect = HTTPException(
            status_code=404, 
            detail="CV file not found on server"
        )
        
        response = client.get(f"/api/v1/cvs/{cv_id}/download")
        
        assert response.status_code == 404
        assert response.json()["detail"] == "CV file not found on server"


@pytest.mark.asyncio
async def test_download_cv_unauthorized():
    """Test downloading CV without authentication returns 401 Unauthorized."""
    from fastapi.testclient import TestClient
    from app.main import app
    
    cv_id = uuid.uuid4()
    
    # Use fresh client without auth overrides
    app.dependency_overrides = {}
    
    with TestClient(app) as unauthenticated_client:
        response = unauthenticated_client.get(f"/api/v1/cvs/{cv_id}/download")
        
        assert response.status_code == 401
        assert response.json()["detail"] == "Not authenticated"


@pytest.mark.asyncio
async def test_download_cv_preserves_original_filename(client: TestClient, test_user: DBUser, mock_db_session: AsyncMock, tmp_path):
    """Test that download preserves the original filename in Content-Disposition."""
    cv_id = uuid.uuid4()
    
    # Create temp file with UUID name (as stored on disk)
    stored_file = tmp_path / f"{cv_id}.pdf"
    stored_file.write_bytes(b"%PDF-1.4\ncontent")
    
    with patch("app.modules.cv.router.get_cv_for_download") as mock_get_cv:
        mock_cv = MagicMock()
        mock_cv.id = cv_id
        mock_cv.user_id = test_user.id
        mock_cv.filename = "John_Doe_Resume_2025.pdf"  # Original user filename
        mock_cv.file_path = str(stored_file)
        
        mock_get_cv.return_value = mock_cv
        
        response = client.get(f"/api/v1/cvs/{cv_id}/download")
        
        assert response.status_code == 200
        # Should use the original filename, not the UUID
        content_disposition = response.headers.get("content-disposition", "")
        assert "John_Doe_Resume_2025.pdf" in content_disposition
        assert str(cv_id) not in content_disposition

