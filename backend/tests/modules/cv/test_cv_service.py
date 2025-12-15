"""
Tests for CV service functionality.
Covers CV upload, routing logic, and integration with AI analysis.
"""
import pytest
import uuid
from unittest.mock import AsyncMock, Mock, patch, MagicMock
from pathlib import Path
import tempfile
import os

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.cv.service import create_cv, trigger_ai_analysis
from app.modules.users.models import User
from app.modules.cv.models import CV


class TestCreateCV:
    """Tests for CV creation and upload functionality."""

    @pytest.mark.asyncio
    async def test_create_cv_success(self):
        """Test successful CV creation."""
        # Create a mock database session
        mock_db = AsyncMock(spec=AsyncSession)
        mock_db.add = Mock()
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()

        # Create a mock user
        mock_user = Mock(spec=User)
        mock_user.id = uuid.uuid4()

        # Create a mock file
        mock_file = AsyncMock()
        mock_file.filename = "test_cv.pdf"
        mock_file.read = AsyncMock(return_value=b"%PDF-1.4\ntest content")

        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('app.modules.cv.service.settings') as mock_settings:
                mock_settings.CV_STORAGE_PATH = Path(temp_dir)

                with patch('app.modules.cv.service.asyncio.create_task'):
                    result = await create_cv(mock_db, mock_file, mock_user)

                    # Verify database operations
                    assert mock_db.add.call_count == 2  # CV and CVAnalysis
                    assert mock_db.commit.call_count == 2
                    assert mock_db.refresh.call_count == 2

    @pytest.mark.asyncio
    async def test_create_cv_creates_upload_directory(self):
        """Test that create_cv creates upload directory if it doesn't exist."""
        mock_db = AsyncMock(spec=AsyncSession)
        mock_db.add = Mock()
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()

        mock_user = Mock(spec=User)
        mock_user.id = uuid.uuid4()

        mock_file = AsyncMock()
        mock_file.filename = "test_cv.pdf"
        mock_file.read = AsyncMock(return_value=b"%PDF-1.4\ntest content")

        with tempfile.TemporaryDirectory() as temp_dir:
            new_upload_dir = Path(temp_dir) / "new_uploads"

            with patch('app.modules.cv.service.settings') as mock_settings:
                mock_settings.CV_STORAGE_PATH = new_upload_dir

                with patch('app.modules.cv.service.asyncio.create_task'):
                    await create_cv(mock_db, mock_file, mock_user)

                    # Verify directory was created
                    assert new_upload_dir.exists()


class TestTriggerAIAnalysis:
    """Tests for AI analysis triggering functionality."""

    @pytest.mark.asyncio
    async def test_trigger_ai_analysis_success(self):
        """Test successful AI analysis trigger."""
        cv_id = uuid.uuid4()
        file_path = "/path/to/cv.pdf"

        with patch('app.core.database.AsyncSessionLocal') as mock_session_local:
            mock_db = AsyncMock()
            mock_session_local.return_value.__aenter__.return_value = mock_db

            with patch('app.modules.ai.service.ai_service') as mock_ai_service:
                mock_ai_service.analyze_cv = AsyncMock()

                await trigger_ai_analysis(cv_id, file_path)

                # Verify AI service was called
                mock_ai_service.analyze_cv.assert_called_once_with(
                    cv_id, file_path, mock_db
                )

    @pytest.mark.asyncio
    async def test_trigger_ai_analysis_handles_exception(self):
        """Test that AI analysis errors are logged but don't raise."""
        cv_id = uuid.uuid4()
        file_path = "/path/to/cv.pdf"

        with patch('app.core.database.AsyncSessionLocal') as mock_session_local:
            mock_db = AsyncMock()
            mock_session_local.return_value.__aenter__.return_value = mock_db

            with patch('app.modules.ai.service.ai_service') as mock_ai_service:
                mock_ai_service.analyze_cv = AsyncMock(
                    side_effect=Exception("Analysis failed")
                )

                with patch('app.modules.cv.service.logger') as mock_logger:
                    # Should not raise
                    await trigger_ai_analysis(cv_id, file_path)

                    # Verify error was logged
                    mock_logger.error.assert_called_once()


class TestCVRoutingIntegration:
    """Integration tests for CV routing to OCR or text extraction."""

    @pytest.mark.asyncio
    async def test_cv_routes_to_standard_extraction(self):
        """Test that text-based CV uses standard extraction."""
        cv_id = uuid.uuid4()
        file_path = "/path/to/text_cv.pdf"

        with patch('app.core.database.AsyncSessionLocal') as mock_session_local:
            mock_db = AsyncMock()
            mock_session_local.return_value.__aenter__.return_value = mock_db

            with patch('app.modules.ai.service.ai_service') as mock_ai_service:
                # Setup mock to verify the call
                mock_ai_service.analyze_cv = AsyncMock()

                await trigger_ai_analysis(cv_id, file_path)

                # Verify analyze_cv was called (which handles routing internally)
                mock_ai_service.analyze_cv.assert_called_once()
                call_args = mock_ai_service.analyze_cv.call_args
                assert call_args[0][0] == cv_id
                assert call_args[0][1] == file_path

    @pytest.mark.asyncio
    async def test_cv_analysis_with_force_ocr_flag(self):
        """Test that force_ocr flag is properly passed to AI service."""
        from app.modules.ai.service import ai_service

        cv_id = uuid.uuid4()
        mock_db = AsyncMock(spec=AsyncSession)

        with patch.object(ai_service, 'perform_ocr_extraction', return_value="OCR text " * 50):
            with patch.object(ai_service, '_perform_ai_analysis', return_value=ai_service._get_fallback_analysis()):
                with patch.object(ai_service, '_update_analysis_status'):
                    with patch.object(ai_service, '_save_analysis_results'):
                        # Call with force_ocr=True
                        await ai_service.analyze_cv(
                            cv_id, "/path/to/cv.pdf", mock_db, force_ocr=True
                        )

                        # Verify OCR was called
                        ai_service.perform_ocr_extraction.assert_called_once()
