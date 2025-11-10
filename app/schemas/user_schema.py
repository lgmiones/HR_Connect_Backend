"""
Pydantic schemas for User
"""
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional


class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr


class UserCreate(UserBase):
    """Schema for user creation"""
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")


class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str


class UserResponse(UserBase):
    """Schema for user response"""
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserWithLeaveBalance(UserResponse):
    """Schema for user with leave balance information"""
    total_leaves: Optional[int] = None
    used_leaves: Optional[int] = None
    remaining_leaves: Optional[int] = None
    
    class Config:
        from_attributes = True
