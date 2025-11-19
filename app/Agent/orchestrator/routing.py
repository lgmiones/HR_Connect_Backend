"""
Routing logic for query orchestration
Decides between sequential, parallel, or merge execution
"""

import logging
from app.Agent.models import AgentState

logger = logging.getLogger(__name__)


def should_continue(state: AgentState) -> str:
    """
    Determine if we should process more sub-queries (for sequential processing)
    
    Args:
        state: Current agent state
        
    Returns:
        'continue' if more queries to process, 'finish' if done
    """
    sub_queries = state.sub_queries or []
    current_index = state.current_query_index
    
    return "continue" if current_index < len(sub_queries) else "finish"


def should_merge_or_parallel(state: AgentState) -> str:
    """
    Decide between merging policy queries, parallel execution, or sequential
    
    Strategy:
    - 1 query → Sequential (simple)
    - All policy queries → Merge with LCEL (fastest, most coherent)
    - Mixed query types → Parallel execution (independent processing)
    
    Args:
        state: Current agent state
        
    Returns:
        'sequential', 'merge_policy', or 'parallel'
    """
    sub_queries = state.sub_queries or []
    
    # Single query - use sequential
    if len(sub_queries) <= 1:
        logger.info(f"➡️ Routing to SEQUENTIAL (1 query)")
        return "sequential"
    
    # Log routing decision details
    _log_routing_decision(sub_queries)
    
    # Check if ALL queries are policy-related
    all_policy = all(sq.query_type == "policy" for sq in sub_queries)
    
    if all_policy:
        logger.info(f"🔀 All {len(sub_queries)} queries are policy-related → MERGING with LCEL")
        return "merge_policy"
    else:
        logger.info(f"🔀 Mixed query types → PARALLEL execution")
        return "parallel"


def _log_routing_decision(sub_queries: list) -> None:
    """Log detailed routing decision for debugging"""
    logger.warning("=" * 60)
    logger.warning("🔍 ORCHESTRATOR: Routing Decision")
    for i, sq in enumerate(sub_queries):
        logger.warning(f"   Q{i+1}: type='{sq.query_type}' | question='{sq.question}'")
    logger.warning("=" * 60)


def get_query_type_summary(sub_queries: list) -> dict:
    """
    Analyze query types in the batch
    
    Args:
        sub_queries: List of SubQuery objects
        
    Returns:
        dict with counts of each query type
    """
    summary = {
        "policy": 0,
        "personal_data": 0,
        "general": 0,
        "total": len(sub_queries)
    }
    
    for sq in sub_queries:
        query_type = sq.query_type
        if query_type in summary:
            summary[query_type] += 1
    
    return summary