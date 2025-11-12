"""
Query decomposition - breaks compound questions into individual sub-queries
Single Responsibility Principle: Only handles query decomposition
"""

import logging
from app.Agent.models import AgentState, QueryDecomposition
from app.Agent.utils.llm_config import llm

logger = logging.getLogger(__name__)


class QueryDecomposer:
    """Decomposes user queries into individual sub-questions"""
    
    def __init__(self, llm_instance=None):
        self.llm = llm_instance or llm
        self.decomposer_llm = self.llm.with_structured_output(QueryDecomposition)
    
    def decompose(self, state: AgentState) -> dict:
        """
        Break down user's message into individual questions
        
        Args:
            state: Current agent state with user message
            
        Returns:
            Updated state dict with sub_queries
        """
        last_message = state.messages[-1]
        
        result = self.decomposer_llm.invoke([
            {
                "role": "system",
                "content": self._get_decomposition_prompt()
            },
            {"role": "user", "content": last_message.content}
        ])
        
        logger.info(f"Decomposed into {len(result.sub_queries)} sub-queries")
        for i, sq in enumerate(result.sub_queries):
            logger.info(f"  Sub-query {i+1}: [{sq.query_type}] {sq.question}")
        
        return {
            "sub_queries": result.sub_queries,
            "is_multiple": result.is_multiple,
            "query_results": []
        }
    
    @staticmethod
    def _get_decomposition_prompt() -> str:
        """Returns the system prompt for query decomposition"""
        return """You are a query decomposition expert. Break down the user's message into individual, standalone questions.

For each question, classify it as:
- 'policy': Questions about company policies, guidelines, procedures
- 'personal_data': Questions about user's specific data (leave balance, attendance, etc.)
- 'general': General questions about the system or HR

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