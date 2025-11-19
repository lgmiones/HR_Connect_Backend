"""
Leave history service
Handles leave history/request queries
"""

import logging
from sqlalchemy import text
from app.db.session import get_db

logger = logging.getLogger(__name__)


def get_leave_history(question: str, user_id: int, leave_types: dict) -> list[dict]:
    """
    Query database for leave history
    
    Args:
        question: User's question
        user_id: User ID for database query
        leave_types: Dict specifying which types to query
        
    Returns:
        List of leave history records
    """
    db = next(get_db())
    history_data = []

    try:
        logger.info(f"Querying leave history for user {user_id}")
        
        # Query vacation leave history
        if leave_types['vacation']:
            vacation_records = _get_vacation_history(db, user_id)
            history_data.extend(vacation_records)
        
        # Query sick leave history
        if leave_types['sick']:
            sick_records = _get_sick_history(db, user_id)
            history_data.extend(sick_records)
        
        # Query emergency leave history
        if leave_types['emergency']:
            emergency_records = _get_emergency_history(db, user_id)
            history_data.extend(emergency_records)
        
        # Sort by date (most recent first)
        history_data.sort(key=lambda x: x['raw_date'], reverse=True)
        
        logger.info(f"Found {len(history_data)} total leave records")
        return history_data
        
    except Exception as e:
        logger.error(f"Database error fetching leave history: {e}", exc_info=True)
        raise
    finally:
        db.close()


def _get_vacation_history(db, user_id: int) -> list[dict]:
    """Fetch vacation leave history"""
    try:
        results = db.execute(
            text("""
                SELECT TOP 10 used_days, reason, created_at 
                FROM dbo.vacation_leave_requests
                WHERE user_id = :user_id 
                ORDER BY created_at DESC
            """),
            {"user_id": user_id}
        ).fetchall()
        
        logger.info(f"Found {len(results)} vacation leave records")
        
        return [
            {
                "type": "Vacation",
                "days": record[0],
                "reason": record[1],
                "date": record[2].strftime("%B %d, %Y") if record[2] else "Unknown",
                "raw_date": record[2]
            }
            for record in results
        ]
    except Exception as e:
        logger.error(f"Error querying vacation leave: {e}")
        return []


def _get_sick_history(db, user_id: int) -> list[dict]:
    """Fetch sick leave history"""
    try:
        results = db.execute(
            text("""
                SELECT TOP 10 used_days, reason, created_at 
                FROM dbo.sick_leave_requests
                WHERE user_id = :user_id 
                ORDER BY created_at DESC
            """),
            {"user_id": user_id}
        ).fetchall()
        
        logger.info(f"Found {len(results)} sick leave records")
        
        return [
            {
                "type": "Sick",
                "days": record[0],
                "reason": record[1],
                "date": record[2].strftime("%B %d, %Y") if record[2] else "Unknown",
                "raw_date": record[2]
            }
            for record in results
        ]
    except Exception as e:
        logger.error(f"Error querying sick leave: {e}")
        return []


def _get_emergency_history(db, user_id: int) -> list[dict]:
    """Fetch emergency leave history"""
    try:
        results = db.execute(
            text("""
                SELECT TOP 10 used_days, reason, created_at 
                FROM dbo.emergency_leave_requests
                WHERE user_id = :user_id 
                ORDER BY created_at DESC
            """),
            {"user_id": user_id}
        ).fetchall()
        
        logger.info(f"Found {len(results)} emergency leave records")
        
        return [
            {
                "type": "Emergency",
                "days": record[0],
                "reason": record[1],
                "date": record[2].strftime("%B %d, %Y") if record[2] else "Unknown",
                "raw_date": record[2]
            }
            for record in results
        ]
    except Exception as e:
        logger.error(f"Error querying emergency leave: {e}")
        return []