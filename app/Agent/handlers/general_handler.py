"""
General query handler - Single Responsibility Principle
Handles general questions about the system with LLM-generated responses
"""

import logging
from app.Agent.handlers.base_handler import BaseQueryHandler
from app.Agent.handlers.general.llm_responder import generate_llm_response

logger = logging.getLogger(__name__)


class GeneralQueryHandler(BaseQueryHandler):
    """
    Handles general questions about HRConnect
    
    Uses LLM (AIVA) for natural, context-aware responses
    """
    
    def can_handle(self, query_type: str) -> bool:
        return query_type == "general"
    
    def handle(self, question: str, user_id: int | None = None) -> str:
        """
        Handle general questions with LLM-generated responses
        
        Args:
            question: General question about the system
            user_id: Not typically used for general queries
            
        Returns:
            Natural language response from AIVA
        """
        logger.info(f"Handling general query: {question}")
        
        try:
            # Use 'other' intent for general system questions
            # (greeting/thanks/help are handled separately with 0 sub-queries)
            response = generate_llm_response(question, intent='other')
            logger.info("✅ Generated LLM response for general query")
            return response
            
        except Exception as e:
            logger.error(f"❌ LLM response failed: {e}", exc_info=True)
            
            # Fallback error message
            return f"**{question}**\n\nI apologize, but I'm having trouble processing your question right now. Please try again or contact HR directly for assistance."