"""Unit tests for delete_user_account service function."""

import os
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.modules.ai.models import CVAnalysis
from app.modules.cv.models import CV
from app.modules.users.models import User
from app.modules.users.services import delete_user_account


@pytest.fixture
def mock_db():
    """Create a mock async database session."""
    return AsyncMock()


def create_mock_cv(user_id: int, file_path: str | None = None, analyses: list | None = None) -> MagicMock:
    """Helper to create a mock CV with analyses."""
    cv = MagicMock(spec=CV)
    cv.id = uuid.uuid4()
    cv.user_id = user_id
    cv.file_path = file_path
    cv.analyses = analyses or []
    return cv


def create_mock_analysis(cv_id: uuid.UUID) -> MagicMock:
    """Helper to create a mock CVAnalysis."""
    analysis = MagicMock(spec=CVAnalysis)
    analysis.id = uuid.uuid4()
    analysis.cv_id = cv_id
    return analysis


class TestDeleteUserAccount:
    """Tests for delete_user_account service function."""

    @pytest.mark.asyncio
    async def test_successfully_deletes_user_and_associated_data(self, mock_db: AsyncMock):
        """Test: Successfully deletes user and all associated data."""
        user_id = 1
        file_path = "/tmp/test_cv.pdf"
        
        # Create mock CV with analyses
        analyses = [create_mock_analysis(uuid.uuid4())]
        cvs = [create_mock_cv(user_id, file_path, analyses)]

        # Mock the query result
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = cvs
        mock_db.execute.return_value = mock_result

        # Mock file exists
        with patch("os.path.exists", return_value=True), \
             patch("os.remove") as mock_remove:
            
            await delete_user_account(mock_db, user_id)

            # Verify file was deleted
            mock_remove.assert_called_once_with(file_path)

        # Verify database operations were called
        assert mock_db.execute.call_count == 4  # 1 select + 3 deletes
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_deletes_cv_analyses_manually_no_cascade(self, mock_db: AsyncMock):
        """Test: Deletes CVAnalyses manually (no CASCADE constraint)."""
        user_id = 1
        cv_id = uuid.uuid4()
        analysis_id = uuid.uuid4()
        
        # Create mock CV with analysis
        analysis = create_mock_analysis(cv_id)
        analysis.id = analysis_id
        cvs = [create_mock_cv(user_id, analyses=[analysis])]

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = cvs
        mock_db.execute.return_value = mock_result

        with patch("os.path.exists", return_value=False):  # No file to delete
            await delete_user_account(mock_db, user_id)

        # Verify CVAnalysis delete was called
        # Since mock_db.execute returns the same mock_result for all calls, we check call count
        # In practice, the function calls execute 4 times: select, delete analyses, delete cvs, delete user
        assert mock_db.execute.call_count == 4

    @pytest.mark.asyncio
    async def test_deletes_cvs_manually_no_cascade(self, mock_db: AsyncMock):
        """Test: Deletes CVs manually (no CASCADE constraint)."""
        user_id = 1
        cv_id = uuid.uuid4()
        
        cvs = [create_mock_cv(user_id)]

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = cvs
        mock_db.execute.return_value = mock_result

        with patch("os.path.exists", return_value=False):
            await delete_user_account(mock_db, user_id)

        # Verify CV delete was called - 3 calls: select, delete cvs, delete user
        assert mock_db.execute.call_count == 3

    @pytest.mark.asyncio
    async def test_deletes_files_from_storage(self, mock_db: AsyncMock):
        """Test: Deletes associated files from local storage."""
        user_id = 1
        file_paths = ["/tmp/cv1.pdf", "/tmp/cv2.pdf"]
        
        cvs = [
            create_mock_cv(user_id, file_paths[0]),
            create_mock_cv(user_id, file_paths[1])
        ]

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = cvs
        mock_db.execute.return_value = mock_result

        with patch("os.path.exists", return_value=True), \
             patch("os.remove") as mock_remove:
            
            await delete_user_account(mock_db, user_id)

            # Verify both files were deleted
            assert mock_remove.call_count == 2
            mock_remove.assert_any_call(file_paths[0])
            mock_remove.assert_any_call(file_paths[1])

    @pytest.mark.asyncio
    async def test_handles_file_deletion_errors_gracefully(self, mock_db: AsyncMock):
        """Test: Handles file deletion errors gracefully (continues with DB deletion)."""
        user_id = 1
        file_path = "/tmp/test_cv.pdf"
        
        cvs = [create_mock_cv(user_id, file_path)]

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = cvs
        mock_db.execute.return_value = mock_result

        with patch("os.path.exists", return_value=True), \
             patch("os.remove", side_effect=OSError("Permission denied")):
            
            # Should not raise exception
            await delete_user_account(mock_db, user_id)

            # Should still commit DB changes
            mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_handles_user_with_no_cvs(self, mock_db: AsyncMock):
        """Test: Handles user with no CVs (only deletes user)."""
        user_id = 1
        cvs = []  # No CVs

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = cvs
        mock_db.execute.return_value = mock_result

        await delete_user_account(mock_db, user_id)

        # Should still delete user - execute called 2 times: select (empty), delete user
        assert mock_db.execute.call_count == 2
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_handles_cvs_with_no_file_path(self, mock_db: AsyncMock):
        """Test: Handles CVs with no file_path gracefully."""
        user_id = 1
        
        cvs = [
            create_mock_cv(user_id, None),  # No file_path
            create_mock_cv(user_id, "")     # Empty file_path
        ]

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = cvs
        mock_db.execute.return_value = mock_result

        with patch("os.path.exists", return_value=False), \
             patch("os.remove") as mock_remove:
            
            await delete_user_account(mock_db, user_id)

            # Should not attempt to delete files
            mock_remove.assert_not_called()