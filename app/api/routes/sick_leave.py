"""
Sick Leave Routes
Handles sick leave balance operations
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.sick_leave import SickLeave
from app.api.dependencies import get_current_user
from app.services.generic_post import post_leave
from app.db.session import get_db
from app.services.leave_service import LeaveService
from app.schemas.leave_schemas import SickLeaveResponse, UpdateLeaveRequest, SickLeaveHistoryResponse
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/sick-leave", tags=["Sick Leave"])


@router.post("", response_model=SickLeaveResponse, status_code=201)
async def create_emergency_leave(
    request: UpdateLeaveRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new emergency leave request"""
    
    # Validate reason is provided
    if not request.reason or not request.reason.strip():
        raise HTTPException(
            status_code=400,
            detail="Reason is required for emergency leave request"
        )
    
    # Validate used_days is positive
    if request.used_days <= 0:
        raise HTTPException(
            status_code=400,
            detail="Number of days must be greater than zero"
        )
    
    try:
        leave = LeaveService.post_sick_leave(
            db=db,
            user_id=current_user.user_id,
            used_days=request.used_days,
            reason=request.reason
        )
        return leave
    except ValueError as e:
        # Handle insufficient balance errors
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

@router.get("/balance", response_model=SickLeaveResponse)
def get_vacation_balance(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return LeaveService.get_or_create_sick_leave(db, current_user.user_id)

@router.get("/history", response_model=SickLeaveHistoryResponse)
def get_vacation_history(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    history = LeaveService.get_sick_leave_history(db, current_user.user_id)
    return {"history": history}

@router.put("", response_model=SickLeaveResponse)
async def update_sick_leave(
    request: UpdateLeaveRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    **PUT** - Update sick leave used days
    
    **Requires**: Valid JWT token in Authorization header
    
    **Parameters**:
    - **used_days**: Number of sick days used
    
    **Example Request**:
    ```json
    {
        "used_days": 2
    }
    ```
    
    **Returns**: Updated sick leave record
    """
    try:
        logger.info(f"Updating sick leave for user {current_user.user_id}")
        leave = LeaveService.update_sick_leave(db, current_user.user_id, request.used_days)
        return leave
    except Exception as e:
        logger.error(f"Error updating sick leave: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update sick leave")