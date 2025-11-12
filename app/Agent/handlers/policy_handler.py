"""
Policy query handler - Single Responsibility Principle
Only handles policy-related queries using vector database
"""

import logging
from app.Agent.handlers.base_handler import BaseQueryHandler
from app.services.retriever import query_hr_documents

logger = logging.getLogger(__name__)


class PolicyQueryHandler(BaseQueryHandler):
    """Handles policy questions using RAG (Chroma DB)"""
    
    def can_handle(self, query_type: str) -> bool:
        return query_type == "policy"
    
    def handle(self, question: str, user_id: int | None = None) -> str:
        """
        Handle policy questions using vector database
        
        Args:
            question: Policy-related question
            user_id: Not used for policy queries
            
        Returns:
            Policy information from HR documents
        """
        logger.info(f"Handling policy query: {question}")
        
        try:
            rag_result = query_hr_documents(question)
            return f"**{question}**\n\n{rag_result['answer']}"
        except Exception as e:
            logger.error(f"Error in policy query: {str(e)}")
            return f"**{question}**\n\nSorry, I encountered an error retrieving policy information."