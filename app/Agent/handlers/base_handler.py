"""
Base handler interface - Dependency Inversion Principle
All query handlers must implement this interface
"""

from abc import ABC, abstractmethod


class BaseQueryHandler(ABC):
    """Abstract base class for all query handlers"""
    
    @abstractmethod
    def handle(self, question: str, user_id: int | None = None) -> str:
        """
        Handle a query and return the answer
        
        Args:
            question: The user's question
            user_id: Optional user ID for personalized queries
            
        Returns:
            Formatted answer string
        """
        pass
    
    @abstractmethod
    def can_handle(self, query_type: str) -> bool:
        """
        Check if this handler can process the given query type
        
        Args:
            query_type: The type of query (policy, personal_data, general)
            
        Returns:
            True if this handler can process the query type
        """
        pass