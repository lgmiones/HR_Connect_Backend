from sqlalchemy.orm import Session
from app.models.vacation_leave import VacationLeave
from app.models.sick_leave import SickLeave
from app.models.emergency_leave import EmergencyLeave


class LeaveService:
    """Service for managing leave balances"""

    @staticmethod
    def get_or_create_vacation_leave(db: Session, user_id: int) -> VacationLeave:
        """Get or create vacation leave record for user"""
        leave = db.query(VacationLeave).filter(
            VacationLeave.user_id == user_id
        ).first()
        
        if not leave:
            leave = VacationLeave(user_id=user_id)
            db.add(leave)
            db.commit()
            db.refresh(leave)
        
        return leave

    @staticmethod
    def get_or_create_sick_leave(db: Session, user_id: int) -> SickLeave:
        """Get or create sick leave record for user"""
        leave = db.query(SickLeave).filter(
            SickLeave.user_id == user_id
        ).first()
        
        if not leave:
            leave = SickLeave(user_id=user_id)
            db.add(leave)
            db.commit()
            db.refresh(leave)
        
        return leave

    @staticmethod
    def get_or_create_emergency_leave(db: Session, user_id: int) -> EmergencyLeave:
        """Get or create emergency leave record for user"""
        leave = db.query(EmergencyLeave).filter(
            EmergencyLeave.user_id == user_id
        ).first()
        
        if not leave:
            leave = EmergencyLeave(user_id=user_id)
            db.add(leave)
            db.commit()
            db.refresh(leave)
        
        return leave

    @staticmethod
    def get_all_leave_balances(db: Session, user_id: int) -> dict:
        """Get all leave balances for user"""
        vacation = LeaveService.get_or_create_vacation_leave(db, user_id)
        sick = LeaveService.get_or_create_sick_leave(db, user_id)
        emergency = LeaveService.get_or_create_emergency_leave(db, user_id)
        
        return {
            "vacation_leave": vacation,
            "sick_leave": sick,
            "emergency_leave": emergency
        }

    @staticmethod
    def update_vacation_leave(db: Session, user_id: int, used_days: int) -> VacationLeave:
        """Update vacation leave used days"""
        leave = LeaveService.get_or_create_vacation_leave(db, user_id)
        leave.used_days = used_days
        db.commit()
        db.refresh(leave)
        return leave

    @staticmethod
    def update_sick_leave(db: Session, user_id: int, used_days: int) -> SickLeave:
        """Update sick leave used days"""
        leave = LeaveService.get_or_create_sick_leave(db, user_id)
        leave.used_days = used_days
        db.commit()
        db.refresh(leave)
        return leave

    @staticmethod
    def update_emergency_leave(db: Session, user_id: int, used_days: int) -> EmergencyLeave:
        """Update emergency leave used days"""
        leave = LeaveService.get_or_create_emergency_leave(db, user_id)
        leave.used_days = used_days
        db.commit()
        db.refresh(leave)
        return leave

    @staticmethod
    def get_remaining_days(total_days: int, used_days: int) -> int:
        """Calculate remaining days"""
        return total_days - used_days