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
from app.schemas.leave_schemas import SickLeaveResponse, UpdateLeaveRequest
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/sick-leave", tags=["Sick Leave"])


@router.post("", response_model=SickLeaveResponse, status_code=201)
async def create_sick_leave(
    request: UpdateLeaveRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return post_leave(db, current_user.user_id, request.used_days, "sick")


@router.get("", response_model=SickLeaveResponse)
async def get_sick_leave(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    **GET** - Retrieve sick leave balance
    
    **Requires**: Valid JWT token in Authorization header
    
    **Returns**:
    - sick_id: Unique identifier
    - user_id: User ID
    - total_days: Total sick days allowed (10)
    - used_days: Days already used
    - last_updated: Last update date
    
    **Example Response**:
    ```json
    {
        "sick_id": 1,
        "user_id": 1,
        "total_days": 10,
        "used_days": 2,
        "last_updated": "2025-11-13"
    }
    ```
    """
    try:
        leave = LeaveService.get_or_create_sick_leave(db, current_user.user_id)
        logger.info(f"Retrieved sick leave for user {current_user.user_id}")
        return leave
    except Exception as e:
        logger.error(f"Error fetching sick leave: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve sick leave")


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