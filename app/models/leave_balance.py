from sqlalchemy import Column, Integer, String, ForeignKey, Date
from sqlalchemy.sql import func
from app.db.session import Base

class LeaveBalance(Base):
    __tablename__ = "leave_balance"

    leave_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), index=True)
    total_leaves = Column(String(100))
    used_leaves = Column(String(255))
    last_updated = Column(Date, default=func.current_date(), onupdate=func.current_date())