"""
Leave Balance database model
"""
from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.session import Base


class LeaveBalance(Base):
    """Leave Balance model for tracking employee leave credits"""
    
    __tablename__ = "leave_balances"
    
    leave_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False, unique=True)
    total_leaves = Column(Integer, nullable=False, default=15)
    used_leaves = Column(Integer, nullable=False, default=0)
    last_updated = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationship with user
    user = relationship("User", back_populates="leave_balance")
    
    @property
    def remaining_leaves(self):
        """Calculate remaining leave balance"""
        return self.total_leaves - self.used_leaves
    
    def __repr__(self):
        return f"<LeaveBalance(user_id={self.user_id}, remaining={self.remaining_leaves})>"
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "leave_id": self.leave_id,
            "user_id": self.user_id,
            "total_leaves": self.total_leaves,
            "used_leaves": self.used_leaves,
            "remaining_leaves": self.remaining_leaves,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None
        }
