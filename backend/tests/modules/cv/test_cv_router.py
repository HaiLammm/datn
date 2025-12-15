import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from fastapi.testclient import TestClient

from app.core.config import settings
from app.modules.users.models import User as DBUser


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

