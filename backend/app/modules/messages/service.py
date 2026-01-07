import uuid
import logging
from typing import Optional
from datetime import datetime

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.messages.models import Conversation, Message
from app.modules.messages.schemas import (
    ConversationCreateRequest,
    ConversationResponse,
    MessageCreateRequest,
    MessageResponse,
    MessageCreateResponse,
    ConversationListItemSchema,
    UserBasicInfo,
    MessagePreview,
)
from app.modules.users.models import User

logger = logging.getLogger(__name__)


class MessageService:
    """Service layer for conversation and message operations."""

    @staticmethod
    async def create_or_get_conversation(
        db: AsyncSession,
        recruiter_id: int,
        candidate_id: int,
        initial_message: str,
    ) -> tuple[ConversationResponse, bool]:
        """
        Create a new conversation or return existing one.

        Args:
            db: Database session
            recruiter_id: ID of the recruiter
            candidate_id: ID of the candidate
            initial_message: First message content

        Returns:
            Tuple of (ConversationResponse, is_new_conversation)
        """
        # Check if conversation already exists
        existing_conversation = await db.execute(
            select(Conversation).where(
                and_(
                    Conversation.recruiter_id == recruiter_id,
                    Conversation.candidate_id == candidate_id,
                )
            )
        )
        conversation = existing_conversation.scalars().first()

        is_new = False

        if conversation:
            # Return existing conversation
            return ConversationResponse(
                id=conversation.id,
                recruiter_id=conversation.recruiter_id,
                candidate_id=conversation.candidate_id,
                created_at=conversation.created_at,
                updated_at=conversation.updated_at,
            ), False

        # Create new conversation
        conversation = Conversation(
            recruiter_id=recruiter_id,
            candidate_id=candidate_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add(conversation)
        await db.flush()  # Get ID without committing

        # Create initial message
        message = Message(
            conversation_id=conversation.id,
            sender_id=recruiter_id,
            content=initial_message,
            created_at=datetime.utcnow(),
            is_read=False,
        )
        db.add(message)
        await db.commit()
        await db.refresh(conversation)

        is_new = True
        logger.info(
            "Created new conversation %s between recruiter %d and candidate %d",
            conversation.id,
            recruiter_id,
            candidate_id,
        )

        return ConversationResponse(
            id=conversation.id,
            recruiter_id=conversation.recruiter_id,
            candidate_id=conversation.candidate_id,
            created_at=conversation.created_at,
            updated_at=conversation.updated_at,
        ), is_new

    @staticmethod
    async def save_message(
        db: AsyncSession,
        conversation_id: uuid.UUID,
        sender_id: int,
        content: str,
    ) -> MessageResponse:
        """
        Save a new message to the database.

        This function is called by the Socket.io server when a message is sent.

        Args:
            db: Database session
            conversation_id: ID of the conversation
            sender_id: ID of the message sender
            content: Message content

        Returns:
            MessageResponse with the created message
        """
        # Verify conversation exists
        conversation_result = await db.execute(
            select(Conversation).where(Conversation.id == conversation_id)
        )
        conversation = conversation_result.scalars().first()

        if not conversation:
            raise ValueError(f"Conversation {conversation_id} not found")

        # Update conversation's updated_at
        conversation.updated_at = datetime.utcnow()

        # Create message
        message = Message(
            conversation_id=conversation_id,
            sender_id=sender_id,
            content=content,
            created_at=datetime.utcnow(),
            is_read=False,
        )
        db.add(message)
        await db.commit()
        await db.refresh(message)

        logger.info(
            "Message %s saved to conversation %s by user %d",
            message.id,
            conversation_id,
            sender_id,
        )

        # Get sender name for response
        sender_result = await db.execute(
            select(User.full_name).where(User.id == sender_id)
        )
        sender_name = sender_result.scalars().first()

        return MessageResponse(
            id=message.id,
            conversation_id=message.conversation_id,
            sender_id=message.sender_id,
            content=message.content,
            created_at=message.created_at,
            is_read=message.is_read,
            sender_name=sender_name,
        )

    @staticmethod
    async def get_conversation_messages(
        db: AsyncSession,
        conversation_id: uuid.UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[MessageResponse], int]:
        """
        Get messages for a conversation (for initial load).

        Args:
            db: Database session
            conversation_id: ID of the conversation
            limit: Maximum number of messages to return
            offset: Number of messages to skip

        Returns:
            Tuple of (list of MessageResponse, total count)
        """
        # Get total count
        count_result = await db.execute(
            select(Message.id).where(Message.conversation_id == conversation_id)
        )
        total = len(count_result.scalars().all())

        # Get messages with sender info
        result = await db.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        messages = result.scalars().all()

        # Get sender names
        sender_ids = {msg.sender_id for msg in messages}
        sender_names = {}
        if sender_ids:
            users_result = await db.execute(
                select(User.id, User.full_name).where(User.id.in_(sender_ids))
            )
            sender_names = dict(users_result.fetchall())

        # Build response (reverse to get chronological order)
        message_responses = [
            MessageResponse(
                id=msg.id,
                conversation_id=msg.conversation_id,
                sender_id=msg.sender_id,
                content=msg.content,
                created_at=msg.created_at,
                is_read=msg.is_read,
                sender_name=sender_names.get(msg.sender_id),
            )
            for msg in reversed(messages)
        ]

        return message_responses, total

    @staticmethod
    async def get_conversation_by_id(
        db: AsyncSession,
        conversation_id: uuid.UUID,
    ) -> Optional[ConversationResponse]:
        """
        Get a conversation by ID with user details.

        Args:
            db: Database session
            conversation_id: ID of the conversation

        Returns:
            ConversationResponse or None if not found
        """
        from sqlalchemy.orm import selectinload
        from app.modules.users.models import User
        from app.modules.messages.schemas import UserBasicInfo
        
        result = await db.execute(
            select(Conversation)
            .options(
                selectinload(Conversation.recruiter),
                selectinload(Conversation.candidate)
            )
            .where(Conversation.id == conversation_id)
        )
        conversation = result.scalars().first()

        if not conversation:
            return None

        # Get recruiter and candidate info
        recruiter_info = None
        candidate_info = None
        
        if conversation.recruiter:
            recruiter_info = UserBasicInfo(
                id=conversation.recruiter.id,
                full_name=conversation.recruiter.full_name or conversation.recruiter.email,
                email=conversation.recruiter.email,
                role=conversation.recruiter.role,
                avatar=None  # Add avatar field to User model if needed
            )
        
        if conversation.candidate:
            candidate_info = UserBasicInfo(
                id=conversation.candidate.id,
                full_name=conversation.candidate.full_name or conversation.candidate.email,
                email=conversation.candidate.email,
                role=conversation.candidate.role,
                avatar=None  # Add avatar field to User model if needed
            )

        return ConversationResponse(
            id=conversation.id,
            recruiter_id=conversation.recruiter_id,
            candidate_id=conversation.candidate_id,
            created_at=conversation.created_at,
            updated_at=conversation.updated_at,
            recruiter=recruiter_info,
            candidate=candidate_info,
        )

    @staticmethod
    async def mark_messages_as_read(
        db: AsyncSession,
        conversation_id: uuid.UUID,
        user_id: int,
    ) -> int:
        """
        Mark all unread messages in a conversation as read for a user.

        Args:
            db: Database session
            conversation_id: ID of the conversation
            user_id: ID of the user (who is reading)

        Returns:
            Number of messages marked as read
        """
        from sqlalchemy import update

        result = await db.execute(
            update(Message)
            .where(
                and_(
                    Message.conversation_id == conversation_id,
                    Message.sender_id != user_id,  # Don't mark own messages
                    Message.is_read == False,
                )
            )
            .values(is_read=True, created_at=Message.created_at)  # Keep original created_at
        )
        await db.commit()

        marked_count = result.rowcount
        logger.info(
            "Marked %d messages as read in conversation %s for user %d",
            marked_count,
            conversation_id,
            user_id,
        )

        return marked_count

    @staticmethod
    async def get_user_conversations(
        db: AsyncSession,
        user_id: int,
        role: str,
        limit: int = 20,
    ) -> list[ConversationResponse]:
        """
        Get all conversations for a user (as recruiter or candidate).

        Args:
            db: Database session
            user_id: ID of the user
            role: 'recruiter' or 'candidate'
            limit: Maximum number of conversations to return

        Returns:
            List of ConversationResponse ordered by updated_at descending
        """
        if role == "recruiter":
            condition = Conversation.recruiter_id == user_id
        else:
            condition = Conversation.candidate_id == user_id

        result = await db.execute(
            select(Conversation)
            .where(condition)
            .order_by(Conversation.updated_at.desc())
            .limit(limit)
        )
        conversations = result.scalars().all()

        return [
            ConversationResponse(
                id=c.id,
                recruiter_id=c.recruiter_id,
                candidate_id=c.candidate_id,
                created_at=c.created_at,
                updated_at=c.updated_at,
            )
            for c in conversations
        ]

    @staticmethod
    async def get_unread_count(
        db: AsyncSession,
        user_id: int,
        role: str,
    ) -> int:
        """
        Get total unread message count for a user across all their conversations.

        Args:
            db: Database session
            user_id: ID of the user
            role: 'recruiter' or 'candidate'

        Returns:
            Total count of unread messages where user is NOT the sender
        """
        # Get user's conversation IDs
        if role == "recruiter":
            condition = Conversation.recruiter_id == user_id
        else:
            condition = Conversation.candidate_id == user_id

        # Get conversations
        result = await db.execute(
            select(Conversation.id).where(condition)
        )
        conversation_ids = [c[0] for c in result.fetchall()]

        if not conversation_ids:
            return 0

        # Count unread messages where user is NOT the sender
        from sqlalchemy import func

        result = await db.execute(
            select(func.count(Message.id))
            .where(
                and_(
                    Message.conversation_id.in_(conversation_ids),
                    Message.sender_id != user_id,
                    Message.is_read == False,
                )
            )
        )

        return result.scalar() or 0

    @staticmethod
    async def get_conversation_list_for_user(
        db: AsyncSession,
        user_id: int,
        role: str,
        limit: int = 20,
    ) -> list[ConversationListItemSchema]:
        """
        Get conversation list for user with enhanced information (Story 7.3).
        
        Returns conversations with:
        - Other participant info (name, avatar, role)
        - Last message preview
        - Unread count (messages where is_read=FALSE AND sender_id != user_id)
        - Updated timestamp
        
        Optimized with LATERAL JOIN for performance.
        
        Args:
            db: Database session
            user_id: ID of the user
            role: 'recruiter' or 'candidate'
            limit: Maximum number of conversations to return
            
        Returns:
            List of ConversationListItemSchema ordered by updated_at descending
        """
        from sqlalchemy import text, case, func
        
        # Build the optimized query with LATERAL JOIN
        query = text("""
            SELECT
                c.id::text as conversation_id,
                c.updated_at,
                -- Other participant info
                u.id as other_user_id,
                u.full_name as other_user_name,
                u.avatar as other_user_avatar,
                u.role as other_user_role,
                -- Last message
                last_msg.content as last_message_content,
                last_msg.created_at as last_message_time,
                last_msg.sender_id as last_message_sender_id,
                -- Unread count
                (
                    SELECT COUNT(*)
                    FROM messages m
                    WHERE m.conversation_id = c.id
                        AND m.is_read = FALSE
                        AND m.sender_id != :current_user_id
                ) as unread_count
            FROM conversations c
            -- Join with other participant (not current user)
            JOIN users u ON (
                CASE
                    WHEN c.recruiter_id = :current_user_id THEN u.id = c.candidate_id
                    ELSE u.id = c.recruiter_id
                END
            )
            -- Get last message using LATERAL JOIN (efficient)
            LEFT JOIN LATERAL (
                SELECT content, created_at, sender_id
                FROM messages
                WHERE conversation_id = c.id
                ORDER BY created_at DESC
                LIMIT 1
            ) last_msg ON true
            WHERE
                c.recruiter_id = :current_user_id OR c.candidate_id = :current_user_id
            ORDER BY
                c.updated_at DESC
            LIMIT :limit
        """)
        
        result = await db.execute(
            query, 
            {
                "current_user_id": user_id,
                "limit": limit
            }
        )
        
        rows = result.fetchall()
        
        conversations = []
        for row in rows:
            # Build last message preview if exists
            last_message = None
            if row.last_message_content:
                last_message = MessagePreview(
                    content=row.last_message_content,
                    timestamp=row.last_message_time,
                    sender_id=row.last_message_sender_id
                )
            
            # Build conversation list item
            conversation = ConversationListItemSchema(
                conversation_id=row.conversation_id,
                other_participant=UserBasicInfo(
                    id=row.other_user_id,
                    full_name=row.other_user_name or f"User {row.other_user_id}",
                    email="",  # Not available in this query
                    role=row.other_user_role,
                    avatar=row.other_user_avatar
                ),
                last_message=last_message,
                unread_count=row.unread_count,
                updated_at=row.updated_at
            )
            
            conversations.append(conversation)
        
        logger.info(
            "Retrieved %d conversations for user %d (role: %s)",
            len(conversations),
            user_id,
            role,
        )
        
        return conversations

    @staticmethod
    async def get_conversation_participants(
        db: AsyncSession,
        conversation_id: uuid.UUID,
    ) -> tuple[int, int]:
        """
        Get conversation participant IDs (recruiter_id, candidate_id).
        
        Used by Socket.io server to emit conversation-updated events.
        
        Args:
            db: Database session
            conversation_id: ID of the conversation
            
        Returns:
            Tuple of (recruiter_id, candidate_id)
        """
        result = await db.execute(
            select(Conversation.recruiter_id, Conversation.candidate_id)
            .where(Conversation.id == conversation_id)
        )
        
        row = result.first()
        if not row:
            raise ValueError(f"Conversation {conversation_id} not found")
            
        return row.recruiter_id, row.candidate_id
