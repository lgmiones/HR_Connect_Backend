"""
Personal data query handler - Single Responsibility Principle
Orchestrates personal data queries (balance and history)
"""

import logging
from app.Agent.handlers.base_handler import BaseQueryHandler
from app.Agent.handlers.personal_data import (
    detect_intent,
    detect_leave_type,
    get_leave_balance,
    get_leave_history,
    generate_history_response
)

logger = logging.getLogger(__name__)


class PersonalDataQueryHandler(BaseQueryHandler):
    """
    Handles personal data questions using SQL database
    
    Orchestrates intent detection, data retrieval, and response formatting
    """
    
    def can_handle(self, query_type: str) -> bool:
        return query_type == "personal_data"
    
    def handle(self, question: str, user_id: int | None = None) -> str:
        """
        Handle personal data questions
        
        Args:
            question: Personal data question
            user_id: Required for database queries
            
        Returns:
            Formatted response based on query intent
        """
        logger.info(f"Handling personal data query for user {user_id}: {question}")
        
        # Check authentication
        if not user_id:
            return f"**{question}**\n\nYou need to log in to access your personal data."
        
        # Detect intent
        intent = detect_intent(question)
        
        # Route to appropriate handler
        if intent == 'balance':
            return self._handle_balance_query(question, user_id)
        elif intent == 'history':
            return self._handle_history_query(question, user_id)
        else:
            return self._handle_unknown_query(question)
    
    def _handle_balance_query(self, question: str, user_id: int) -> str:
        """Handle leave balance queries"""
        logger.info("Intent: leave balance")
        return get_leave_balance(question, user_id)
    
    def _handle_history_query(self, question: str, user_id: int) -> str:
        """Handle leave history queries"""
        logger.info("Intent: leave history")
        
        # Detect which leave types to query
        leave_types = detect_leave_type(question)
        logger.info(f"Leave types to query: {leave_types}")
        
        # Get history data
        history_data = get_leave_history(question, user_id, leave_types)
        
        # Check if any history found
        if not history_data:
            return f"**{question}**\n\nYou don't have any leave request history yet."
        
        # Generate natural language response with LLM
        return generate_history_response(question, history_data)
    
    def _handle_unknown_query(self, question: str) -> str:
        """Handle queries with unclear intent"""
        return (
            f"**{question}**\n\n"
            "I can help with:\n"
            "• Leave balance queries (e.g., 'How many vacation days do I have left?')\n"
            "• Leave history/request records (e.g., 'What leaves did I take last month?')\n\n"
            "Try asking about your vacation, sick, or emergency leaves."
        )