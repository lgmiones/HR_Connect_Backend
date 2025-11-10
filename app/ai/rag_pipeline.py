"""
Agentic RAG Pipeline for HRConnect Chatbot
"""
from typing import List, Dict, Optional
import logging
from app.ai.vector_store import get_vector_store
from app.ai.llm import get_llm_client
from app.core.config import settings

logger = logging.getLogger(__name__)


class RAGPipeline:
    """Retrieval-Augmented Generation Pipeline"""
    
    def __init__(self):
        """Initialize RAG pipeline with vector store and LLM"""
        self.vector_store = get_vector_store()
        self.llm_client = get_llm_client()
        self.conversation_history: List[Dict[str, str]] = []
    
    def retrieve_context(self, query: str) -> List[str]:
        """
        Retrieve relevant context from vector store
        
        Args:
            query: User query
            
        Returns:
            List of relevant document excerpts
        """
        try:
            results = self.vector_store.query(
                query_text=query,
                n_results=settings.TOP_K_RESULTS
            )
            
            # Extract documents from results
            documents = results.get('documents', [[]])[0]
            distances = results.get('distances', [[]])[0]
            
            # Filter by similarity threshold
            relevant_docs = [
                doc for doc, dist in zip(documents, distances)
                if dist <= (1 - settings.SIMILARITY_THRESHOLD)  # Convert to distance
            ]
            
            logger.info(f"Retrieved {len(relevant_docs)} relevant documents")
            return relevant_docs
            
        except Exception as e:
            logger.error(f"Error retrieving context: {str(e)}")
            return []
    
    def format_context(self, documents: List[str], employee_data: Optional[Dict] = None) -> str:
        """
        Format retrieved documents and employee data into context
        
        Args:
            documents: Retrieved documents from vector store
            employee_data: Optional employee-specific data from SQL database
            
        Returns:
            Formatted context string
        """
        context_parts = []
        
        # Add HR policy context
        if documents:
            context_parts.append("=== HR POLICIES AND INFORMATION ===")
            for i, doc in enumerate(documents, 1):
                context_parts.append(f"\n[Policy {i}]\n{doc}")
        
        # Add employee-specific data
        if employee_data:
            context_parts.append("\n=== EMPLOYEE INFORMATION ===")
            for key, value in employee_data.items():
                context_parts.append(f"{key}: {value}")
        
        return "\n\n".join(context_parts)
    
    def build_prompt(
        self,
        query: str,
        context: str,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> List[Dict[str, str]]:
        """
        Build the prompt for the LLM
        
        Args:
            query: User query
            context: Retrieved context
            conversation_history: Optional conversation history
            
        Returns:
            List of message dictionaries for the LLM
        """
        system_prompt = """You are HRConnect Assistant, an AI-powered HR chatbot for employee assistance.

Your responsibilities:
1. Answer questions about HR policies, leave management, and company procedures
2. Provide accurate information based on the context provided
3. Be helpful, professional, and concise
4. If you don't have enough information, admit it and suggest contacting HR directly
5. Always cite the relevant policy when providing information

Guidelines:
- Use the context provided to answer questions
- If employee data is provided, personalize your response
- Keep responses clear and actionable
- Use a friendly but professional tone
- For leave balance queries, provide specific numbers
- For policy questions, explain clearly and cite sources

Context:
{context}
"""
        
        messages = [
            {"role": "system", "content": system_prompt.format(context=context)}
        ]
        
        # Add conversation history if provided
        if conversation_history:
            # Limit history to prevent token overflow
            recent_history = conversation_history[-settings.MAX_CONVERSATION_HISTORY:]
            messages.extend(recent_history)
        
        # Add current query
        messages.append({"role": "user", "content": query})
        
        return messages
    
    def generate_response(
        self,
        query: str,
        employee_data: Optional[Dict] = None,
        use_history: bool = True
    ) -> Dict[str, any]:
        """
        Generate a response using the RAG pipeline
        
        Args:
            query: User query
            employee_data: Optional employee-specific data
            use_history: Whether to use conversation history
            
        Returns:
            Dictionary containing response and metadata
        """
        try:
            # Step 1: Retrieve relevant context
            documents = self.retrieve_context(query)
            
            # Step 2: Format context
            context = self.format_context(documents, employee_data)
            
            # Step 3: Build prompt
            conversation_history = self.conversation_history if use_history else None
            messages = self.build_prompt(query, context, conversation_history)
            
            # Step 4: Generate response
            response_text = self.llm_client.generate_response(messages)
            
            # Step 5: Update conversation history
            if use_history:
                self.conversation_history.append({"role": "user", "content": query})
                self.conversation_history.append({"role": "assistant", "content": response_text})
                
                # Trim history if too long
                if len(self.conversation_history) > settings.MAX_CONVERSATION_HISTORY * 2:
                    self.conversation_history = self.conversation_history[-settings.MAX_CONVERSATION_HISTORY * 2:]
            
            return {
                "response": response_text,
                "sources_count": len(documents),
                "has_employee_data": employee_data is not None
            }
            
        except Exception as e:
            logger.error(f"Error in RAG pipeline: {str(e)}")
            return {
                "response": "I apologize, but I encountered an error processing your request. Please try again or contact HR directly.",
                "error": str(e),
                "sources_count": 0,
                "has_employee_data": False
            }
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        logger.info("Conversation history cleared")
    
    def get_history(self) -> List[Dict[str, str]]:
        """
        Get conversation history
        
        Returns:
            List of conversation messages
        """
        return self.conversation_history.copy()


# Global RAG pipeline instance per session
_rag_pipelines: Dict[str, RAGPipeline] = {}


def get_rag_pipeline(session_id: str = "default") -> RAGPipeline:
    """
    Get or create a RAG pipeline for a session
    
    Args:
        session_id: Unique session identifier
        
    Returns:
        RAGPipeline instance
    """
    if session_id not in _rag_pipelines:
        _rag_pipelines[session_id] = RAGPipeline()
    return _rag_pipelines[session_id]


def clear_session(session_id: str):
    """
    Clear a session's RAG pipeline
    
    Args:
        session_id: Session identifier to clear
    """
    if session_id in _rag_pipelines:
        del _rag_pipelines[session_id]
        logger.info(f"Cleared RAG pipeline for session: {session_id}")
