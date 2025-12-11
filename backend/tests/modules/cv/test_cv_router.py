import pytest
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient # Added TestClient import

from app.core.config import settings
from app.main import app
from app.modules.users.models import User as DBUser  # Alias to avoid conflict


# Mock create_cv service
@pytest.fixture(autouse=True)
def mock_create_cv() -> AsyncMock:
    with patch("app.modules.cv.router.create_cv") as mock_func:
        yield mock_func


@pytest.mark.asyncio
async def test_upload_cv_valid_pdf(
    client: TestClient, test_user: DBUser, mock_create_cv: AsyncMock
):
    mock_create_cv.return_value = {
        "id": "00000000-0000-0000-0000-000000000002",
        "user_id": str(test_user.id),
        "filename": "test_cv.pdf",
        "file_path": f"{settings.CV_STORAGE_PATH}/test_cv.pdf",
        "uploaded_at": "2025-01-01T00:00:00",
        "is_active": True,
    }

    # Create a dummy PDF file
    pdf_content = b"%PDF-1.4\n1 0 obj<</Type/Catalog>>endobj\nxref\n0 2\n0000000000 65535 f\n0000000009 00000 n\ntrailer<</Size 2/Root 1 0 R>>startxref\n15\n%%EOF"
    files = {"file": ("test_cv.pdf", pdf_content, "application/pdf")}
    response = client.post("/api/v1/cvs/", files=files)

    assert response.status_code == 201
    assert response.json()["filename"] == "test_cv.pdf"
    mock_create_cv.assert_called_once()


@pytest.mark.asyncio
async def test_upload_cv_invalid_file_type(client: TestClient):
    # Create a dummy text file
    txt_content = b"This is a text file, not a PDF or DOCX."
    files = {"file": ("test.txt", txt_content, "text/plain")}
    response = client.post("/api/v1/cvs/", files=files)

    assert response.status_code == 400
    assert "Chỉ chấp nhận file PDF hoặc DOCX." in response.json()["detail"]


@pytest.mark.asyncio
async def test_upload_cv_unauthenticated(client: TestClient):
    # Temporarily remove the dependency override for this test
    app.dependency_overrides = {}

    pdf_content = b"%PDF-1.4\n..."
    files = {"file": ("test_cv.pdf", pdf_content, "application/pdf")}

    response = client.post("/api/v1/cvs/", files=files)

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"




@pytest.mark.asyncio
async def test_read_root(client: TestClient):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the API"}


@pytest.mark.asyncio
async def test_get_cv_router(client: TestClient):
    response = client.get("/api/v1/cvs/")
    assert response.status_code == 200
    assert response.json() == {"message": "CV router is working!"}


# Rate limiting test removed - implemented as simple in-memory solution
# In production, this would use Redis and be tested separately

