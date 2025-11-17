"""
Emergency Leave Routes
Handles emergency leave balance operations
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.emergency_leave import EmergencyLeave
from app.services.generic_post import post_leave
from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.services.leave_service import LeaveService
from app.schemas.leave_schemas import EmergencyLeaveResponse, UpdateLeaveRequest, EmergencyLeaveHistoryResponse
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/emergency-leave", tags=["Emergency Leave"])


@router.post("", response_model=EmergencyLeaveResponse, status_code=201)
async def create_emergency_leave(
    request: UpdateLeaveRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new emergency leave request"""
    leave = LeaveService.post_emergency_leave(
        db=db,
        user_id=current_user.user_id,
        used_days=request.used_days,
        reason=request.reason
    )
    return leave

@router.get("/balance", response_model=EmergencyLeaveResponse)
def get_vacation_balance(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return LeaveService.get_or_create_emergency_leave(db, current_user.user_id)

@router.get("/history", response_model=EmergencyLeaveHistoryResponse)
def get_vacation_history(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    history = LeaveService.get_emergency_leave_history(db, current_user.user_id)
    return {"history": history}

@router.put("", response_model=EmergencyLeaveResponse)
async def update_emergency_leave(
    request: UpdateLeaveRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    **PUT** - Update emergency leave used days
    
    **Requires**: Valid JWT token in Authorization header
    
    **Parameters**:
    - **used_days**: Number of emergency days used
    
    **Example Request**:
    ```json
    {
        "used_days": 1
    }
    ```
    
    **Returns**: Updated emergency leave record
    """
    try:
        logger.info(f"Updating emergency leave for user {current_user.user_id}")
        leave = LeaveService.update_emergency_leave(db, current_user.user_id, request.used_days)
        return leave
    except Exception as e:
        logger.error(f"Error updating emergency leave: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update emergency leave")