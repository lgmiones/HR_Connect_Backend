from sqlalchemy import Column, Integer, ForeignKey, Date, UniqueConstraint
from sqlalchemy.sql import func
from app.db.session import Base


class VacationLeave(Base):
    """Vacation leave balance model - One-to-One with User"""
    __tablename__ = "vacation_leave"

    vacation_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), index=True, nullable=False, unique=True)
    total_days = Column(Integer, nullable=False, default=20)
    used_days = Column(Integer, nullable=False, default=0)
    last_updated = Column(Date, server_default=func.current_date(), onupdate=func.current_date())
    
    __table_args__ = (UniqueConstraint('user_id', name='uq_vacation_user_id'),)