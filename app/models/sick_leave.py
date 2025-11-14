from sqlalchemy import Column, Integer, ForeignKey, Date, UniqueConstraint
from sqlalchemy.sql import func
from app.db.session import Base


class SickLeave(Base):
    """Sick leave balance model"""
    __tablename__ = "sick_leave"

    sick_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), index=True, nullable=False, unique=True)
    total_days = Column(Integer, default=15)
    used_days = Column(Integer, default=0)
    last_updated = Column(Date, server_default=func.current_date(), onupdate=func.current_date())

    __table_args__ = (UniqueConstraint('user_id', name='uq_sick_user_id'),)
