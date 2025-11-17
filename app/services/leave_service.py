from sqlalchemy.orm import Session
from app.models.vacation_leave import VacationLeave
from app.models.sick_leave import SickLeave
from app.models.emergency_leave import EmergencyLeave
from datetime import date

class LeaveService:
    """Service for managing leave balances"""

    @staticmethod
    def get_or_create_vacation_leave(db: Session, user_id: int, reason: str = "Vacation") -> VacationLeave:
        """Get or create vacation leave record for user"""
        leave = db.query(VacationLeave).filter(
            VacationLeave.user_id == user_id
        ).first()
        
        if not leave:
            leave = VacationLeave(
                user_id=user_id,
                reason=reason
                )
            db.add(leave)
            db.commit()
            db.refresh(leave)
        
        return leave

    @staticmethod
    def get_or_create_sick_leave(db: Session, user_id: int, reason: str = "Sick Leave") -> SickLeave:
        """Get or create sick leave record for user"""
        leave = db.query(SickLeave).filter(
            SickLeave.user_id == user_id
        ).first()
        
        if not leave:
            leave = SickLeave(
                user_id=user_id,
                reason=reason
                )
            db.add(leave)
            db.commit()
            db.refresh(leave)
        
        return leave

    @staticmethod
    def get_or_create_emergency_leave(db: Session, user_id: int, reason: str = "Emergency") -> EmergencyLeave:
        """Get or create emergency leave record for user"""
        leave = db.query(EmergencyLeave).filter(
            EmergencyLeave.user_id == user_id
        ).first()
        
        if not leave:
            leave = EmergencyLeave(
                user_id=user_id,
                reason=reason
                )
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
    
    @staticmethod
    def get_or_create_leave(db: Session, user_id: int, leave_type: str):
        """
        Generic method to get or create a leave record.
        leave_type: "vacation", "sick", "emergency"
        """
        model_map = {
            "vacation": VacationLeave,
            "sick": SickLeave,
            "emergency": EmergencyLeave
        }

        if leave_type not in model_map:
            raise ValueError("Invalid leave type")

        Model = model_map[leave_type]
        leave = db.query(Model).filter(Model.user_id == user_id).first()

        if not leave:
            leave = Model(user_id=user_id)
            db.add(leave)
            db.commit()
            db.refresh(leave)

        return leave

    @staticmethod
    def deduct_leave_days(leave, used_days: int):
        """
        Deduct used_days from total_days and update the leave record
        """
        if used_days + leave.used_days > leave.total_days:
            raise ValueError("Used days cannot exceed total days")

        leave.used_days += used_days
        leave.last_updated = date.today()
        return leave