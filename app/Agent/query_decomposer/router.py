"""
Query type routing - Single Responsibility
Routes queries to appropriate handlers (policy, personal_data, general)
"""

import logging

logger = logging.getLogger(__name__)


def quick_route(question: str) -> str:
    """
    Fast keyword-based routing (no LLM needed)
    
    Args:
        question: User's question string
        
    Returns:
        str: 'policy', 'personal_data', or 'general'
    """
    question_lower = question.lower()
    
    # ===== PERSONAL DATA INDICATORS (PRIORITY) =====
    if _is_personal_data_query(question_lower):
        return "personal_data"
    
    # ===== GENERAL INDICATORS =====
    if _is_general_query(question_lower):
        return "general"
    
    # ===== POLICY INDICATORS (default) =====
    if _is_policy_query(question_lower):
        return "policy"
    
    # Default to general for unclear queries
    return "general"


# def _is_personal_data_query(question_lower: str) -> bool:
    """
    Check if query is about personal data
    
    Requires BOTH personal keyword AND personal topic
    Enhanced with past tense verbs and time references
    """
    # Personal indicators (I/my + actions)
    personal_keywords = [
        # Possessives
        "my", "me",
        
        # Present tense
        "i have", "i am", "do i", "can i",
        
        # Past tense
        "i took", "i used", "i applied", "i requested",
        "did i take", "did i use", "did i apply", "did i request",
        "have i taken", "have i used",
        
        # Question starters about self
        "what did i", "when did i", "how many did i",
        "show me my", "tell me my"
    ]
    
    # Personal data topics
    personal_topics = [
        # Balance-related
        "balance", "remaining", "left", "available",
        
        # History-related
        "history", "past", "previous", "recent", "last",
        "took", "used", "taken", "applied", "requested",
        
        # Time-related personal queries
        "last month", "last week", "this year", "recently",
        "this month", "this week",
        
        # Other personal data
        "salary", "attendance", "days", "record", "records"
    ]
    
    has_personal_keyword = any(kw in question_lower for kw in personal_keywords)
    has_personal_topic = any(topic in question_lower for topic in personal_topics)
    
    return has_personal_keyword and has_personal_topic
def _is_personal_data_query(question_lower: str) -> bool:
    """
    Check if query is about personal data
    
    Enhanced to catch implicit personal queries about leave history/records
    """
    
    # Explicit personal keywords
    explicit_personal_keywords = [
        "my", "me",
        "i have", "i am", "do i", "can i",
        "i took", "i used", "i applied", "i requested",
        "did i take", "did i use", "did i apply", "did i request",
        "have i taken", "have i used",
        "what did i", "when did i", "how many did i",
        "show me my", "tell me my"
    ]
    
    # Personal data topics
    personal_topics = [
        "balance", "remaining", "left", "available",
        "history", "past", "previous", "recent", "last",
        "took", "used", "taken", "applied", "requested",
        "last month", "last week", "this year", "recently",
        "this month", "this week",
        "salary", "attendance", "days", "record", "records"
    ]
    
    # ✅ NEW: Implicit personal query patterns
    # Questions about leave events/records without explicit "my"
    implicit_personal_patterns = [
        # Asking about specific dates/periods
        r'what.*leave.*on \d{1,2}[/-]\d{1,2}[/-]\d{2,4}',  # "what leaves on 11/17/2025"
        r'what.*leave.*in (january|february|march|april|may|june|july|august|september|october|november|december)',
        r'what.*leave.*happened',
        r'what kind of.*leave',
        r'which.*leave.*took',
        
        # Questions about leave records
        r'show.*leave.*history',
        r'list.*leave',
        r'display.*leave',
        
        # Questions about specific counts/totals for the user
        r'how many.*leave.*took',
        r'total.*leave.*used',
    ]
    
    # Check explicit personal keywords
    has_explicit_personal = any(kw in question_lower for kw in explicit_personal_keywords)
    
    # Check personal topics
    has_personal_topic = any(topic in question_lower for topic in personal_topics)
    
    # ✅ Check implicit personal patterns
    import re
    has_implicit_personal = any(
        re.search(pattern, question_lower) 
        for pattern in implicit_personal_patterns
    )
    
    # Match if:
    # 1. Has explicit personal keyword AND topic, OR
    # 2. Has implicit personal pattern
    return (has_explicit_personal and has_personal_topic) or has_implicit_personal

def _is_general_query(question_lower: str) -> bool:
    """Check if query is a general greeting or system question"""
    general_keywords = [
        "hello", "hi ", "hey", "good morning", "good afternoon",
        "thank", "thanks", "help", "what can you do", "who are you"
    ]
    
    return any(keyword in question_lower for keyword in general_keywords)


def _is_policy_query(question_lower: str) -> bool:
    """Check if query is about HR policies (fallback)"""
    policy_keywords = [
        # Document types
        "policy", "policies", "rule", "procedure", "guideline", "regulation",
        
        # Leave-related (general)
        "leave", "vacation", "sick", "emergency", "time off", "pto",
        
        # Benefits & compensation
        "benefit", "benefits", "salary", "compensation", "bonus",
        "payout", "payroll", "payment", "pay", "allowance",
        
        # Processes
        "process", "requirement", "apply", "request", "approval",
        "application", "filing", "submit",
        
        # Question starters (general)
        "how to", "what is", "when is", "where is",
        
        # Schedule-related
        "schedule", "date", "deadline", "timeline", "when",
        
        # Other HR topics
        "attendance", "performance", "evaluation", "review",
        "onboarding", "orientation", "training", "development"
    ]
    
    return any(kw in question_lower for kw in policy_keywords)