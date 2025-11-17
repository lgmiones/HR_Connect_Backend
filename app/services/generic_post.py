from fastapi import HTTPException
from sqlalchemy.orm import Session  # ✅ import Session
from app.services.leave_service import LeaveService  # ✅ import LeaveService


def post_leave(db: Session, user_id: int, used_days: int, leave_type: str):
    try:
        leave = LeaveService.get_or_create_leave(db, user_id, leave_type)
        leave = LeaveService.deduct_leave_days(leave, used_days)
        db.commit()
        db.refresh(leave)
        return leave
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception:
        raise HTTPException(status_code=500, detail=f"Failed to create/update {leave_type} leave")
