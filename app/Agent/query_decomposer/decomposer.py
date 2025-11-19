"""
Main query decomposer - Orchestrates the decomposition process
Single Responsibility: Coordinates tier selection and decomposition flow
"""

import logging
from app.Agent.models import AgentState, QueryDecomposition, SubQuery
from app.Agent.utils.llm_config import llm
from app.Agent.query_decomposer.detectors import is_simple_query, quick_decompose
from app.Agent.query_decomposer.router import quick_route
from app.Agent.query_decomposer.prompts import get_decomposition_prompt

logger = logging.getLogger(__name__)


class QueryDecomposer:
    """
    Decomposes user queries into individual sub-questions
    
    Uses a three-tier approach:
    - TIER 1: Fast-path for simple queries (no LLM)
    - TIER 2: Rule-based for obvious compounds (no LLM)
    - TIER 3: LLM-based for complex queries
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
        Break down user's message into individual questions
        
        OPTIMIZATION: Three-tier approach for maximum speed
        - TIER 1: Simple queries (70% coverage, <0.01s)
        - TIER 2: Rule-based compounds (20% coverage, <0.01s)
        - TIER 3: LLM decomposition (10% coverage, 2-3s)
        
        Args:
            state: Current agent state with user message
            
        Returns:
            dict: Updated state with sub_queries, is_multiple, query_results
        """
        last_message = state.messages[-1]
        question = last_message.content if hasattr(last_message, 'content') else last_message["content"]
        
        logger.info(f"📥 Decomposing query: {question}")
        
        # ===== TIER 1: Simple single query fast-path =====
        if is_simple_query(question):
            return self._handle_simple_query(question)
        
        # ===== TIER 2: Rule-based compound decomposition =====
        is_compound, questions = quick_decompose(question)
        
        if is_compound and len(questions) > 1:
            return self._handle_compound_query(questions)
        
        # ===== TIER 3: Complex query - use LLM =====
        return self._handle_complex_query(question)
    
    def _handle_simple_query(self, question: str) -> dict:
        """
        Handle TIER 1: Simple single queries
        
        Args:
            question: User's simple question
            
        Returns:
            dict: State update with single sub-query
        """
        logger.info(f"⚡ TIER 1: Simple single query detected (saved ~2-3s)")
        
        query_type = quick_route(question)
        logger.info(f"   Route: {query_type}")
        
        return {
            "sub_queries": [SubQuery(question=question, query_type=query_type)],
            "is_multiple": False,
            "query_results": [],
            "current_query_index": 0
        }
    
    def _handle_compound_query(self, questions: list[str]) -> dict:
        """
        Handle TIER 2: Rule-based compound queries
        
        Args:
            questions: List of decomposed questions
            
        Returns:
            dict: State update with multiple sub-queries
        """
        logger.info(f"⚡ TIER 2: Rule-based decomposition into {len(questions)} questions (saved ~2-3s)")
        
        sub_queries = []
        for i, q in enumerate(questions):
            query_type = quick_route(q)
            sub_queries.append(SubQuery(question=q, query_type=query_type))
            logger.warning(f"   🔍 Q{i+1}: type='{query_type}' | '{q}'")
        
        return {
            "sub_queries": sub_queries,
            "is_multiple": True,
            "query_results": [],
            "current_query_index": 0
        }
    
    def _handle_complex_query(self, question: str) -> dict:
        """
        Handle TIER 3: Complex queries requiring LLM
        
        Args:
            question: User's complex question
            
        Returns:
            dict: State update with LLM-decomposed sub-queries
        """
        logger.info(f"🔍 TIER 3: Complex query - using LLM decomposition (~2-3s)")
        
        result = self.decomposer_llm.invoke([
            {
                "role": "system",
                "content": get_decomposition_prompt()
            },
            {"role": "user", "content": question}
        ])
        
        logger.info(f"   LLM decomposed into {len(result.sub_queries)} sub-queries")
        for i, sq in enumerate(result.sub_queries):
            logger.warning(f"   🔍 Q{i+1}: type='{sq.query_type}' | '{sq.question}'")
        
        return {
            "sub_queries": result.sub_queries,
            "is_multiple": result.is_multiple,
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