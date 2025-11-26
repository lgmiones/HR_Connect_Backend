"""
Authentication Service
Business logic for authentication operations
"""

from datetime import timedelta, datetime, timezone  # Add timezone import
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
        if self.user_repo.email_exists(user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        hashed_password = get_password_hash(user_data.password)
        new_user = self.user_repo.create_user(
            email=user_data.email,
            hashed_password=hashed_password
        )
        
        return new_user
    
    def authenticate_user(self, credentials: UserLogin) -> Token:
        """Authenticate user and return JWT token"""
        user = self.user_repo.get_by_email(credentials.email)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        if not verify_password(credentials.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        # FIRST LOGIN WINS: Check if user already has an active session
        if user.current_token_jti is not None and user.token_expires_at is not None:
            # Get current time with UTC timezone
            now = datetime.now(timezone.utc)
            
            # Check if the existing token has expired
            if now < user.token_expires_at:
                # Token is still valid - reject login
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Account is already logged in on another device. Please logout first or contact support."
                )
            else:
                # Token expired - clear it and allow new login
                self.user_repo.clear_active_token(user.user_id)
        
        # Create access token with unique JTI
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        access_token, jti = create_access_token(
            data={"user_id": user.user_id, "email": user.email},
            expires_delta=access_token_expires
        )
        
        # Calculate expiration time with UTC timezone
        expires_at = datetime.now(timezone.utc) + access_token_expires
        
        # Store the active token with expiration
        self.user_repo.update_active_token(user.user_id, jti, expires_at)
        
        return Token(access_token=access_token, token_type="bearer")