from fastapi import HTTPException
from sqlalchemy.orm import Session  
from app.services.leave_service import LeaveService  


def post_leave(db: Session, user_id: int, used_days: int, leave_type: str, reason: str):
    try:
        # Use leave-type-specific get_or_create method
        if leave_type == "emergency":
            leave = LeaveService.get_or_create_emergency_leave(db, user_id, reason)
        elif leave_type == "sick":
            leave = LeaveService.get_or_create_sick_leave(db, user_id, reason)
        elif leave_type == "vacation":
            leave = LeaveService.get_or_create_vacation_leave(db, user_id, reason)
        else:
            raise ValueError(f"Unknown leave type: {leave_type}")

        # Deduct used days
        leave = LeaveService.deduct_leave_days(leave, used_days)

        # Update reason in case user provided a new one
        leave.reason = reason

        db.commit()
        db.refresh(leave)
        return leave
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create/update {leave_type} leave: {e}")



