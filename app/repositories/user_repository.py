"""
User Repository
Handles all database operations related to User model
"""

from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.user import User
from app.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository[User]):
    """User-specific repository"""
    
    def __init__(self, db: Session):
        super().__init__(User, db)
    
    def get_by_email(self, email: str) -> Optional[User]:
        """Find user by email address"""
        return self.db.query(User).filter(User.email == email).first()
    
    def get_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID - ALWAYS fetch fresh from DB"""
        
        # ✅ CRITICAL: Expire all cached objects first
        self.db.expire_all()
        
        # ✅ Query by primary key
        user = self.db.query(User).filter(User.user_id == user_id).first()
        
        if user:
            # ✅ Refresh from database to ensure fresh data
            self.db.refresh(user)
            
            # ✅ Log to verify correct user
            print(f"📧 get_by_id query result: user_id={user.user_id}, email={user.email}")
        
        return user
    
    def email_exists(self, email: str) -> bool:
        """Check if email already exists in database"""
        return self.db.query(User).filter(User.email == email).first() is not None
    
    def create_user(self, email: str, hashed_password: str) -> User:
        """Create a new user"""
        return self.create({
            "email": email,
            "hashed_password": hashed_password
        })
    
    def update_active_token(self, user_id: int, jti: str, expires_at: datetime) -> None:
        """
        Update user's current active token JTI with expiration
        This invalidates any previous session tokens
        """
        user = self.get_by_id(user_id)
        if user:
            user.current_token_jti = jti
            user.token_expires_at = expires_at
            self.db.commit()
    
    def clear_active_token(self, user_id: int) -> None:
        """
        Clear user's active token on logout
        """
        user = self.get_by_id(user_id)
        if user:
            user.current_token_jti = None
            user.token_expires_at = None
            self.db.commit()