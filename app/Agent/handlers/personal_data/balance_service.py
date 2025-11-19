"""
Leave balance service
Handles current leave balance queries
"""

import logging
from sqlalchemy import text
from app.db.session import get_db

logger = logging.getLogger(__name__)


def get_leave_balance(question: str, user_id: int) -> str:
    """
    Query database for current leave balances
    
    Args:
        question: User's question
        user_id: User ID for database query
        
    Returns:
        Formatted balance information
    """
    db = next(get_db())
    question_lower = question.lower()
    lines = []

    try:
        # Fetch all leave types
        vacation_result = _get_vacation_balance(db, user_id)
        sick_result = _get_sick_balance(db, user_id)
        emergency_result = _get_emergency_balance(db, user_id)

        # Filter based on question
        if "vacation" in question_lower and vacation_result:
            lines.append(_format_balance_line("Vacation", "🏖️", vacation_result))

        elif "sick" in question_lower and sick_result:
            lines.append(_format_balance_line("Sick", "🏥", sick_result))

        elif "emergency" in question_lower and emergency_result:
            lines.append(_format_balance_line("Emergency", "🚨", emergency_result))
        
        else:
            # Show all leave types for general queries
            if vacation_result:
                lines.append(_format_balance_line("Vacation", "🏖️", vacation_result))
            if sick_result:
                lines.append(_format_balance_line("Sick", "🏥", sick_result))
            if emergency_result:
                lines.append(_format_balance_line("Emergency", "🚨", emergency_result))
        
        if not lines:
            return f"**{question}**\n\nNo leave records found for your account."
        
        return "**Your Leave Balance:**\n" + "\n".join(lines)

    except Exception as e:
        logger.error(f"Database error fetching leave balance: {e}", exc_info=True)
        return f"**{question}**\n\nSorry, I couldn't retrieve your leave balance. Please try again later."
    finally:
        db.close()


def _get_vacation_balance(db, user_id: int):
    """Fetch vacation leave balance"""
    return db.execute(
        text("SELECT total_days, used_days FROM dbo.vacation_leave WHERE user_id = :user_id"),
        {"user_id": user_id}
    ).fetchone()


def _get_sick_balance(db, user_id: int):
    """Fetch sick leave balance"""
    return db.execute(
        text("SELECT total_days, used_days FROM dbo.sick_leave WHERE user_id = :user_id"),
        {"user_id": user_id}
    ).fetchone()


def _get_emergency_balance(db, user_id: int):
    """Fetch emergency leave balance"""
    return db.execute(
        text("SELECT total_days, used_days FROM dbo.emergency_leave WHERE user_id = :user_id"),
        {"user_id": user_id}
    ).fetchone()


def _format_balance_line(leave_type: str, emoji: str, result: tuple) -> str:
    """
    Format a single balance line
    
    Args:
        leave_type: Name of leave type
        emoji: Emoji icon
        result: (total_days, used_days) tuple
        
    Returns:
        Formatted string like "🏖️ Vacation: 16/20 days"
    """
    total_days, used_days = result
    remaining = total_days - (used_days or 0)
    return f"{emoji} {leave_type}: {remaining}/{total_days} days"