# embed_documents.py
import logging
from sentence_transformers import SentenceTransformer
from langchain_chroma import Chroma
from langchain.embeddings.base import Embeddings
from app.Chromadb.file_loader import load_hr_documents, split_documents
from langchain_openai import AzureOpenAIEmbeddings
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_azure_embedding():
    """Return Azure OpenAI Embedding instance."""
    return AzureOpenAIEmbeddings(
        azure_endpoint=settings.AZURE_EMBEDDINGS_ENDPOINT,
        azure_deployment=settings.AZURE_EMBEDDINGS_DEPLOYMENT,
        api_key=settings.AZURE_EMBEDDINGS_API_KEY,
        api_version=settings.AZURE_OPENAI_API_VERSION
    )


def setup_vector_store(
    docs_folder: str = "./data/hr_docs",
    persist_directory: str = "./chroma_db",
    collection_name: str = "hr_documents",
    chunk_size: int = 800,
    chunk_overlap: int = 150
):
    logger.info("📚 Loading documents...")
    docs = load_hr_documents(docs_folder)
    if not docs:
        logger.error("❌ No documents found. Aborting.")
        return None

    logger.info("✂️ Splitting documents into chunks...")
    split_docs = split_documents(docs, chunk_size=chunk_size, chunk_overlap=chunk_overlap)

    logger.info("🔧 Initializing Azure embedding function...")
    embedding = get_azure_embedding()

    logger.info("💾 Creating Chroma vector store (from_documents)...")
    vectorstore = Chroma.from_documents(
        documents=split_docs,
        embedding=embedding,
        persist_directory=persist_directory,
        collection_name=collection_name
    )

    try:
        count = vectorstore._collection.count()
        logger.info(f"🎉 Chroma collection '{collection_name}' contains {count} vectors")
    except:
        pass

    return vectorstore

if __name__ == "__main__":
    vs = setup_vector_store()
    if vs:
        logger.info("✅ Indexing complete.")
    else:
        logger.error("❌ Indexing failed.")