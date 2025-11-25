"""
Intent detection for personal data queries
Enhanced keyword-based detection with comprehensive patterns
"""

import logging
import re

logger = logging.getLogger(__name__)


def detect_intent(question: str) -> str:
    """
    Detect the intent of a personal data query
    
    Args:
        question: User's question
        
    Returns:
        str: 'balance', 'history', or 'unknown'
    """
    question_lower = question.lower().strip()
    
    # Check balance first (more specific patterns)
    if is_leave_balance_query(question_lower):
        logger.info("Intent: balance")
        return 'balance'
    
    # Check history (broader patterns)
    if is_leave_history_query(question_lower):
        logger.info("Intent: history")
        return 'history'
    
    # Unknown
    logger.info("Intent: unknown")
    return 'unknown'


def is_leave_balance_query(question_lower: str) -> bool:
    """
    Check if question is about current leave balance
    
    Keywords: balance, remaining, left, how many, available
    """
    balance_keywords = [
        'balance', 'remaining', 'left', 'how many', 'how much',
        'available', 'do i have', 'days left', 'have left',
        'still have', 'can i use', 'can i take'
    ]
    return any(keyword in question_lower for keyword in balance_keywords)


def is_leave_history_query(question_lower: str) -> bool:
    """
    Check if question is about leave history/requests
    Comprehensive pattern matching for various phrasings
    """
    # Definite history keywords (high confidence)
    definite_keywords = [
        'history', 'past', 'previous', 'took', 'taken', 'used',
        'entries', 'records', 'requests', 'applied', 'requested'
    ]
    
    if any(keyword in question_lower for keyword in definite_keywords):
        return True
    
    # Action verbs indicating retrieval
    action_verbs = ['give', 'show', 'display', 'list', 'get', 'fetch', 
                    'pull', 'see', 'view', 'check', 'find', 'tell']
    
    has_action = any(f"{verb} " in question_lower or f"{verb} me" in question_lower 
                     for verb in action_verbs)
    
    # Leave context
    has_leave_context = any(word in question_lower for word in 
                           ['leave', 'vacation', 'sick', 'emergency', 'vl', 'sl', 'el'])
    
    # Action verb + leave context = history query
    if has_action and has_leave_context:
        return True
    
    # Time references indicate history
    time_refs = ['when', 'last', 'recent', 'this month', 'last month',
                 'this year', 'last year', 'on ', 'in ', 'during']
    
    has_time = any(ref in question_lower for ref in time_refs)
    
    if has_time and has_leave_context:
        return True
    
    # Date patterns (11/17/2025, 2024-11-17, etc.)
    has_date = re.search(r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}', question_lower)
    
    if has_date and has_leave_context:
        return True
    
    return False


def detect_leave_type(question: str) -> dict:
    """
    Detect which leave types the user is asking about
    
    Args:
        question: User's question
        
    Returns:
        dict: {'vacation': bool, 'sick': bool, 'emergency': bool}
    """
    question_lower = question.lower()
    
    # Explicit leave type mentions (including abbreviations)
    vacation = 'vacation' in question_lower or 'vl' in question_lower
    sick = 'sick' in question_lower or 'sl' in question_lower
    emergency = 'emergency' in question_lower or 'el' in question_lower
    
    # If no specific type mentioned, query all types
    if not (vacation or sick or emergency):
        vacation = sick = emergency = True
    
    logger.info(f"Leave types: vacation={vacation}, sick={sick}, emergency={emergency}")
    
    return {
        'vacation': vacation,
        'sick': sick,
        'emergency': emergency
    }
