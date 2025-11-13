from pydantic import BaseModel
from datetime import datetime


class MessageCreate(BaseModel):
    """Schema for creating a new message"""
    content: str


class MessageResponse(BaseModel):
    """Schema for message response"""
    message_id: int
    conversation_id: int
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


class MessageUpdate(BaseModel):
    """Schema for updating a message"""
    content: str