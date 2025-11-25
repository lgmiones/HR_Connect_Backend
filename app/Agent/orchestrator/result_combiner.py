# """
# Result combination logic
# Merges multiple query results into final response
# """

# import logging
# from app.Agent.models import AgentState

# logger = logging.getLogger(__name__)


# def combine_results(state: AgentState) -> dict:
#     """
#     Combine all sub-query results into final answer
    
#     Handles:
#     - Single result: Return as-is
#     - Multiple results: Concatenate with formatting
#     - No results: Error message
    
#     Args:
#         state: Current agent state
        
#     Returns:
#         Updated state dict with final answer
#     """
#     query_results = state.query_results or []
#     sub_queries = state.sub_queries or []
    
#     # Build final answer
#     if not query_results:
#         final_answer = _build_error_message()
#     elif len(query_results) == 1:
#         final_answer = query_results[0]
#     else:
#         final_answer = _build_multi_result_answer(query_results)
    
#     # Determine query_type for metadata
#     query_type = _determine_query_type(sub_queries)
    
#     logger.info(f"✅ Combined {len(query_results)} results (type: {query_type})")
    
#     return {
#         "messages": [{"role": "assistant", "content": final_answer}],
#         "query_type": query_type,        
#         "is_multiple": state.is_multiple, 
#         "sub_queries": sub_queries       
#     }


# def _build_error_message() -> str:
#     """Build error message when no results available"""
#     return "I couldn't process your questions. Please try again."


# def _build_multi_result_answer(query_results: list) -> str:
#     """
#     Build final answer from multiple results
    
#     Args:
#         query_results: List of individual query results
        
#     Returns:
#         Combined formatted answer
#     """
#     # Simple concatenation with spacing
#     return "\n\n".join(query_results)


# def _determine_query_type(sub_queries: list) -> str:
#     """
#     Determine overall query type for metadata
    
#     Args:
#         sub_queries: List of SubQuery objects
        
#     Returns:
#         'compound', or the type of single query, or 'general'
#     """
#     if not sub_queries:
#         return "general"
    
#     if len(sub_queries) > 1:
#         return "compound"
    
#     return sub_queries[0].query_type


# def get_query_stats(state: AgentState) -> dict:
#     """
#     Get statistics about the query processing
    
#     Useful for debugging and analytics
    
#     Args:
#         state: Current agent state
        
#     Returns:
#         dict with query statistics
#     """
#     sub_queries = state.sub_queries or []
#     query_results = state.query_results or []
    
#     return {
#         "total_queries": len(sub_queries),
#         "completed_queries": len(query_results),
#         "is_multiple": state.is_multiple,
#         "query_types": [sq.query_type for sq in sub_queries]
#     }



"""
Result combination logic
Merges multiple query results into final response
"""

import logging
from app.Agent.models import AgentState
from app.Agent.handlers.general.llm_responder import generate_llm_response

logger = logging.getLogger(__name__)


def combine_results(state: AgentState) -> dict:
    """
    Combine all sub-query results into final answer
    
    Handles:
    - Single result: Return as-is
    - Multiple results: Concatenate with formatting
    - No results but original query exists: Generate LLM response for general queries
    - No results: Error message
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state dict with final answer
    """
    query_results = state.query_results or []
    sub_queries = state.sub_queries or []
    
    # Extract original query from messages
    original_query = None
    if state.messages:
        last_message = state.messages[-1]
        original_query = last_message.content if hasattr(last_message, 'content') else last_message.get("content")
    
    # Build final answer
    if not query_results and not sub_queries and original_query:
        # This is a general query (greeting, thanks, help, etc.)
        # Use intent from decomposer (already detected by LLM)
        intent = getattr(state, 'intent', None) or 'other'
        logger.info(f"🎯 Using intent from decomposer: {intent}")
        
        try:
            final_answer = generate_llm_response(original_query, intent)
            query_type = "general"
        except Exception as e:
            logger.error(f"Failed to generate LLM response: {e}", exc_info=True)
            final_answer = _build_error_message()
            query_type = "error"
    elif not query_results:
        final_answer = _build_error_message()
        query_type = "error"
    elif len(query_results) == 1:
        final_answer = query_results[0]
        query_type = _determine_query_type(sub_queries)
    else:
        final_answer = _build_multi_result_answer(query_results)
        query_type = _determine_query_type(sub_queries)
    
    logger.info(f"✅ Combined {len(query_results)} results (type: {query_type})")
    
    return {
        "messages": [{"role": "assistant", "content": final_answer}],
        "query_type": query_type,        
        "is_multiple": state.is_multiple, 
        "sub_queries": sub_queries       
    }


def _build_error_message() -> str:
    """Build error message when no results available"""
    return "I couldn't process your questions. Please try again."


def _build_multi_result_answer(query_results: list) -> str:
    """
    Build final answer from multiple results
    
    Args:
        query_results: List of individual query results
        
    Returns:
        Combined formatted answer
    """
    # Simple concatenation with spacing
    return "\n\n".join(query_results)


def _determine_query_type(sub_queries: list) -> str:
    """
    Determine overall query type for metadata
    
    Args:
        sub_queries: List of SubQuery objects
        
    Returns:
        'compound', or the type of single query, or 'general'
    """
    if not sub_queries:
        return "general"
    
    if len(sub_queries) > 1:
        return "compound"
    
    return sub_queries[0].query_type


def get_query_stats(state: AgentState) -> dict:
    """
    Get statistics about the query processing
    
    Useful for debugging and analytics
    
    Args:
        state: Current agent state
        
    Returns:
        dict with query statistics
    """
    sub_queries = state.sub_queries or []
    query_results = state.query_results or []
    
    return {
        "total_queries": len(sub_queries),
        "completed_queries": len(query_results),
        "is_multiple": state.is_multiple,
        "query_types": [sq.query_type for sq in sub_queries]
    }