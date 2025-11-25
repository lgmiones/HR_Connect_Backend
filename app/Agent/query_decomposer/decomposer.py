# """
# Main query decomposer - Orchestrates the decomposition process
# Single Responsibility: Coordinates decomposition flow
# Optimized: Azure LLM handles all queries with caching for performance
# """

# import logging
# from app.Agent.models import AgentState, QueryDecomposition
# from app.Agent.utils.llm_config import llm
# from app.Agent.query_decomposer.prompts import get_decomposition_prompt

# logger = logging.getLogger(__name__)


# class QueryDecomposer:
#     """
#     Decomposes user queries into individual sub-questions
    
#     Simplified approach:
#     - All queries handled by Azure LLM for maximum accuracy
#     - Caching layer ensures fast responses for repeated queries (<1s)
#     - New queries: 7-13s with high accuracy
#     """
    
#     def __init__(self, llm_instance=None):
#         """
#         Initialize decomposer with optional LLM instance
        
#         Args:
#             llm_instance: Optional custom LLM instance (defaults to global llm)
#         """
#         self.llm = llm_instance or llm
#         self.decomposer_llm = self.llm.with_structured_output(QueryDecomposition)
    
#     def decompose(self, state: AgentState) -> dict:
#         """
#         Break down user's message into individual sub-questions
        
#         Args:
#             state: Current agent state with user message
            
#         Returns:
#             dict: Updated state with sub_queries, is_multiple, query_results
#         """
#         last_message = state.messages[-1]
#         question = last_message.content if hasattr(last_message, 'content') else last_message["content"]
        
#         logger.info(f"📥 Decomposing query: {question}")
        
#         # Use LLM for all queries - caching handles performance
#         try:
#             result = self.decomposer_llm.invoke([
#                 {"role": "system", "content": get_decomposition_prompt()},
#                 {"role": "user", "content": question}
#             ])
            
#             logger.info(f"🔍 LLM decomposed into {len(result.sub_queries)} sub-queries")
#             for i, sq in enumerate(result.sub_queries):
#                 logger.info(f"   Q{i+1}: type='{sq.query_type}' | '{sq.question}'")
            
#             return {
#                 "sub_queries": result.sub_queries,
#                 "is_multiple": result.is_multiple,
#                 "query_results": [],
#                 "current_query_index": 0
#             }
            
#         except Exception as e:
#             logger.error(f"❌ LLM decomposition failed: {e}")
#             # Fallback: treat as single general query
#             from app.Agent.models import SubQuery
#             return {
#                 "sub_queries": [SubQuery(question=question, query_type="general")],
#                 "is_multiple": False,
#                 "query_results": [],
#                 "current_query_index": 0
#             }


# def decompose_query_node(state: AgentState) -> dict:
#     """
#     LangGraph node wrapper for QueryDecomposer
    
#     Args:
#         state: Current agent state
        
#     Returns:
#         dict: Updated state with decomposition results
#     """
#     decomposer = QueryDecomposer()
#     return decomposer.decompose(state)


"""
Main query decomposer - Orchestrates the decomposition process
Single Responsibility: Coordinates decomposition flow
Optimized: Azure LLM handles all queries with caching for performance
"""

import logging
from app.Agent.models import AgentState, QueryDecomposition
from app.Agent.utils.llm_config import llm
from app.Agent.query_decomposer.prompts import get_decomposition_prompt

logger = logging.getLogger(__name__)


class QueryDecomposer:
    """
    Decomposes user queries into individual sub-questions
    
    Simplified approach:
    - All queries handled by Azure LLM for maximum accuracy
    - Caching layer ensures fast responses for repeated queries (<1s)
    - New queries: 7-13s with high accuracy
    """
    
    def __init__(self, llm_instance=None):
        """
        Initialize decomposer with optional LLM instance
        
        Args:
            llm_instance: Optional custom LLM instance (defaults to global llm)
        """
        self.llm = llm_instance or llm
        self.decomposer_llm = self.llm.with_structured_output(QueryDecomposition)
    
    def decompose(self, state: AgentState) -> dict:
        """
        Break down user's message into individual sub-questions
        
        Args:
            state: Current agent state with user message
            
        Returns:
            dict: Updated state with sub_queries, is_multiple, query_results, intent
        """
        last_message = state.messages[-1]
        question = last_message.content if hasattr(last_message, 'content') else last_message["content"]
        
        logger.info(f"📥 Decomposing query: {question}")
        
        # Use LLM for all queries - caching handles performance
        try:
            result = self.decomposer_llm.invoke([
                {"role": "system", "content": get_decomposition_prompt()},
                {"role": "user", "content": question}
            ])
            
            # Extract intent if present (for general queries with 0 sub-queries)
            intent = getattr(result, 'intent', None) if hasattr(result, 'intent') else None
            
            logger.info(f"🔍 LLM decomposed into {len(result.sub_queries)} sub-queries")
            if intent:
                logger.info(f"🎯 Detected intent: {intent}")
            for i, sq in enumerate(result.sub_queries):
                logger.info(f"   Q{i+1}: type='{sq.query_type}' | '{sq.question}'")
            
            return {
                "sub_queries": result.sub_queries,
                "is_multiple": result.is_multiple,
                "intent": intent,
                "query_results": [],
                "current_query_index": 0
            }
            
        except Exception as e:
            logger.error(f"❌ LLM decomposition failed: {e}")
            # Fallback: treat as single general query
            from app.Agent.models import SubQuery
            return {
                "sub_queries": [SubQuery(question=question, query_type="general")],
                "is_multiple": False,
                "intent": "other",
                "query_results": [],
                "current_query_index": 0
            }


def decompose_query_node(state: AgentState) -> dict:
    """
    LangGraph node wrapper for QueryDecomposer
    
    Args:
        state: Current agent state
        
    Returns:
        dict: Updated state with decomposition results
    """
    decomposer = QueryDecomposer()
    return decomposer.decompose(state)