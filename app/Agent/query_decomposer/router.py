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
    
    # ===== PERSONAL DATA INDICATORS =====
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


def _is_personal_data_query(question_lower: str) -> bool:
    """
    Check if query is about personal data
    
    Requires both a personal keyword AND a personal topic
    """
    personal_keywords = ["my", "me", "i have", "i am", "do i"]
    personal_topics = ["balance", "remaining", "left", "salary", "attendance", "days"]
    
    has_personal_keyword = any(kw in question_lower for kw in personal_keywords)
    has_personal_topic = any(topic in question_lower for topic in personal_topics)
    
    return has_personal_keyword and has_personal_topic


def _is_general_query(question_lower: str) -> bool:
    """Check if query is a general greeting or system question"""
    general_keywords = [
        "hello", "hi ", "hey", "good morning", "good afternoon",
        "thank", "thanks", "help", "what can you do", "who are you"
    ]
    
    return any(keyword in question_lower for keyword in general_keywords)


def _is_policy_query(question_lower: str) -> bool:
    """Check if query is about HR policies"""
    policy_keywords = [
        # Document types
        "policy", "policies", "rule", "procedure", "guideline", "regulation",
        
        # Leave-related
        "leave", "vacation", "sick", "emergency", "time off", "pto",
        
        # Benefits & compensation
        "benefit", "benefits", "salary", "compensation", "bonus",
        "payout", "payroll", "payment", "pay", "allowance",  # ✅ ADDED
        
        # Processes
        "process", "requirement", "apply", "request", "approval",
        "application", "filing", "submit",
        
        # Questions starters
        "how to", "what is", "when is", "where is",  # ✅ ADDED "when is"
        
        # Schedule-related
        "schedule", "date", "deadline", "timeline", "when",  # ✅ ADDED
        
        # Other HR topics
        "attendance", "performance", "evaluation", "review",
        "onboarding", "orientation", "training", "development"
    ]
    
    return any(kw in question_lower for kw in policy_keywords)