"""
Unit tests for Message Service
"""
import uuid
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.messages.models import Conversation, Message
from app.modules.messages.service import MessageService
from app.modules.messages.schemas import (
    ConversationCreateRequest,
    MessageCreateRequest,
)


class TestMessageService:
    """Tests for MessageService class."""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database session."""
        db = AsyncMock(spec=AsyncSession)
        return db

    @pytest.fixture
    def sample_conversation(self):
        """Create a sample conversation object."""
        return Conversation(
            id=uuid.uuid4(),
            recruiter_id=1,
            candidate_id=2,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

    @pytest.fixture
    def sample_user(self):
        """Create a sample user object."""
        user = MagicMock()
        user.id = 1
        user.full_name = "Test User"
        user.email = "test@example.com"
        return user

    @pytest.mark.asyncio
    async def test_create_or_get_conversation_creates_new(self, mock_db):
        """Test creating a new conversation when none exists."""
        # Setup mock to return None for existing conversation check
        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = None
        mock_db.execute = AsyncMock(return_value=mock_result)
        
        # Mock flush to set conversation ID
        def mock_flush():
            # Find the conversation object that was added
            for call in mock_db.add.call_args_list:
                obj = call[0][0]  # First positional argument
                if hasattr(obj, 'recruiter_id') and hasattr(obj, 'candidate_id'):
                    obj.id = uuid.uuid4()  # Set a real UUID

        mock_db.flush = AsyncMock(side_effect=mock_flush)
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()

        # Call the service
        with patch('app.modules.messages.service.datetime') as mock_datetime:
            mock_datetime.utcnow.return_value = datetime(2024, 1, 1, 12, 0, 0)
            
            conversation, is_new = await MessageService.create_or_get_conversation(
                db=mock_db,
                recruiter_id=1,
                candidate_id=2,
                initial_message="Hello, I would like to discuss the position.",
            )

            # Assertions
            assert is_new is True
            assert conversation.recruiter_id == 1
            assert conversation.candidate_id == 2
            assert conversation.id is not None
            mock_db.add.assert_called()
            mock_db.flush.assert_called()
            mock_db.commit.assert_called()

    @pytest.mark.asyncio
    async def test_create_or_get_conversation_returns_existing(self, mock_db, sample_conversation):
        """Test returning existing conversation."""
        # Setup mock to return existing conversation
        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = sample_conversation

        mock_db.execute = AsyncMock(return_value=mock_result)

        with patch('app.modules.messages.service.select') as mock_select:
            mock_select.return_value = MagicMock(
                where=MagicMock(return_value=MagicMock(
                    scalars=MagicMock(return_value=MagicMock(first=MagicMock(return_value=sample_conversation)))
                ))
            )

            # Call the service
            conversation, is_new = await MessageService.create_or_get_conversation(
                db=mock_db,
                recruiter_id=1,
                candidate_id=2,
                initial_message="Hello, I would like to discuss the position.",
            )

            # Assertions
            assert is_new is False
            assert conversation.id == sample_conversation.id
            mock_db.add.assert_not_called()

    @pytest.mark.asyncio
    async def test_save_message_success(self, mock_db, sample_conversation):
        """Test saving a new message."""
        # Setup mocks for database operations
        mock_conversation_result = MagicMock()
        mock_conversation_result.scalars.return_value.first.return_value = sample_conversation
        
        mock_sender_result = MagicMock()
        mock_sender_result.scalars.return_value.first.return_value = "Test User"
        
        mock_db.execute = AsyncMock(side_effect=[
            mock_conversation_result,  # For conversation lookup
            mock_sender_result,        # For sender name lookup
        ])
        mock_db.commit = AsyncMock()
        mock_db.add = MagicMock()

        def mock_refresh(obj):
            if hasattr(obj, 'conversation_id'):  # It's a message
                obj.id = uuid.uuid4()

        mock_db.refresh = AsyncMock(side_effect=mock_refresh)

        # Call the service
        with patch('app.modules.messages.service.datetime') as mock_datetime:
            mock_datetime.utcnow.return_value = datetime(2024, 1, 1, 12, 0, 0)
            
            message = await MessageService.save_message(
                db=mock_db,
                conversation_id=sample_conversation.id,
                sender_id=1,
                content="Test message",
            )

            # Assertions
            assert message.content == "Test message"
            assert message.sender_name == "Test User"
            mock_db.add.assert_called()
            mock_db.commit.assert_called()

    @pytest.mark.asyncio
    async def test_save_message_conversation_not_found(self, mock_db):
        """Test saving message to non-existent conversation."""
        # Setup mock to return no conversation
        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = None
        mock_db.execute = AsyncMock(return_value=mock_result)

        with patch('app.modules.messages.service.select') as mock_select:
            mock_select.return_value = MagicMock(
                where=MagicMock(return_value=MagicMock(
                    scalars=MagicMock(return_value=MagicMock(first=MagicMock(return_value=None)))
                ))
            )

            # Call the service and expect ValueError
            with pytest.raises(ValueError, match="Conversation .* not found"):
                await MessageService.save_message(
                    db=mock_db,
                    conversation_id=uuid.uuid4(),
                    sender_id=1,
                    content="Test message",
                )

    @pytest.mark.asyncio
    async def test_get_conversation_messages(self, mock_db, sample_conversation):
        """Test getting messages for a conversation."""
        # Setup mocks
        mock_count_result = MagicMock()
        mock_count_result.scalars.return_value.all.return_value = [1, 2, 3]

        mock_messages_result = MagicMock()
        mock_messages = [
            MagicMock(
                id=uuid.uuid4(),
                conversation_id=sample_conversation.id,
                sender_id=1,
                content="Message 1",
                created_at=datetime.utcnow(),
                is_read=False,
            ),
            MagicMock(
                id=uuid.uuid4(),
                conversation_id=sample_conversation.id,
                sender_id=2,
                content="Message 2",
                created_at=datetime.utcnow(),
                is_read=True,
            ),
        ]
        mock_messages_result.scalars.return_value.all.return_value = mock_messages

        mock_user_result = MagicMock()
        mock_user_result.fetchall.return_value = [(1, "User 1"), (2, "User 2")]

        mock_db.execute = AsyncMock(side_effect=[
            mock_count_result,
            mock_messages_result,
            mock_user_result,
        ])

        with patch('app.modules.messages.service.select') as mock_select:
            # Setup the mocks
            mock_select.return_value = MagicMock(
                where=MagicMock(return_value=MagicMock(
                    order_by=MagicMock(return_value=MagicMock(
                        offset=MagicMock(return_value=MagicMock(
                            limit=MagicMock(return_value=MagicMock(
                                scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=mock_messages)))
                            ))
                        ))
                    ))
                ))
            )

            # Call the service
            messages, total = await MessageService.get_conversation_messages(
                db=mock_db,
                conversation_id=sample_conversation.id,
            )

            # Assertions
            assert total == 3
            assert len(messages) == 2

    @pytest.mark.asyncio
    async def test_get_conversation_by_id_found(self, mock_db, sample_conversation):
        """Test getting a conversation by ID."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = sample_conversation
        mock_db.execute = AsyncMock(return_value=mock_result)

        with patch('app.modules.messages.service.select') as mock_select:
            mock_select.return_value = MagicMock(
                where=MagicMock(return_value=MagicMock(
                    scalars=MagicMock(return_value=MagicMock(first=MagicMock(return_value=sample_conversation)))
                ))
            )

            # Call the service
            conversation = await MessageService.get_conversation_by_id(
                db=mock_db,
                conversation_id=sample_conversation.id,
            )

            # Assertions
            assert conversation is not None
            assert conversation.id == sample_conversation.id

    @pytest.mark.asyncio
    async def test_get_conversation_by_id_not_found(self, mock_db):
        """Test getting a non-existent conversation by ID."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = None
        mock_db.execute = AsyncMock(return_value=mock_result)

        with patch('app.modules.messages.service.select') as mock_select:
            mock_select.return_value = MagicMock(
                where=MagicMock(return_value=MagicMock(
                    scalars=MagicMock(return_value=MagicMock(first=MagicMock(return_value=None)))
                ))
            )

            # Call the service
            conversation = await MessageService.get_conversation_by_id(
                db=mock_db,
                conversation_id=uuid.uuid4(),
            )

            # Assertions
            assert conversation is None


class TestConversationModel:
    """Tests for Conversation model."""

    def test_conversation_table_name(self):
        """Test Conversation model table name."""
        assert Conversation.__tablename__ == "conversations"

    def test_conversation_columns(self):
        """Test Conversation model has required columns."""
        assert hasattr(Conversation, "id")
        assert hasattr(Conversation, "recruiter_id")
        assert hasattr(Conversation, "candidate_id")
        assert hasattr(Conversation, "created_at")
        assert hasattr(Conversation, "updated_at")


class TestMessageModel:
    """Tests for Message model."""

    def test_message_table_name(self):
        """Test Message model table name."""
        assert Message.__tablename__ == "messages"

    def test_message_columns(self):
        """Test Message model has required columns."""
        assert hasattr(Message, "id")
        assert hasattr(Message, "conversation_id")
        assert hasattr(Message, "sender_id")
        assert hasattr(Message, "content")
        assert hasattr(Message, "created_at")
        assert hasattr(Message, "is_read")


class TestSchemas:
    """Tests for Pydantic schemas."""

    def test_conversation_create_request_schema(self):
        """Test ConversationCreateRequest schema."""
        data = ConversationCreateRequest(
            candidate_id=1,
            initial_message="Hello, I would like to discuss the position.",
        )
        assert data.candidate_id == 1
        assert "discuss" in data.initial_message

    def test_conversation_create_request_validation(self):
        """Test ConversationCreateRequest validation."""
        with pytest.raises(ValueError):
            ConversationCreateRequest(
                candidate_id=1,
                initial_message="",  # Empty message should fail
            )

    def test_message_create_request_schema(self):
        """Test MessageCreateRequest schema."""
        data = MessageCreateRequest(
            conversation_id=uuid.uuid4(),
            content="This is a test message",
        )
        assert "test" in data.content
