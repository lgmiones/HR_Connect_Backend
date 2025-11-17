from sqlalchemy.orm import Session
from app.models.vacation_leave import VacationLeave
from app.models.sick_leave import SickLeave
from app.models.emergency_leave import EmergencyLeave
from app.models.emergency_leave_request import EmergencyLeaveRequest
from app.models.vacation_leave_request import VacationLeaveRequest
from app.models.sick_leave_request import SickLeaveRequest
from datetime import date

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
    
      # --- Post leave (updates balance + history) ---
    @staticmethod
    def post_vacation_leave(db: Session, user_id: int, used_days: int, reason: str) -> VacationLeave:
        
        leave = LeaveService.get_or_create_vacation_leave(db, user_id)
        leave.used_days += used_days
        db.commit()
        db.refresh(leave)

        leave_request = VacationLeaveRequest(
            user_id=user_id,
            used_days=used_days,
            reason=reason
        )
        db.add(leave_request)
        db.commit()
        db.refresh(leave_request)

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
    
         # --- Post leave (updates balance + history) ---
    @staticmethod
    def post_sick_leave(db: Session, user_id: int, used_days: int, reason: str) -> SickLeave:
        
        leave = LeaveService.get_or_create_sick_leave(db, user_id)
        leave.used_days += used_days
        db.commit()
        db.refresh(leave)

        leave_request = SickLeaveRequest(
            user_id=user_id,
            used_days=used_days,
            reason=reason
        )
        db.add(leave_request)
        db.commit()
        db.refresh(leave_request)

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
    
    # --- Post leave (updates balance + history) ---
    @staticmethod
    def post_emergency_leave(db: Session, user_id: int, used_days: int, reason: str) -> EmergencyLeave:
        
        leave = LeaveService.get_or_create_emergency_leave(db, user_id)
        leave.used_days += used_days
        db.commit()
        db.refresh(leave)

        leave_request = EmergencyLeaveRequest(
            user_id=user_id,
            used_days=used_days,
            reason=reason
        )
        db.add(leave_request)
        db.commit()
        db.refresh(leave_request)

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
    
    @staticmethod
    def get_vacation_leave_history(db: Session, user_id: int):
        return db.query(VacationLeaveRequest).filter(
            VacationLeaveRequest.user_id == user_id
        ).order_by(VacationLeaveRequest.created_at.desc()).all()

    @staticmethod
    def get_sick_leave_history(db: Session, user_id: int):
        return db.query(SickLeaveRequest).filter(
            SickLeaveRequest.user_id == user_id
        ).order_by(SickLeaveRequest.created_at.desc()).all()

    @staticmethod
    def get_emergency_leave_history(db: Session, user_id: int):
        return db.query(EmergencyLeaveRequest).filter(
            EmergencyLeaveRequest.user_id == user_id
        ).order_by(EmergencyLeaveRequest.created_at.desc()).all()