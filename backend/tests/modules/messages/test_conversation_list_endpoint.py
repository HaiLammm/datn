"""
Unit tests for Conversation List API Endpoint (Story 7.3)
Tests the new conversation list endpoint with last message, unread count, and other participant info.
"""
import uuid
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app


class TestConversationListEndpoint:
    """Tests for GET /conversations endpoint with enhanced data (Story 7.3)."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)

    @pytest.fixture
    def mock_current_user(self):
        """Mock authenticated user (recruiter)."""
        user = AsyncMock()
        user.id = 1
        user.role = "recruiter"
        user.email = "recruiter@test.com"
        user.full_name = "Test Recruiter"
        user.is_active = True
        return user

    @pytest.fixture
    def sample_conversation_data(self):
        """Sample conversation data that would be returned by the new service method."""
        conv_id = uuid.uuid4()
        return {
            "conversation_id": str(conv_id),
            "other_participant": {
                "id": 2,
                "name": "Test Candidate",
                "avatar": None,
                "role": "candidate"
            },
            "last_message": {
                "content": "Hello! I'm interested in this position.",
                "timestamp": datetime.utcnow(),
                "sender_id": 2
            },
            "unread_count": 1,
            "updated_at": datetime.utcnow()
        }

    @pytest.mark.asyncio
    async def test_get_conversations_empty_list(self, client, mock_current_user):
        """Test that empty list is returned when user has no conversations."""
        # Arrange
        with patch("app.modules.messages.router.get_current_user", return_value=mock_current_user):
            with patch("app.modules.messages.router.MessageService.get_conversation_list_for_user") as mock_service:
                mock_service.return_value = []
                
                # Act
                response = client.get("/api/v1/messages/conversations")
                
                # Assert
                assert response.status_code == 200
                data = response.json()
                assert data == []

    @pytest.mark.asyncio
    async def test_get_conversations_returns_correct_schema(self, client, mock_current_user, sample_conversation_data):
        """Test that GET /conversations returns ConversationListItemSchema format."""
        # Arrange
        with patch("app.modules.messages.router.get_current_user", return_value=mock_current_user):
            with patch("app.modules.messages.router.MessageService.get_conversation_list_for_user") as mock_service:
                mock_service.return_value = [sample_conversation_data]
                
                # Act
                response = client.get("/api/v1/messages/conversations")
                
                # Assert
                assert response.status_code == 200
                data = response.json()
                
                assert len(data) == 1
                conversation = data[0]
                
                # Verify ConversationListItemSchema structure
                assert "conversation_id" in conversation
                assert "other_participant" in conversation
                assert "last_message" in conversation
                assert "unread_count" in conversation
                assert "updated_at" in conversation
                
                # Verify other_participant structure
                other_participant = conversation["other_participant"]
                assert "id" in other_participant
                assert "name" in other_participant
                assert "avatar" in other_participant
                assert "role" in other_participant
                
                # Verify last_message structure
                last_message = conversation["last_message"]
                assert "content" in last_message
                assert "timestamp" in last_message
                assert "sender_id" in last_message
                
                assert conversation["unread_count"] == 1