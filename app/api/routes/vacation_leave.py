"""
Vacation Leave Routes
Handles vacation leave balance operations
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models.user import User
from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.services.leave_service import LeaveService
from app.schemas.leave_schemas import VacationLeaveResponse, UpdateLeaveRequest
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/vacation-leave", tags=["Vacation Leave"])


@router.get("", response_model=VacationLeaveResponse)
async def get_vacation_leave(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    **GET** - Retrieve vacation leave balance
    
    **Requires**: Valid JWT token in Authorization header
    
    **Returns**:
    - vacation_id: Unique identifier
    - user_id: User ID
    - total_days: Total vacation days allowed (18)
    - used_days: Days already used
    - last_updated: Last update date
    
    **Example Response**:
    ```json
    {
        "vacation_id": 1,
        "user_id": 1,
        "total_days": 18,
        "used_days": 6,
        "last_updated": "2025-11-13"
    }
    ```
    """
    try:
        leave = LeaveService.get_or_create_vacation_leave(db, current_user.user_id)
        logger.info(f"Retrieved vacation leave for user {current_user.user_id}")
        return leave
    except Exception as e:
        logger.error(f"Error fetching vacation leave: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve vacation leave")


@router.post("", response_model=VacationLeaveResponse, status_code=status.HTTP_201_CREATED)
async def create_vacation_leave(
    request: UpdateLeaveRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    **POST** - Create/Initialize vacation leave for user
    
    **Requires**: Valid JWT token in Authorization header
    
    **Parameters**:
    - **used_days**: Initial used days (default: 0)
    
    **Example Request**:
    ```json
    {
        "used_days": 0
    }
    ```
    
    **Returns**: Vacation leave record
    """
    try:
        leave = LeaveService.get_or_create_vacation_leave(db, current_user.user_id)
        leave.used_days = request.used_days
        db.commit()
        db.refresh(leave)
        logger.info(f"Created/Updated vacation leave for user {current_user.user_id}")
        return leave
    except Exception as e:
        logger.error(f"Error creating vacation leave: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create vacation leave")


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