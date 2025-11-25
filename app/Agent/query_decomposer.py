"""
Backward compatibility wrapper for query decomposer
Imports from new modular structure
"""

from app.Agent.query_decomposer.decomposer import QueryDecomposer, decompose_query_node

__all__ = [
    "QueryDecomposer",
    "decompose_query_node"
]