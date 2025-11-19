"""
ChromaDB vectorstore service
Handles document retrieval operations
"""

import logging
from langchain_chroma import Chroma
from langchain_openai import AzureOpenAIEmbeddings
from app.core.config import settings

logger = logging.getLogger(__name__)

# ============================================
# Singleton Vectorstore
# ============================================

_embedding = None
_vectorstore = None


def get_vectorstore():
    """
    Get or create vectorstore with Azure embeddings (singleton)
    
    Returns:
        Chroma vectorstore instance
    """
    global _embedding, _vectorstore
    
    if _vectorstore is None:
        logger.info("Initializing Azure embeddings and vectorstore...")
        
        _embedding = AzureOpenAIEmbeddings(
            azure_endpoint=settings.AZURE_EMBEDDINGS_ENDPOINT,
            azure_deployment=settings.AZURE_EMBEDDINGS_DEPLOYMENT,
            api_key=settings.AZURE_EMBEDDINGS_API_KEY,
            api_version=settings.AZURE_OPENAI_API_VERSION
        )
        
        _vectorstore = Chroma(
            persist_directory="./chroma_db",
            collection_name="hr_documents",
            embedding_function=_embedding
        )
        logger.info("✅ Vectorstore initialized and cached")
    
    return _vectorstore


# ============================================
# Document Retrieval
# ============================================

def retrieve_documents(question: str, k: int = 2) -> str:
    """
    Retrieve relevant documents from ChromaDB for a single question
    
    Args:
        question: Single HR policy question
        k: Number of documents to retrieve
        
    Returns:
        Formatted context string with retrieved documents
    """
    try:
        vectorstore = get_vectorstore()
        
        # ChromaDB search (includes Azure embedding API call)
        docs = vectorstore.similarity_search(query=question, k=k)
        
        # Build context
        context = "\n\n".join([
            f"Document {i+1}:\n{doc.page_content}" 
            for i, doc in enumerate(docs)
        ])
        
        # Trim if too long
        max_context_length = 1000
        if len(context) > max_context_length:
            context = context[:max_context_length] + "..."
        
        logger.info(f"Retrieved {len(docs)} documents ({len(context)} chars)")
        return context
        
    except Exception as e:
        logger.error(f"ChromaDB retrieval error: {str(e)}", exc_info=True)
        return "Error retrieving documents."


def retrieve_documents_broad(questions: list[str], k: int = 3) -> str:
    """
    Retrieve documents using multiple questions for broader context
    Optimized for compound queries
    
    Args:
        questions: List of related policy questions
        k: Number of documents to retrieve
        
    Returns:
        Formatted context string with retrieved documents
    """
    try:
        vectorstore = get_vectorstore()
        
        # Combine questions for broader retrieval
        combined_query = " | ".join(questions)
        
        # ChromaDB search
        docs = vectorstore.similarity_search(query=combined_query, k=k)
        
        # Build context
        context = "\n\n".join([
            f"Document {i+1}:\n{doc.page_content}" 
            for i, doc in enumerate(docs)
        ])
        
        # Aggressive trimming for speed
        max_context_length = 1000
        if len(context) > max_context_length:
            context = context[:max_context_length] + "..."
        
        logger.info(f"Retrieved {len(docs)} documents for compound query ({len(context)} chars)")
        return context
        
    except Exception as e:
        logger.error(f"ChromaDB compound retrieval error: {str(e)}", exc_info=True)
        return "Error retrieving documents."