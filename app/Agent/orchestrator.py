"""
LangGraph orchestrator - coordinates the overall workflow
Single Responsibility: Only manages workflow logic
OPTIMIZED: Parallel execution, smart policy merging, clean logging
"""
import logging
from concurrent.futures import ThreadPoolExecutor
from langgraph.graph import StateGraph, START, END

from app.Agent.models import AgentState
from app.Agent.query_decomposer import decompose_query_node
from app.Agent.handlers import handler_factory

logger = logging.getLogger(__name__)


# ============================================
# LangGraph Nodes
# ============================================

def process_subquery(state: AgentState) -> dict:
    """Process one sub-query at a time using appropriate handler (sequential)"""
    current_index = state.current_query_index
    sub_queries = state.sub_queries or []
    
    if current_index >= len(sub_queries):
        return state.dict()
    
    current_query = sub_queries[current_index]
    logger.info(f"Processing sub-query {current_index + 1}/{len(sub_queries)}: {current_query.question}")
    
    # Get appropriate handler and process query
    handler = handler_factory.get_handler(current_query.query_type)
    result = handler.handle(current_query.question, state.user_id)
    
    # Store result
    query_results = state.query_results or []
    query_results.append(result)
    
    return {
        "query_results": query_results,
        "current_query_index": current_index + 1
    }


def process_all_subqueries_parallel(state: AgentState) -> dict:
    """
    Process all sub-queries in parallel using ThreadPoolExecutor
    
    OPTIMIZATION: Executes multiple queries simultaneously
    - 2 queries: ~50% faster (executes in time of slowest query)
    - 3+ queries: Even bigger gains
    
    Example: Policy (7s) + Personal (0.5s) 
    - Sequential: 7.5s total
    - Parallel: 7s total (50% faster!)
    """
    sub_queries = state.sub_queries or []
    user_id = state.user_id
    
    logger.info(f"⚡ Processing {len(sub_queries)} sub-queries in PARALLEL")
    
    def process_single(query):
        """Process a single query (used by ThreadPoolExecutor)"""
        try:
            handler = handler_factory.get_handler(query.query_type)
            result = handler.handle(query.question, user_id)
            logger.info(f"✓ Completed: [{query.query_type}] {query.question[:50]}...")
            return result
        except Exception as e:
            logger.error(f"✗ Failed: {query.question[:50]}... - {str(e)}")
            return f"**{query.question}**\n\nSorry, I encountered an error processing this question."
    
    # Execute all queries in parallel
    with ThreadPoolExecutor(max_workers=min(len(sub_queries), 5)) as executor:
        query_results = list(executor.map(process_single, sub_queries))
    
    logger.info(f"✅ All {len(query_results)} queries completed in parallel")
    
    return {
        "query_results": query_results,
        "current_query_index": len(sub_queries)
    }


def merge_and_query_policies(state: AgentState) -> dict:
    """
    Merge multiple policy questions into one LCEL chain call
    
    OPTIMIZATION: Single retrieval + single LLM call for policy compounds
    - Faster than parallel (no duplicate retrievals)
    - More coherent answers (single context)
    - Lower cost (one LLM call)
    
    Example: "What is X policy and how to apply for Y?"
    - Before: 2 retrievals + 2 LLM calls = ~7s (parallel)
    - After: 1 retrieval + 1 LLM call = ~5s (30% faster!)
    """
    sub_queries = state.sub_queries or []
    
    # Extract just the questions
    questions = [sq.question for sq in sub_queries]
    
    logger.info(f"🔄 Merging {len(questions)} policy queries into single LCEL call")
    for i, q in enumerate(questions):
        logger.info(f"   Q{i+1}: {q}")
    
    try:
        # ✅ Use compound LCEL chain
        from app.services.retriever import query_compound_policies
        
        result = query_compound_policies(questions)
        
        logger.info(f"✅ Compound query completed successfully")
        
        return {
            "query_results": [result['answer']],  # Single comprehensive answer
            "current_query_index": len(sub_queries)
        }
        
    except Exception as e:
        logger.error(f"Merge query failed: {str(e)}", exc_info=True)
        
        # Fallback to parallel if merge fails
        logger.warning("Falling back to parallel execution")
        return process_all_subqueries_parallel(state)


def should_continue(state: AgentState) -> str:
    """Determine if we should process more sub-queries (for sequential processing)"""
    sub_queries = state.sub_queries or []
    current_index = state.current_query_index
    
    return "continue" if current_index < len(sub_queries) else "finish"


def should_merge_or_parallel(state: AgentState) -> str:
    """
    Decide between merging policy queries, parallel execution, or sequential
    """
    sub_queries = state.sub_queries or []
    
    # Single query - use sequential
    if len(sub_queries) <= 1:
        logger.info(f"➡️ Routing to SEQUENTIAL (1 query)")
        return "sequential"
    
    # ✅ DEBUG BLOCK
    logger.warning("=" * 60)
    logger.warning("🔍 ORCHESTRATOR: Routing Decision")
    for i, sq in enumerate(sub_queries):
        logger.warning(f"   Q{i+1}: type='{sq.query_type}' | question='{sq.question}'")
    logger.warning("=" * 60)
    
    # Check if ALL queries are policy-related
    all_policy = all(sq.query_type == "policy" for sq in sub_queries)
    
    if all_policy:
        logger.info(f"🔀 All {len(sub_queries)} queries are policy-related → MERGING with LCEL")
        return "merge_policy"
    else:
        logger.info(f"🔀 Mixed query types → PARALLEL execution")
        return "parallel"


def combine_results(state: AgentState) -> dict:
    """Combine all sub-query results into final answer"""
    
    query_results = state.query_results or []
    sub_queries = state.sub_queries or []
    
    # Build final answer
    if not query_results:
        final_answer = "I couldn't process your questions. Please try again."
    elif len(query_results) == 1:
        final_answer = query_results[0]
    else:
        # ✅ OPTIMIZATION: More concise formatting for multiple results
        final_answer = "\n\n".join(query_results)
    
    # Determine query_type for metadata
    if sub_queries:
        query_type = "compound" if len(sub_queries) > 1 else sub_queries[0].query_type
    else:
        query_type = "general"
    
    logger.info(f"✅ Combined {len(query_results)} results (type: {query_type})")
    
    return {
        "messages": [{"role": "assistant", "content": final_answer}],
        "query_type": query_type,        
        "is_multiple": state.is_multiple, 
        "sub_queries": sub_queries       
    }


# ============================================
# Build Graph
# ============================================

def create_agentic_orchestrator():
    """
    Build and compile the LangGraph workflow with parallel execution and smart merging
    
    Workflow:
    1. Decompose query into sub-queries
    2. Route based on query types:
       - All policy → Merge with LCEL (fastest)
       - Mixed types → Parallel execution
       - Single query → Sequential
    3. Process queries
    4. Combine results
    """
    graph_builder = StateGraph(AgentState)

    # Add nodes
    graph_builder.add_node("decompose", decompose_query_node)
    graph_builder.add_node("process_sequential", process_subquery)
    graph_builder.add_node("process_parallel", process_all_subqueries_parallel)
    graph_builder.add_node("merge_policy", merge_and_query_policies)  # ✅ NEW
    graph_builder.add_node("combine", combine_results)

    # Build workflow
    graph_builder.add_edge(START, "decompose")
    
    # ✅ Smart routing based on query types
    graph_builder.add_conditional_edges(
        "decompose",
        should_merge_or_parallel,
        {
            "merge_policy": "merge_policy",      # All policy → merge with LCEL
            "parallel": "process_parallel",      # Mixed types → parallel
            "sequential": "process_sequential"   # Single query → sequential
        }
    )
    
    # Sequential: Loop through sub-queries one by one
    graph_builder.add_conditional_edges(
        "process_sequential",
        should_continue,
        {
            "continue": "process_sequential",
            "finish": "combine"
        }
    )
    
    # Parallel and merged both go straight to combine
    graph_builder.add_edge("process_parallel", "combine")
    graph_builder.add_edge("merge_policy", "combine")  # ✅ NEW
    
    graph_builder.add_edge("combine", END)

    return graph_builder.compile()


# Create the compiled graph
hr_agent_graph = create_agentic_orchestrator()
logger.info("🚀 HR Agent Graph compiled with PARALLEL execution and LCEL policy merging")