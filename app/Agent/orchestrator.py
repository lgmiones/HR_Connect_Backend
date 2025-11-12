"""
LangGraph orchestrator - coordinates the overall workflow
Single Responsibility: Only manages workflow logic
"""

import logging
from langgraph.graph import StateGraph, START, END

from app.Agent.models import AgentState
from app.Agent.query_decomposer import decompose_query_node
from app.Agent.handlers import handler_factory

logger = logging.getLogger(__name__)


# ============================================
# LangGraph Nodes
# ============================================

def process_subquery(state: AgentState) -> dict:
    """Process one sub-query at a time using appropriate handler"""
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


def should_continue(state: AgentState) -> str:
    """Determine if we should process more sub-queries"""
    sub_queries = state.sub_queries or []
    current_index = state.current_query_index
    
    return "continue" if current_index < len(sub_queries) else "finish"


def combine_results(state: AgentState) -> dict:
    """Combine all sub-query results into final answer"""
    query_results = state.query_results or []
    
    if not query_results:
        final_answer = "I couldn't process your questions. Please try again."
    elif len(query_results) == 1:
        final_answer = query_results[0]
    else:
        final_answer = "Here are the answers to your questions:\n\n" + "\n\n---\n\n".join(query_results)
    
    return {
        "messages": [{"role": "assistant", "content": final_answer}]
    }


# ============================================
# Build Graph
# ============================================

def create_agentic_orchestrator():
    """Build and compile the LangGraph workflow"""
    graph_builder = StateGraph(AgentState)

    # Add nodes
    graph_builder.add_node("decompose", decompose_query_node)
    graph_builder.add_node("process", process_subquery)
    graph_builder.add_node("combine", combine_results)

    # Build workflow
    graph_builder.add_edge(START, "decompose")
    graph_builder.add_edge("decompose", "process")
    
    # Loop through sub-queries
    graph_builder.add_conditional_edges(
        "process",
        should_continue,
        {
            "continue": "process",
            "finish": "combine"
        }
    )
    
    graph_builder.add_edge("combine", END)

    return graph_builder.compile()


# Create the compiled graph
hr_agent_graph = create_agentic_orchestrator()
logger.info("HR Agent Graph compiled successfully")