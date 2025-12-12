import pytest
from unittest.mock import AsyncMock, MagicMock
from httpx import AsyncClient

from app.modules.ai.models import CVAnalysis, AnalysisStatus


@pytest.mark.asyncio
async def test_get_cv_analysis_status(async_client: AsyncClient, create_test_user_and_cv, mock_db_session: AsyncMock):
    """Test getting CV analysis status (user already authenticated via fixture)."""
    user, cv = create_test_user_and_cv

    # First call returns CV (ownership check), second returns status
    mock_cv_result = MagicMock()
    mock_cv_result.scalar_one_or_none.return_value = cv

    mock_status_result = MagicMock()
    mock_status_result.scalar_one_or_none.return_value = AnalysisStatus.PROCESSING

    # Configure mock to return different results for each execute call
    mock_db_session.execute.side_effect = [mock_cv_result, mock_status_result]

    # Get status - user is already authenticated via async_client fixture
    response = await async_client.get(f"/api/v1/ai/cvs/{cv.id}/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "PROCESSING"


@pytest.mark.asyncio
async def test_get_cv_analysis_not_found(async_client: AsyncClient, mock_db_session: AsyncMock):
    """Test getting analysis for non-existent CV."""
    # First call (CV ownership check) returns None - CV not found
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db_session.execute.return_value = mock_result

    # Try to get analysis for non-existent CV
    response = await async_client.get("/api/v1/ai/cvs/non-existent-id/status")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_cv_analysis_unauthorized(unauthenticated_async_client: AsyncClient, create_test_user_and_cv):
    """Test getting analysis without authentication."""
    user, cv = create_test_user_and_cv

    response = await unauthenticated_async_client.get(f"/api/v1/ai/cvs/{cv.id}/status")
    assert response.status_code == 401
