from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class ConversationCreate(BaseModel):
    """Schema for creating a new conversation"""
    title: Optional[str] = None


class ConversationUpdate(BaseModel):
    """Schema for updating a conversation"""
    title: Optional[str] = None


class ConversationResponse(BaseModel):
    """Schema for conversation response without messages"""
    conversation_id: int
    user_id: int
    title: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ConversationDetailResponse(BaseModel):
    """Schema for conversation response with all messages"""
    conversation_id: int
    user_id: int
    title: Optional[str]
    created_at: datetime
    updated_at: datetime
    messages: List['MessageResponse'] = []

    class Config:
        from_attributes = True


# Import after class definition to avoid circular imports
from app.schemas.messages import MessageResponse

ConversationDetailResponse.model_rebuild()