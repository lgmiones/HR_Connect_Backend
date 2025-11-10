"""
ChromaDB Vector Store for HR Policy Documents
"""
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Optional
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)


class VectorStore:
    """Manages ChromaDB operations for HR policy documents"""
    
    def __init__(self):
        """Initialize ChromaDB client and collection"""
        self.client = chromadb.PersistentClient(
            path=settings.CHROMA_PERSIST_DIRECTORY
        )
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=settings.CHROMA_COLLECTION_NAME,
            metadata={"description": "HR policies and documentation"}
        )
        
        logger.info(f"ChromaDB collection '{settings.CHROMA_COLLECTION_NAME}' initialized")
    
    def add_documents(
        self,
        documents: List[str],
        metadatas: Optional[List[Dict]] = None,
        ids: Optional[List[str]] = None
    ) -> None:
        """
        Add documents to the vector store
        
        Args:
            documents: List of document texts
            metadatas: Optional list of metadata dictionaries
            ids: Optional list of document IDs
        """
        try:
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            logger.info(f"Added {len(documents)} documents to vector store")
        except Exception as e:
            logger.error(f"Error adding documents: {str(e)}")
            raise
    
    def query(
        self,
        query_text: str,
        n_results: int = None
    ) -> Dict:
        """
        Query the vector store for similar documents
        
        Args:
            query_text: Query string
            n_results: Number of results to return
            
        Returns:
            Dictionary containing query results
        """
        if n_results is None:
            n_results = settings.TOP_K_RESULTS
            
        try:
            results = self.collection.query(
                query_texts=[query_text],
                n_results=n_results
            )
            
            logger.info(f"Query returned {len(results['documents'][0])} results")
            return results
        except Exception as e:
            logger.error(f"Error querying vector store: {str(e)}")
            raise
    
    def get_all_documents(self) -> Dict:
        """
        Get all documents from the collection
        
        Returns:
            Dictionary containing all documents
        """
        try:
            return self.collection.get()
        except Exception as e:
            logger.error(f"Error retrieving documents: {str(e)}")
            raise
    
    def delete_collection(self) -> None:
        """Delete the entire collection"""
        try:
            self.client.delete_collection(name=settings.CHROMA_COLLECTION_NAME)
            logger.info(f"Deleted collection '{settings.CHROMA_COLLECTION_NAME}'")
        except Exception as e:
            logger.error(f"Error deleting collection: {str(e)}")
            raise
    
    def count_documents(self) -> int:
        """
        Get the count of documents in the collection
        
        Returns:
            Number of documents
        """
        return self.collection.count()


# Global vector store instance
_vector_store: Optional[VectorStore] = None


def get_vector_store() -> VectorStore:
    """
    Get or create the global vector store instance
    
    Returns:
        VectorStore instance
    """
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStore()
    return _vector_store


def initialize_vector_store() -> VectorStore:
    """
    Initialize the vector store (called at startup)
    
    Returns:
        VectorStore instance
    """
    return get_vector_store()
