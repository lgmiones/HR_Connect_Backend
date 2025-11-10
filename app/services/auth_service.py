"""
Authentication Service
Business logic for authentication operations
"""

from datetime import timedelta
from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.core.config import settings

from app.core.auth_utils import (
    verify_password,
    get_password_hash,
    create_access_token
)
from app.repositories.user_repository import UserRepository
from app.models.user import User
from app.schemas.auth_schemas import UserRegister, UserLogin, Token


class AuthService:
    """Authentication service"""
    
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
    
    def register_user(self, user_data: UserRegister) -> User:
        """Register a new user"""
        # Check if email already exists
        if self.user_repo.email_exists(user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Hash password
        hashed_password = get_password_hash(user_data.password)
        
        # Create user using repository
        new_user = self.user_repo.create_user(
            email=user_data.email,
            hashed_password=hashed_password
        )
        
        return new_user
    
    def authenticate_user(self, credentials: UserLogin) -> Token:
        """Authenticate user and return JWT token"""
        # Get user by email
        user = self.user_repo.get_by_email(credentials.email)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        # Verify password
        if not verify_password(credentials.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        # Create access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"user_id": user.user_id, "email": user.email},
            expires_delta=access_token_expires
        )
        
        return Token(access_token=access_token, token_type="bearer")