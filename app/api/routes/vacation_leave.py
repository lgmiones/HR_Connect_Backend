"""
Vacation Leave Routes
Handles vacation leave balance operations
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models.user import User
from app.services.generic_post import post_leave
from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.services.leave_service import LeaveService
from app.schemas.leave_schemas import VacationLeaveResponse, UpdateLeaveRequest, VacationLeaveHistoryResponse
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/vacation-leave", tags=["Vacation Leave"])

@router.post("", response_model=VacationLeaveResponse, status_code=201)
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
        leave = LeaveService.post_vacation_leave(
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

@router.get("/balance", response_model=VacationLeaveResponse)
def get_vacation_balance(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return LeaveService.get_or_create_vacation_leave(db, current_user.user_id)

@router.get("/history", response_model=VacationLeaveHistoryResponse)
def get_vacation_history(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    history = LeaveService.get_vacation_leave_history(db, current_user.user_id)
    return {"history": history}


@router.put("", response_model=VacationLeaveResponse)
async def update_vacation_leave(
    request: UpdateLeaveRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    **PUT** - Update vacation leave used days
    
    **Requires**: Valid JWT token in Authorization header
    
    **Parameters**:
    - **used_days**: Number of vacation days used
    
    **Example Request**:
    ```json
    {
        "used_days": 6
    }
    ```
    
    **Returns**: Updated vacation leave record
    """
    try:
        logger.info(f"Updating vacation leave for user {current_user.user_id}")
        leave = LeaveService.update_vacation_leave(db, current_user.user_id, request.used_days)
        return leave
    except Exception as e:
        logger.error(f"Error updating vacation leave: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update vacation leave")