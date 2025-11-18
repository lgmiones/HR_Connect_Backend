"""
Query decomposition - breaks compound questions into individual sub-queries
Single Responsibility Principle: Only handles query decomposition
OPTIMIZED: Three-tier approach (simple fast-path, rule-based compound, LLM fallback)
"""

import logging
import re
from app.Agent.models import AgentState, QueryDecomposition, SubQuery
from app.Agent.utils.llm_config import llm

logger = logging.getLogger(__name__)


class QueryDecomposer:
    """Decomposes user queries into individual sub-questions"""
    
    def __init__(self, llm_instance=None):
        self.llm = llm_instance or llm
        self.decomposer_llm = self.llm.with_structured_output(QueryDecomposition)
    
    @staticmethod
    def is_simple_query(question: str) -> bool:
        """
        Fast heuristic to detect simple single questions (no LLM needed)
        
        Returns True if it's clearly a straightforward single question
        Returns False for compound queries or complex questions
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
    
    @staticmethod
    def quick_decompose(question: str) -> tuple[bool, list[str]]:
        """
        Fast rule-based decomposition for obvious compound queries (no LLM needed)
        
        Patterns detected:
        1. "X and Y?" - Two questions connected by "and"
        2. "X? Y?" - Multiple question marks
        3. Numbered lists - "1. X 2. Y"
        
        Returns: (is_compound, list_of_questions)
        """
        question_lower = question.lower().strip()
        
        # ===== PATTERN 1: Multiple question marks =====
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
        
        # ===== PATTERN 2: Numbered lists =====
        # Match patterns like "1. X 2. Y" or "1) X 2) Y"
        numbered_pattern = r'\d+[\.)]\s*([^\d]+?)(?=\d+[\.)]|\Z)'
        matches = re.findall(numbered_pattern, question, re.DOTALL)
        
        if len(matches) >= 2:
            logger.info("   Pattern: Numbered list detected")
            questions = [q.strip() + ("?" if not q.strip().endswith("?") else "") for q in matches]
            return True, questions
        
                # ===== PATTERN 3: "X and Y?" format =====
        if " and " in question_lower:
            parts = question.split(" and ", 1)
            
            if len(parts) == 2:
                second_part = parts[1].lower().strip()
                
                # ✅ IMPROVED: Better question pattern detection
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
                
                # ✅ Check if second part starts with any question pattern
                second_part_starts_with_question = any(
                    second_part.startswith(pattern) 
                    for pattern in question_patterns
                )
                
                if second_part_starts_with_question:
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
        
        # ===== PATTERN 4: Explicit multiple question indicators =====
        multiple_indicators = [
            "i have", "two questions", "three questions", "multiple questions",
            "first question", "second question", "also", "additionally"
        ]
        
        if any(indicator in question_lower for indicator in multiple_indicators):
            # This might be compound, but too complex for rule-based
            # Return False to trigger LLM decomposition
            logger.info("   Pattern: Explicit multiple indicators (needs LLM)")
            return False, [question]
        
        # Not a compound query or too complex for rule-based
        return False, [question]
    
    @staticmethod
    def quick_route(question: str) -> str:
        """
        Fast keyword-based routing (no LLM needed)
        
        Returns: 'policy', 'personal_data', or 'general'
        """
        question_lower = question.lower()
        
        # ===== PERSONAL DATA INDICATORS =====
        personal_keywords = ["my", "me", "i have", "i am", "do i"]
        personal_topics = ["balance", "remaining", "left", "salary", "attendance", "days"]
        
        # Must have both a personal keyword AND a personal topic
        if any(kw in question_lower for kw in personal_keywords) and \
           any(topic in question_lower for topic in personal_topics):
            return "personal_data"
        
        # ===== GENERAL INDICATORS =====
        general_keywords = [
            "hello", "hi ", "hey", "good morning", "good afternoon",
            "thank", "thanks", "help", "what can you do", "who are you"
        ]
        
        if any(keyword in question_lower for keyword in general_keywords):
            return "general"
        
        # ===== POLICY INDICATORS (default) =====
        # Most HR questions are about policies
        policy_keywords = [
            "policy", "policies", "leave", "benefit", "rule", "procedure",
            "guideline", "how to", "what is", "process", "requirement",
            "apply", "request", "approval"
        ]
        
        if any(kw in question_lower for kw in policy_keywords):
            return "policy"
        
        # Default to general for unclear queries
        return "general"
    
    def decompose(self, state: AgentState) -> dict:
        """
        Break down user's message into individual questions
        
        OPTIMIZATION: Three-tier approach for maximum speed
        
        TIER 1 (⚡⚡⚡): Simple single queries
        - Detection: is_simple_query()
        - Processing: quick_route()
        - Time saved: ~2-3 seconds
        - Coverage: ~70% of queries
        
        TIER 2 (⚡⚡): Obvious compound queries
        - Detection: quick_decompose()
        - Processing: Rule-based splitting + quick_route()
        - Time saved: ~2-3 seconds
        - Coverage: ~20% of queries
        
        TIER 3 (🐢): Complex queries
        - Uses LLM for decomposition
        - Time: 2-3 seconds
        - Coverage: ~10% of queries
        
        Args:
            state: Current agent state with user message
            
        Returns:
            Updated state dict with sub_queries
        """
        last_message = state.messages[-1]
        question = last_message.content if hasattr(last_message, 'content') else last_message["content"]
        
        logger.info(f"📥 Decomposing query: {question}")
        
        # ===== TIER 1: Simple single query fast-path =====
        if self.is_simple_query(question):
            logger.info(f"⚡ TIER 1: Simple single query detected (saved ~2-3s)")
            
            query_type = self.quick_route(question)
            logger.info(f"   Route: {query_type}")
            
            return {
                "sub_queries": [SubQuery(question=question, query_type=query_type)],
                "is_multiple": False,
                "query_results": [],
                "current_query_index": 0
            }
        
        # ===== TIER 2: Rule-based compound decomposition =====
        is_compound, questions = self.quick_decompose(question)
        
        if is_compound and len(questions) > 1:
            logger.info(f"⚡ TIER 2: Rule-based decomposition into {len(questions)} questions (saved ~2-3s)")
            
            sub_queries = []
            for i, q in enumerate(questions):
                query_type = self.quick_route(q)
                sub_queries.append(SubQuery(question=q, query_type=query_type))
                logger.info(f"   Q{i+1}: [{query_type}] {q}")
            
            return {
                "sub_queries": sub_queries,
                "is_multiple": True,
                "query_results": [],
                "current_query_index": 0
            }
        
        # ===== TIER 3: Complex query - use LLM =====
        logger.info(f"🔍 TIER 3: Complex query - using LLM decomposition (~2-3s)")
        
        result = self.decomposer_llm.invoke([
            {
                "role": "system",
                "content": self._get_decomposition_prompt()
            },
            {"role": "user", "content": question}
        ])
        
        logger.info(f"   LLM decomposed into {len(result.sub_queries)} sub-queries")
        for i, sq in enumerate(result.sub_queries):
            logger.info(f"   Q{i+1}: [{sq.query_type}] {sq.question}")
        
        return {
            "sub_queries": result.sub_queries,
            "is_multiple": result.is_multiple,
            "query_results": [],
            "current_query_index": 0
        }
    
    @staticmethod
    def _get_decomposition_prompt() -> str:
        """Returns the system prompt for query decomposition"""
        return """You are a query decomposition expert. Break down the user's message into individual, standalone questions.

For each question, classify it as:
- 'policy': Questions about company policies, guidelines, procedures
- 'personal_data': Questions about user's specific data (leave balance, attendance, etc.)
- 'general': General questions about the system or HR

Be concise and extract only the core questions.

Examples:

User: "What is the leave policy?"
Output: 
- Question 1: "What is the leave policy?" (policy)
is_multiple: False

User: "What is the leave policy and how many leaves do I have?"
Output:
- Question 1: "What is the leave policy?" (policy)
- Question 2: "How many leaves do I have?" (personal_data)
is_multiple: True

User: "I have three questions. What is the leave policy? How many leaves do I have left? How do I apply for emergency leave?"
Output:
- Question 1: "What is the leave policy?" (policy)
- Question 2: "How many leaves do I have left?" (personal_data)
- Question 3: "How do I apply for emergency leave?" (policy)
is_multiple: True

Keep each question standalone and complete."""


# Convenience function for use in LangGraph nodes
def decompose_query_node(state: AgentState) -> dict:
    """LangGraph node wrapper for QueryDecomposer"""
    decomposer = QueryDecomposer()
    return decomposer.decompose(state)