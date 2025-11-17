"""
Retriever service - OPTIMIZED with Azure Embeddings (maximum performance)
"""

import os
import logging
import time
from langchain_chroma import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import AzureOpenAIEmbeddings
from dotenv import load_dotenv
from app.core.config import settings
from app.Agent.utils.llm_config import get_llm

load_dotenv()
logger = logging.getLogger(__name__)

_embedding = None
_vectorstore = None


def get_vectorstore():
    """Get or create vectorstore with Azure embeddings (singleton)"""
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


def query_hr_documents(question: str, k: int = 2):  # ✅ Reduced to 2 docs
    """
    Query HR documents - MAXIMUM OPTIMIZATION with Azure Embeddings
    
    Performance targets with Azure Embeddings:
    - Query embedding: ~2.7s (Azure API - cannot optimize)
    - ChromaDB search: ~0.1s
    - LLM generation: ~5-6s (optimized)
    - Total: ~8-9s
    """
    
    total_start = time.time()
    
    try:
        logger.info(f"🔍 Querying: {question}")
        
        # Get vectorstore (cached)
        vs_start = time.time()
        vectorstore = get_vectorstore()
        logger.info(f"⏱️ Vectorstore: {(time.time() - vs_start):.2f}s")

        # ChromaDB search (includes Azure embedding API call)
        search_start = time.time()
        docs = vectorstore.similarity_search(query=question, k=k)
        logger.info(f"⏱️ ChromaDB search (with Azure embedding): {(time.time() - search_start):.2f}s")
        logger.info(f"Retrieved {len(docs)} documents")

        # Build context - AGGRESSIVE trimming
        context = "\n\n".join([d.page_content for d in docs])
        
        max_context_length = 1000  # ✅ Very aggressive for speed
        if len(context) > max_context_length:
            context = context[:max_context_length] + "..."
        
        logger.info(f"📝 Context: {len(context)} chars")

        # Get LLM (cached)
        llm = get_llm()

        # ✅ ULTRA-MINIMAL prompt (absolute minimum tokens)
        prompt = PromptTemplate(
            input_variables=["context", "question"],
            template="Policy:\n{context}\n\nQ: {question}\nA:",
        )

        # LLM call
        llm_start = time.time()
        chain = prompt | llm | StrOutputParser()
        answer = chain.invoke({"context": context, "question": question})
        llm_time = time.time() - llm_start
        
        total_time = time.time() - total_start
        
        logger.info(f"⏱️ LLM: {llm_time:.2f}s")
        logger.info(f"⏱️ TOTAL: {total_time:.2f}s")
        logger.info(f"   Breakdown: Embedding+Search={time.time()-total_start-llm_time:.2f}s + LLM={llm_time:.2f}s")

        return {"answer": answer}
    
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        raise