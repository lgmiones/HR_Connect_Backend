"""
Simple Pydantic schemas for authentication
"""

from pydantic import BaseModel, EmailStr


class UserRegister(BaseModel):
    """User registration"""
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    """User login"""
    email: EmailStr
    password: str


class Token(BaseModel):
    """Token response"""
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    """User response without password"""
    user_id: int
    email: str
    
    class Config:
        from_attributes = True