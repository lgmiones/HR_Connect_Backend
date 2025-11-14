# embed_documents.py
import logging
from sentence_transformers import SentenceTransformer
from langchain_chroma import Chroma
from langchain.embeddings.base import Embeddings
from app.Chromadb.file_loader import load_hr_documents, split_documents

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SentenceTransformerEmbeddings(Embeddings):
    """LangChain-compatible wrapper for sentence-transformers."""
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)

    def embed_documents(self, texts):
        # returns list[list[float]]
        emb = self.model.encode(
            texts,
            show_progress_bar=True,
            convert_to_numpy=True,
            normalize_embeddings=True,
            batch_size=32
        )
        return emb.tolist()

    def embed_query(self, text):
        emb = self.model.encode([text], convert_to_numpy=True, normalize_embeddings=True)
        return emb[0].tolist()

def setup_vector_store(
    docs_folder: str = "./data/hr_docs",
    persist_directory: str = "./chroma_db",
    collection_name: str = "hr_documents",
    chunk_size: int = 800,
    chunk_overlap: int = 150,
    model_name: str = "all-MiniLM-L6-v2",
):
    logger.info("📚 Loading documents...")
    docs = load_hr_documents(docs_folder)
    if not docs:
        logger.error("❌ No documents found. Aborting.")
        return None

    logger.info("✂️ Splitting documents into chunks...")
    split_docs = split_documents(docs, chunk_size=chunk_size, chunk_overlap=chunk_overlap)

    logger.info("🔧 Initializing embedding function...")
    embedding = SentenceTransformerEmbeddings(model_name=model_name)

    logger.info("💾 Creating Chroma vector store (from_documents)...")
    vectorstore = Chroma.from_documents(
        documents=split_docs,
        embedding=embedding,
        persist_directory=persist_directory,
        collection_name=collection_name
    )

    # Optionally log counts (safe call)
    try:
        count = vectorstore._collection.count()
        logger.info("🎉 Chroma collection '%s' contains %d vectors", collection_name, count)
    except Exception:
        logger.debug("Skipping collection.count() logging (not available).")

    return vectorstore

if __name__ == "__main__":
    vs = setup_vector_store()
    if vs:
        logger.info("✅ Indexing complete.")
    else:
        logger.error("❌ Indexing failed.")