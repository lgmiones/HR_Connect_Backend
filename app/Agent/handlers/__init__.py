"""
Handler factory - Open/Closed Principle
Easy to add new handlers without modifying existing code
"""

from app.Agent.handlers.base_handler import BaseQueryHandler
from app.Agent.handlers.policy_handler import PolicyQueryHandler
from app.Agent.handlers.personal_data_handler import PersonalDataQueryHandler
from app.Agent.handlers.general_handler import GeneralQueryHandler


class QueryHandlerFactory:
    """Factory for creating appropriate query handlers"""
    
    def __init__(self):
        self._handlers = [
            PolicyQueryHandler(),
            PersonalDataQueryHandler(),
            GeneralQueryHandler()
        ]
    
    def get_handler(self, query_type: str) -> BaseQueryHandler:
        """
        Get the appropriate handler for a query type
        
        Args:
            query_type: The type of query (policy, personal_data, general)
            
        Returns:
            Handler instance that can process the query type
            
        Raises:
            ValueError: If no handler found for query type
        """
        for handler in self._handlers:
            if handler.can_handle(query_type):
                return handler
        
        # Fallback to general handler
        return GeneralQueryHandler()


# Singleton instance
handler_factory = QueryHandlerFactory()