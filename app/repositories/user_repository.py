"""
User Repository
Handles all database operations related to User model
"""

from typing import Optional
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
    
    def email_exists(self, email: str) -> bool:
        """Check if email already exists in database"""
        return self.db.query(User).filter(User.email == email).first() is not None
    
    def create_user(self, email: str, hashed_password: str) -> User:
        """Create a new user"""
        return self.create({
            "email": email,
            "hashed_password": hashed_password
        })