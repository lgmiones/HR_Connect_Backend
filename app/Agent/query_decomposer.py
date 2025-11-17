"""
Query decomposition - breaks compound questions into individual sub-queries
Single Responsibility Principle: Only handles query decomposition
OPTIMIZED: Fast-path routing for simple queries (skips LLM, saves ~2-3s)
"""

import logging
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
        """
        question_lower = question.lower().strip()
        
        # Simple question starters
        simple_starters = [
            "what is", "what's", "how do i", "how can i", "how to",  # ✅ Added "how to"
            "where is", "when is", "who is", "show me", "tell me", 
            "explain", "describe", "can you", "can i"
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
        has_and = " and " in question_lower and "?" in question_lower
        has_compound = any(ind in question_lower for ind in compound_indicators)
        
        # Simple if: starts simply AND only one question mark AND no compound indicators
        is_simple = (
            (starts_simple and question_marks == 1 and not has_and and not has_compound) or
            (question_marks == 1 and len(question.split()) < 15 and not has_compound)
        )
        
        return is_simple
    
    @staticmethod
    def quick_route(question: str) -> str:
        """
        Fast keyword-based routing (no LLM needed)
        
        Returns: 'policy', 'personal_data', or 'general'
        """
        question_lower = question.lower()
        
        # Personal data indicators
        personal_keywords = ["my", "me", "i have", "i am", "do i"]
        personal_topics = ["balance", "remaining", "left", "salary", "attendance"]
        
        if any(kw in question_lower for kw in personal_keywords) and \
           any(topic in question_lower for topic in personal_topics):
            return "personal_data"
        
        # Policy indicators
        policy_keywords = [
            "policy", "policies", "leave", "benefit", "rule", "procedure",
            "guideline", "how to", "what is", "process", "requirement"
        ]
        
        if any(kw in question_lower for kw in policy_keywords):
            return "policy"
        
        return "general"
    
    def decompose(self, state: AgentState) -> dict:
        """
        Break down user's message into individual questions
        
        OPTIMIZATION: Uses fast-path for simple queries (saves ~2-3 seconds)
        
        Args:
            state: Current agent state with user message
            
        Returns:
            Updated state dict with sub_queries
        """
        last_message = state.messages[-1]
        question = last_message.content if hasattr(last_message, 'content') else last_message["content"]
        
        # ✅ FAST PATH: Skip LLM for simple single questions
        if self.is_simple_query(question):
            logger.info(f"⚡ Simple query detected - using fast-path routing")
            
            query_type = self.quick_route(question)
            logger.info(f"   Routed to: {query_type}")
            
            return {
                "sub_queries": [SubQuery(question=question, query_type=query_type)],
                "is_multiple": False,
                "query_results": [],
                "current_query_index": 0
            }
        
        # ✅ SLOW PATH: Use LLM for complex/compound queries
        logger.info(f"🔍 Complex query detected - using LLM decomposition")
        
        result = self.decomposer_llm.invoke([
            {
                "role": "system",
                "content": self._get_decomposition_prompt()
            },
            {"role": "user", "content": question}
        ])
        
        logger.info(f"Decomposed into {len(result.sub_queries)} sub-queries")
        for i, sq in enumerate(result.sub_queries):
            logger.info(f"  Sub-query {i+1}: [{sq.query_type}] {sq.question}")
        
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