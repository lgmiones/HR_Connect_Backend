"""
Intent detection for general queries
Categorizes general questions for appropriate handling
"""

import logging

logger = logging.getLogger(__name__)


def detect_general_intent(question: str) -> str:
    """
    Detect the intent of a general query
    
    Args:
        question: User's question
        
    Returns:
        str: 'help', 'about', 'features', 'greeting', or 'other'
    """
    question_lower = question.lower()
    
    if is_help_query(question_lower):
        return 'help'
    elif is_about_query(question_lower):
        return 'about'
    elif is_features_query(question_lower):
        return 'features'
    elif is_greeting(question_lower):
        return 'greeting'
    else:
        return 'other'


def is_help_query(question_lower: str) -> bool:
    """Check if asking for help or capabilities"""
    help_keywords = [
        "what can you do", "help", "how to use", "guide",
        "how can you help", "what do you do", "capabilities"
    ]
    return any(keyword in question_lower for keyword in help_keywords)


def is_about_query(question_lower: str) -> bool:
    """Check if asking about HRConnect system"""
    about_keywords = [
        "hrconnect", "what is this", "about", "system",
        "who are you", "what are you", "your purpose"
    ]
    return any(keyword in question_lower for keyword in about_keywords)


def is_features_query(question_lower: str) -> bool:
    """Check if asking about features"""
    feature_keywords = [
        "feature", "features", "what does", "functionality",
        "functions", "capabilities", "can i do"
    ]
    return any(keyword in question_lower for keyword in feature_keywords)


def is_greeting(question_lower: str) -> bool:
    """Check if it's a simple greeting"""
    greeting_keywords = [
        "hello", "hi ", "hey", "good morning", "good afternoon",
        "good evening", "greetings"
    ]
    return any(question_lower.startswith(keyword) or f" {keyword}" in question_lower 
               for keyword in greeting_keywords)