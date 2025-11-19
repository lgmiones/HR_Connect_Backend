"""
LangGraph workflow builder
Constructs and compiles the agent orchestration graph
"""

import logging
from langgraph.graph import StateGraph, START, END
from app.Agent.models import AgentState
from app.Agent.query_decomposer import decompose_query_node
from app.Agent.orchestrator.nodes import (
    process_subquery,
    process_all_subqueries_parallel,
    merge_and_query_policies
)
from app.Agent.orchestrator.routing import (
    should_continue,
    should_merge_or_parallel
)
from app.Agent.orchestrator.result_combiner import combine_results

logger = logging.getLogger(__name__)


def create_agentic_orchestrator():
    """
    Build and compile the LangGraph workflow with parallel execution and smart merging
    
    Workflow:
    1. Decompose query into sub-queries
    2. Route based on query types:
       - All policy → Merge with LCEL (fastest, most coherent)
       - Mixed types → Parallel execution (independent processing)
       - Single query → Sequential (simple)
    3. Process queries
    4. Combine results
    
    Returns:
        Compiled LangGraph workflow
    """
    graph_builder = StateGraph(AgentState)

    # Add nodes
    graph_builder.add_node("decompose", decompose_query_node)
    graph_builder.add_node("process_sequential", process_subquery)
    graph_builder.add_node("process_parallel", process_all_subqueries_parallel)
    graph_builder.add_node("merge_policy", merge_and_query_policies)
    graph_builder.add_node("combine", combine_results)

    # Build workflow edges
    _add_workflow_edges(graph_builder)

    logger.info("🚀 HR Agent Graph compiled with PARALLEL execution and LCEL policy merging")
    return graph_builder.compile()


def _add_workflow_edges(graph_builder: StateGraph) -> None:
    """
    Add all edges to the workflow graph
    
    Defines the flow between nodes and conditional routing
    """
    # Start with decomposition
    graph_builder.add_edge(START, "decompose")
    
    # Smart routing based on query types
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
    graph_builder.add_edge("merge_policy", "combine")
    
    # End workflow
    graph_builder.add_edge("combine", END)


def get_graph_visualization() -> str:
    """
    Get a text representation of the graph structure
    
    Useful for debugging and documentation
    
    Returns:
        Text representation of the workflow
    """
    return """
HR Agent Workflow:
    
START
  ↓
decompose (query decomposition)
  ↓
  ├─→ sequential (1 query) → loop → combine
  ├─→ parallel (mixed types) → combine
  └─→ merge_policy (all policy) → combine
       ↓
      END
"""