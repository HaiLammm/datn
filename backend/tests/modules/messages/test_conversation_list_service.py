"""
Unit tests for MessageService.get_conversation_list_for_user method (Story 7.3)
"""
import uuid
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.modules.messages.service import MessageService


class TestConversationListService:
    """Tests for MessageService.get_conversation_list_for_user method."""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database session."""
        return AsyncMock()

    @pytest.fixture
    def sample_query_result(self):
        """Mock SQL query result."""
        row = MagicMock()
        row.conversation_id = str(uuid.uuid4())
        row.updated_at = datetime.utcnow()
        row.other_user_id = 2
        row.other_user_name = "Test Candidate"
        row.other_user_avatar = None
        row.other_user_role = "candidate"
        row.last_message_content = "Hello! I'm interested in this position."
        row.last_message_time = datetime.utcnow()
        row.last_message_sender_id = 2
        row.unread_count = 1
        return [row]

    @pytest.mark.asyncio
    async def test_get_conversation_list_for_user_returns_empty_list(self, mock_db):
        """Test that service returns empty list when no conversations exist."""
        # Arrange
        mock_db.execute.return_value.fetchall.return_value = []
        
        # Act
        result = await MessageService.get_conversation_list_for_user(
            db=mock_db,
            user_id=1,
            role="recruiter",
            limit=20
        )
        
        # Assert
        assert result == []
        mock_db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_conversation_list_for_user_returns_correct_schema(self, mock_db, sample_query_result):
        """Test that service returns ConversationListItemSchema with correct structure."""
        # Arrange
        mock_db.execute.return_value.fetchall.return_value = sample_query_result
        
        # Act
        result = await MessageService.get_conversation_list_for_user(
            db=mock_db,
            user_id=1,
            role="recruiter",
            limit=20
        )
        
        # Assert
        assert len(result) == 1
        conversation = result[0]
        
        # Verify ConversationListItemSchema structure
        assert hasattr(conversation, 'conversation_id')
        assert hasattr(conversation, 'other_participant')
        assert hasattr(conversation, 'last_message')
        assert hasattr(conversation, 'unread_count')
        assert hasattr(conversation, 'updated_at')
        
        # Verify other_participant structure
        other_participant = conversation.other_participant
        assert other_participant.id == 2
        assert other_participant.name == "Test Candidate"
        assert other_participant.avatar is None
        assert other_participant.role == "candidate"
        
        # Verify last_message structure
        last_message = conversation.last_message
        assert last_message.content == "Hello! I'm interested in this position."
        assert last_message.sender_id == 2
        
        # Verify unread_count
        assert conversation.unread_count == 1

    @pytest.mark.asyncio
    async def test_get_conversation_list_for_user_handles_no_last_message(self, mock_db):
        """Test that service handles conversations with no last message."""
        # Arrange
        row = MagicMock()
        row.conversation_id = str(uuid.uuid4())
        row.updated_at = datetime.utcnow()
        row.other_user_id = 2
        row.other_user_name = "Test Candidate"
        row.other_user_avatar = None
        row.other_user_role = "candidate"
        row.last_message_content = None  # No last message
        row.last_message_time = None
        row.last_message_sender_id = None
        row.unread_count = 0
        
        mock_db.execute.return_value.fetchall.return_value = [row]
        
        # Act
        result = await MessageService.get_conversation_list_for_user(
            db=mock_db,
            user_id=1,
            role="recruiter",
            limit=20
        )
        
        # Assert
        assert len(result) == 1
        conversation = result[0]
        
        # last_message should be None when no messages exist
        assert conversation.last_message is None
        assert conversation.unread_count == 0