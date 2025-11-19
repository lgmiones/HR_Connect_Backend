"""
Intent detection for personal data queries
Determines if user wants balance, history, or other info
"""

import logging

logger = logging.getLogger(__name__)


def detect_intent(question: str) -> str:
    """
    Detect the intent of a personal data query
    
    Args:
        question: User's question
        
    Returns:
        str: 'balance', 'history', or 'unknown'
    """
    question_lower = question.lower()
    
    if is_leave_balance_query(question_lower):
        return 'balance'
    elif is_leave_history_query(question_lower):
        return 'history'
    else:
        return 'unknown'


def is_leave_balance_query(question_lower: str) -> bool:
    """
    Check if question is about current leave balance
    
    Keywords: balance, remaining, left, how many, available
    """
    balance_keywords = [
        'balance', 'remaining', 'left', 'how many', 'how much',
        'available', 'do i have', 'days left', 'have left'
    ]
    return any(keyword in question_lower for keyword in balance_keywords)


def is_leave_history_query(question_lower: str) -> bool:
    """
    Check if question is about leave history/requests
    
    Keywords: history, past, took, used, applied
    """
    history_keywords = [
        'history', 'past', 'previous', 'last', 'recent',
        'took', 'taken', 'used', 'applied', 'requested',
        'when did i', 'what leaves', 'my requests', 'did i take'
    ]
    return any(keyword in question_lower for keyword in history_keywords)


def detect_leave_type(question: str) -> dict:
    """
    Detect which leave types the user is asking about
    
    Args:
        question: User's question
        
    Returns:
        dict: {'vacation': bool, 'sick': bool, 'emergency': bool}
    """
    question_lower = question.lower()
    
    vacation = "vacation" in question_lower
    sick = "sick" in question_lower
    emergency = "emergency" in question_lower
    
    # If no specific type mentioned, query all
    if not (vacation or sick or emergency):
        vacation = sick = emergency = True
    
    return {
        'vacation': vacation,
        'sick': sick,
        'emergency': emergency
    }