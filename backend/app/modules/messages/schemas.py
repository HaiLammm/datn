from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


# ============ Conversation Schemas ============


class ConversationCreateRequest(BaseModel):
    """Schema for creating a new conversation."""

    candidate_id: int = Field(..., description="ID of the candidate to start conversation with")
    initial_message: str = Field(..., min_length=1, max_length=5000, description="First message content")


class UserBasicInfo(BaseModel):
    """Schema for basic user information."""
    
    id: int
    full_name: str
    email: str
    role: str
    avatar: Optional[str] = None


class ConversationResponse(BaseModel):
    """Schema for conversation response."""

    id: UUID
    recruiter_id: int
    candidate_id: int
    created_at: datetime
    updated_at: datetime
    recruiter: Optional[UserBasicInfo] = None
    candidate: Optional[UserBasicInfo] = None

    class Config:
        from_attributes = True


class ConversationWithMessages(ConversationResponse):
    """Schema for conversation with its messages."""

    messages: List["MessageResponse"] = []


class ConversationWithDetails(ConversationResponse):
    """Schema for conversation response with additional details."""

    unread_count: int = 0
    last_message: Optional["MessageResponse"] = None
    other_user_name: Optional[str] = None


class UnreadCountResponse(BaseModel):
    """Schema for unread count response."""

    unread_count: int


# ============ Message Schemas ============


class MessageCreateRequest(BaseModel):
    """Schema for creating a new message."""

    conversation_id: UUID = Field(..., description="ID of the conversation")
    content: str = Field(..., min_length=1, max_length=5000, description="Message content")


class MessageResponse(BaseModel):
    """Schema for message response."""

    id: UUID
    conversation_id: UUID
    sender_id: int
    content: str
    created_at: datetime
    is_read: bool
    sender_name: Optional[str] = None  # Populated from User relationship

    class Config:
        from_attributes = True


class MessageCreateResponse(BaseModel):
    """Schema for message creation response from Socket.io server."""

    id: UUID
    conversation_id: UUID
    sender_id: int
    content: str
    created_at: datetime
    is_read: bool


# ============ Message List Schemas ============


class ConversationListResponse(BaseModel):
    """Schema for list of conversations for a user."""

    conversations: List[ConversationWithMessages]
    total: int


class MessageListResponse(BaseModel):
    """Schema for list of messages in a conversation."""

    messages: List[MessageResponse]
    total: int


# ============ Auth Verification Schemas ============
# Note: JWT TokenPayload is imported from auth module to maintain consistency


class AuthVerifyResponse(BaseModel):
    """Response from auth verification endpoint."""

    id: int
    email: str
    role: str
    full_name: Optional[str] = None
    is_active: bool


# ============ Story 7.3: Conversation List Schemas ============
# Note: UserBasicInfo is defined above (line 18-24)


class MessagePreview(BaseModel):
    """Preview of message for conversation list."""
    
    content: str
    timestamp: datetime
    sender_id: int


class ConversationListItemSchema(BaseModel):
    """Schema for conversation list item (Story 7.3)."""
    
    conversation_id: str  # UUID as string for JSON serialization
    other_participant: UserBasicInfo
    last_message: Optional[MessagePreview] = None
    unread_count: int = 0
    updated_at: datetime


# ============ Update forward references ============


ConversationWithMessages.model_rebuild()
