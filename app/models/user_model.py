"""
User database model
"""
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.session import Base


class User(Base):
    """User model representing employees in the system"""
    
    __tablename__ = "users"
    
    user_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    
    # Relationship with leave balances
    leave_balance = relationship(
        "LeaveBalance",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<User(user_id={self.user_id}, email={self.email})>"
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "user_id": self.user_id,
            "email": self.email,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
