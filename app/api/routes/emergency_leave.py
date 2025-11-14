"""
Emergency Leave Routes
Handles emergency leave balance operations
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models.user import User
from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.services.leave_service import LeaveService
from app.schemas.leave_schemas import EmergencyLeaveResponse, UpdateLeaveRequest
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/emergency-leave", tags=["Emergency Leave"])


@router.get("", response_model=EmergencyLeaveResponse)
async def get_emergency_leave(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    **GET** - Retrieve emergency leave balance
    
    **Requires**: Valid JWT token in Authorization header
    
    **Returns**:
    - emergency_id: Unique identifier
    - user_id: User ID
    - total_days: Total emergency days allowed (8)
    - used_days: Days already used
    - last_updated: Last update date
    
    **Example Response**:
    ```json
    {
        "emergency_id": 1,
        "user_id": 1,
        "total_days": 8,
        "used_days": 1,
        "last_updated": "2025-11-13"
    }
    ```
    """
    try:
        leave = LeaveService.get_or_create_emergency_leave(db, current_user.user_id)
        logger.info(f"Retrieved emergency leave for user {current_user.user_id}")
        return leave
    except Exception as e:
        logger.error(f"Error fetching emergency leave: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve emergency leave")


@router.post("", response_model=EmergencyLeaveResponse, status_code=status.HTTP_201_CREATED)
async def create_emergency_leave(
    request: UpdateLeaveRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    **POST** - Create/Initialize emergency leave for user
    
    **Requires**: Valid JWT token in Authorization header
    
    **Parameters**:
    - **used_days**: Initial used days (default: 0)
    
    **Example Request**:
    ```json
    {
        "used_days": 0
    }
    ```
    
    **Returns**: Emergency leave record
    """
    try:
        leave = LeaveService.get_or_create_emergency_leave(db, current_user.user_id)
        leave.used_days = request.used_days
        db.commit()
        db.refresh(leave)
        logger.info(f"Created/Updated emergency leave for user {current_user.user_id}")
        return leave
    except Exception as e:
        logger.error(f"Error creating emergency leave: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create emergency leave")


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