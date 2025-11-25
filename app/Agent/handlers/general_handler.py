"""
General query handler - Single Responsibility Principle
Handles general questions about the system with LLM-generated responses
"""

import logging
from app.Agent.handlers.base_handler import BaseQueryHandler
from app.Agent.handlers.general import (
    detect_general_intent,
    generate_llm_response,
    should_use_llm,
    get_help_template,
    get_about_template,
    get_features_template,
    get_greeting_template,
    get_default_template
)

logger = logging.getLogger(__name__)


class GeneralQueryHandler(BaseQueryHandler):
    """
    Handles general questions about HRConnect
    
    Uses LLM for natural responses with template fallbacks
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
            Natural language response about HRConnect
        """
        logger.info(f"Handling general query: {question}")
        
        # Detect intent
        intent = detect_general_intent(question)
        logger.info(f"Detected intent: {intent}")
        
        # Use LLM for natural responses
        if should_use_llm(intent):
            try:
                return generate_llm_response(question, intent)
            except Exception as e:
                logger.error(f"LLM response failed, using template fallback: {e}")
                return self._get_template_response(question, intent)
        else:
            # Use pre-defined templates (faster)
            return self._get_template_response(question, intent)
    
    def _get_template_response(self, question: str, intent: str) -> str:
        """
        Get template-based response as fallback
        
        Args:
            question: User's question
            intent: Detected intent
            
        Returns:
            Pre-defined template response
        """
        template_map = {
            'help': get_help_template,
            'about': get_about_template,
            'features': get_features_template,
            'greeting': get_greeting_template,
            'other': get_default_template
        }
        
        template_func = template_map.get(intent, get_default_template)
        return template_func(question)