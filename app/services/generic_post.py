from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.services.leave_service import LeaveService

def post_leave(db: Session, user_id: int, used_days: int, leave_type: str, reason: str):
    try:
        if leave_type == "emergency":
            leave = LeaveService.post_emergency_leave(db, user_id, used_days, reason)
        elif leave_type == "sick":
            leave = LeaveService.post_sick_leave(db, user_id, used_days, reason)
        elif leave_type == "vacation":
            leave = LeaveService.post_vacation_leave(db, user_id, used_days, reason)
        else:
            raise ValueError(f"Unknown leave type: {leave_type}")

        return leave

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create/update {leave_type} leave: {e}"
        )
