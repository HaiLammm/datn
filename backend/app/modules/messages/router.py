import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.messages.schemas import (
    ConversationCreateRequest,
    ConversationResponse,
    MessageCreateRequest,
    MessageResponse,
    MessageListResponse,
    AuthVerifyResponse,
    ConversationListItemSchema,
)
from app.modules.messages.service import MessageService
from app.modules.users.models import User

router = APIRouter()


@router.post("/conversations", response_model=ConversationResponse)
async def create_conversation(
    request: ConversationCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new conversation or get existing one with a candidate.
    The initial message is automatically sent.
    """
    if current_user.role != "recruiter":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only recruiters can initiate conversations",
        )

    conversation, is_new = await MessageService.create_or_get_conversation(
        db=db,
        recruiter_id=current_user.id,
        candidate_id=request.candidate_id,
        initial_message=request.initial_message,
    )

    return conversation


@router.get("/conversations", response_model=list[ConversationListItemSchema])
async def get_conversations(
    limit: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get conversation list for current user with enhanced information (Story 7.3).
    
    Returns conversations with:
    - Other participant info (name, avatar, role)  
    - Last message preview
    - Unread count (messages not sent by current user)
    - Sorted by updated_at DESC (newest first)
    """
    conversations = await MessageService.get_conversation_list_for_user(
        db=db,
        user_id=current_user.id,
        role=current_user.role,
        limit=limit,
    )

    return conversations


@router.get("/conversations/unread-count")
async def get_unread_count(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get the total unread message count for the current user.
    Returns the count of unread messages across all conversations.
    """
    unread_count = await MessageService.get_unread_count(
        db=db,
        user_id=current_user.id,
        role=current_user.role,
    )

    return {"unread_count": unread_count}


@router.post("/messages", response_model=MessageResponse)
async def create_message(
    request: MessageCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new message in a conversation.
    This endpoint is primarily called by the Socket.io server.
    """
    try:
        message = await MessageService.save_message(
            db=db,
            conversation_id=request.conversation_id,
            sender_id=current_user.id,
            content=request.content,
        )
        return message
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.get("/conversations/{conversation_id}/messages", response_model=MessageListResponse)
async def get_conversation_messages(
    conversation_id: uuid.UUID,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all messages in a conversation (for initial load).
    """
    # Verify conversation exists and user has access
    conversation = await MessageService.get_conversation_by_id(
        db=db,
        conversation_id=conversation_id,
    )

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    # Check user is part of the conversation
    if (
        current_user.id != conversation.recruiter_id
        and current_user.id != conversation.candidate_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this conversation",
        )

    messages, total = await MessageService.get_conversation_messages(
        db=db,
        conversation_id=conversation_id,
        limit=limit,
        offset=offset,
    )

    return MessageListResponse(messages=messages, total=total)


@router.post("/conversations/{conversation_id}/read")
async def mark_conversation_read(
    conversation_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Mark all messages in a conversation as read.
    """
    # Verify conversation exists and user has access
    conversation = await MessageService.get_conversation_by_id(
        db=db,
        conversation_id=conversation_id,
    )

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    if (
        current_user.id != conversation.recruiter_id
        and current_user.id != conversation.candidate_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this conversation",
        )

    marked_count = await MessageService.mark_messages_as_read(
        db=db,
        conversation_id=conversation_id,
        user_id=current_user.id,
    )

    return {"marked_count": marked_count}


@router.patch("/conversations/{conversation_id}/mark-read")
async def mark_conversation_read_patch(
    conversation_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Mark all messages in a conversation as read (Story 7.3 PATCH endpoint).
    
    Returns the updated unread count for the conversation.
    """
    # Verify conversation exists and user has access
    conversation = await MessageService.get_conversation_by_id(
        db=db,
        conversation_id=conversation_id,
    )

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    if (
        current_user.id != conversation.recruiter_id
        and current_user.id != conversation.candidate_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this conversation",
        )

    marked_count = await MessageService.mark_messages_as_read(
        db=db,
        conversation_id=conversation_id,
        user_id=current_user.id,
    )

    # Return updated unread count (should be 0 after marking as read)
    return {"unread_count": 0, "marked_count": marked_count}


@router.get("/conversations/{conversation_id}/participants")
async def get_conversation_participants(
    conversation_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get conversation participants (for Socket.io server use).
    
    Returns recruiter_id and candidate_id for the conversation.
    """
    try:
        recruiter_id, candidate_id = await MessageService.get_conversation_participants(
            db=db,
            conversation_id=conversation_id,
        )
        
        return {
            "conversation_id": str(conversation_id),
            "recruiter_id": recruiter_id,
            "candidate_id": candidate_id,
            "participants": [recruiter_id, candidate_id]
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.get("/auth/verify", response_model=AuthVerifyResponse)
async def verify_auth(
    current_user: User = Depends(get_current_user),
):
    """
    Verify JWT token and return user information.
    This endpoint is called by the Socket.io server to authenticate connections.
    """
    return AuthVerifyResponse(
        id=current_user.id,
        email=current_user.email,
        role=current_user.role,
        full_name=current_user.full_name,
        is_active=current_user.is_active,
    )

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    if (
        current_user.id != conversation.recruiter_id
        and current_user.id != conversation.candidate_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this conversation",
        )

    marked_count = await MessageService.mark_messages_as_read(
        db=db,
        conversation_id=conversation_id,
        user_id=current_user.id,
    )

    # Return updated unread count (should be 0 after marking as read)
    return {"unread_count": 0, "marked_count": marked_count}

