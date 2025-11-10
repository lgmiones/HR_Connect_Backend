# embed_documents.py
import os
from sentence_transformers import SentenceTransformer
from langchain_chroma.vectorstores import Chroma
from langchain.embeddings.base import Embeddings
from file_loader import load_hr_documents, split_documents
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SentenceTransformerEmbeddings(Embeddings):
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        from sentence_transformers import SentenceTransformer
        self.model = SentenceTransformer(model_name)

    def embed_documents(self, texts):
        return self.model.encode(
            texts,
            show_progress_bar=True,
            convert_to_numpy=True,
            normalize_embeddings=True
        ).tolist()

    def embed_query(self, text):
        return self.model.encode(
            [text],
            convert_to_numpy=True,
            normalize_embeddings=True
        )[0].tolist()

class DocumentEmbedder:
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        self.model_name = model_name
    
    def embed_function(self, texts):
        """Enhanced embedding function with progress tracking"""
        logger.info(f"🔧 Generating embeddings for {len(texts)} chunks...")
        embeddings = self.model.encode(
            texts,
            show_progress_bar=True,
            convert_to_numpy=True,
            normalize_embeddings=True,  # Important for similarity search
            batch_size=32  # Adjust based on available memory
        )
        logger.info(f"✅ Generated embeddings shape: {embeddings.shape}")
        return embeddings

def setup_vector_store():
    """Main function to setup ChromaDB with documents"""
    
    # Load and process documents
    logger.info("📚 Loading HR documents...")
    docs = load_hr_documents("./data/hr_docs")
    
    if not docs:
        logger.error("❌ No documents found to process!")
        return None
    
    logger.info("✂️ Splitting documents into chunks...")
    split_docs = split_documents(docs, chunk_size=800, chunk_overlap=150)
    
    # Initialize embedder
    embedding = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    
    # Create vector store
    logger.info("💾 Creating vector store...")
    
    vectorstore = Chroma.from_documents(
        documents=split_docs,
        embedding=embedding,
        persist_directory="./chroma_db",
        collection_name="hr_documents"
    )
    
    # Verify setup
    collection_count = vectorstore._collection.count()
    logger.info(f"🎉 ChromaDB setup complete! Collection has {collection_count} documents")
    
    return vectorstore

if __name__ == "__main__":
    vectorstore = setup_vector_store()
    if vectorstore:
        logger.info("✅ HR Document embedding pipeline completed successfully!")
    else:
        logger.error("❌ HR Document embedding pipeline failed!")