"""
Query pattern detection - Single Responsibility
Detects simple queries, compound queries, and various patterns
"""

import logging
import re

logger = logging.getLogger(__name__)


def is_simple_query(question: str) -> bool:
    """
    Fast heuristic to detect simple single questions (no LLM needed)
    
    Returns True if it's clearly a straightforward single question
    Returns False for compound queries or complex questions
    
    Args:
        question: User's question string
        
    Returns:
        bool: True if simple single query, False otherwise
    """
    question_lower = question.lower().strip()
    
    # Simple question starters
    simple_starters = [
        "what is", "what's", "how do i", "how can i", "how to",
        "where is", "when is", "who is", "show me", "tell me", 
        "explain", "describe", "can you", "can i", "do i"
    ]
    
    # Compound indicators
    compound_indicators = [
        " and ", " also ", " plus ", " as well as",
        "first", "second", "third", "multiple", "several"
    ]
    
    # Check if starts simple
    starts_simple = any(question_lower.startswith(s) for s in simple_starters)
    
    # Check for multiple questions
    question_marks = question.count("?")
    
    # Check if "and" connects two questions
    if " and " in question_lower:
        parts = question_lower.split(" and ")
        if len(parts) >= 2:
            # Check if second part has question words
            second_part = parts[1]
            question_words = ["how", "what", "when", "where", "who", "why", "do i", "can i", "is", "are", "does"]
            if any(qw in second_part for qw in question_words):
                # This is a compound query like "What is X and how do I Y?"
                return False
    
    has_compound = any(ind in question_lower for ind in compound_indicators)
    
    # Multiple question marks = compound
    if question_marks > 1:
        return False
    
    # Simple if: starts simply AND only one question mark AND no compound indicators
    is_simple = (
        (starts_simple and question_marks == 1 and not has_compound) or
        (question_marks == 1 and len(question.split()) < 15 and not has_compound)
    )
    
    return is_simple


def detect_multiple_question_marks(question: str) -> tuple[bool, list[str]]:
    """
    PATTERN 1: Detect multiple question marks
    Example: "What is X? How do I Y?"
    
    Returns:
        (is_compound, list_of_questions)
    """
    if question.count("?") > 1:
        logger.info("   Pattern: Multiple question marks detected")
        
        # Split on question marks and clean up
        questions = []
        for q in question.split("?"):
            q = q.strip()
            if q:
                questions.append(q + "?")
        
        if len(questions) > 1:
            return True, questions
    
    return False, []


def detect_numbered_list(question: str) -> tuple[bool, list[str]]:
    """
    PATTERN 2: Detect numbered lists
    Examples: "1. X 2. Y" or "1) X 2) Y"
    
    Returns:
        (is_compound, list_of_questions)
    """
    # Match patterns like "1. X 2. Y" or "1) X 2) Y"
    numbered_pattern = r'\d+[\.)]\s*([^\d]+?)(?=\d+[\.)]|\Z)'
    matches = re.findall(numbered_pattern, question, re.DOTALL)
    
    if len(matches) >= 2:
        logger.info("   Pattern: Numbered list detected")
        questions = [
            q.strip() + ("?" if not q.strip().endswith("?") else "") 
            for q in matches
        ]
        return True, questions
    
    return False, []


def detect_and_pattern(question: str) -> tuple[bool, list[str]]:
    """
    PATTERN 3: Detect "X and Y?" format
    Example: "What is the leave policy and how to apply?"
    
    Returns:
        (is_compound, list_of_questions)
    """
    question_lower = question.lower().strip()
    
    if " and " not in question_lower:
        return False, []
    
    parts = question.split(" and ", 1)
    
    if len(parts) != 2:
        return False, []
    
    second_part = parts[1].lower().strip()
    
    # Question patterns to detect
    question_patterns = [
        # Action questions (most common)
        "how to", "how do i", "how can i", "how should i",
        
        # Definition questions  
        "what is", "what are", "what's", "what does",
        
        # Other W questions
        "when", "where", "who", "why", "which",
        
        # Permission/ability questions
        "can i", "could i", "do i", "should i", "may i",
        
        # State questions
        "is there", "are there", "does"
    ]
    
    # Check if second part starts with any question pattern
    if any(second_part.startswith(pattern) for pattern in question_patterns):
        logger.info("   Pattern: 'X and Y' compound detected")
        
        q1 = parts[0].strip()
        q2 = parts[1].strip()
        
        # Ensure both questions end with "?"
        if not q1.endswith("?"):
            q1 += "?"
        if not q2.endswith("?"):
            q2 += "?"
        
        logger.info(f"   Split into: '{q1}' | '{q2}'")
        return True, [q1, q2]
    
    return False, []


def detect_explicit_multiple(question: str) -> bool:
    """
    PATTERN 4: Detect explicit multiple question indicators
    Example: "I have two questions..."
    
    Returns:
        bool: True if explicit indicators found (needs LLM decomposition)
    """
    question_lower = question.lower()
    
    multiple_indicators = [
        "two questions", "three questions", "multiple questions",
        "first question", "second question", "also", "additionally"
    ]
    
    if any(indicator in question_lower for indicator in multiple_indicators):
        logger.info("   Pattern: Explicit multiple indicators (needs LLM)")
        return True
    
    return False


def quick_decompose(question: str) -> tuple[bool, list[str]]:
    """
    Fast rule-based decomposition for obvious compound queries (no LLM needed)
    
    Tries multiple pattern detection strategies in order
    
    Args:
        question: User's question string
        
    Returns:
        (is_compound, list_of_questions)
    """
    
    # Pattern 1: Multiple question marks
    is_compound, questions = detect_multiple_question_marks(question)
    if is_compound:
        return True, questions
    
    # Pattern 2: Numbered lists
    is_compound, questions = detect_numbered_list(question)
    if is_compound:
        return True, questions
    
    # Pattern 3: "and" connector
    is_compound, questions = detect_and_pattern(question)
    if is_compound:
        return True, questions
    
    # Pattern 4: Explicit indicators (needs LLM)
    if detect_explicit_multiple(question):
        return False, [question]  # Signal to use LLM
    
    # Not a compound query or too complex for rule-based
    return False, [question]