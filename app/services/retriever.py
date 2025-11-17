"""
Retriever service - OPTIMIZED with Azure Embeddings, caching, and detailed timing
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

# ✅ OPTIMIZATION: Singleton pattern - cache embeddings and vectorstore
_embedding = None
_vectorstore = None


def get_vectorstore():
    """Get or create vectorstore instance with Azure embeddings (singleton)"""
    global _embedding, _vectorstore
    
    if _vectorstore is None:
        logger.info("Initializing Azure embeddings and vectorstore...")
        
        # ✅ Use Azure OpenAI Embeddings
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


def query_hr_documents(question: str, k: int = 3):
    """
    Query HR documents using ChromaDB + LLM with detailed timing
    
    OPTIMIZATIONS:
    - Cached Azure embeddings (singleton)
    - Cached vectorstore (singleton)
    - Cached LLM instance (singleton)
    - Reduced k to 3 (fewer docs)
    - Context trimming to 1500 chars
    - Performance monitoring
    
    Args:
        question: User's question
        k: Number of documents to retrieve (default: 3)
        
    Returns:
        dict with 'answer' key
    """
    
    total_start = time.time()
    
    try:
        logger.info(f"🔍 Querying HR documents: {question}")
        
        # TIME: Get vectorstore (cached)
        vs_start = time.time()
        vectorstore = get_vectorstore()
        vs_time = time.time() - vs_start
        logger.info(f"⏱️ Get vectorstore: {vs_time:.2f}s")

        # TIME: ChromaDB similarity search
        search_start = time.time()
        docs = vectorstore.similarity_search(query=question, k=k)
        search_time = time.time() - search_start
        logger.info(f"⏱️ ChromaDB search: {search_time:.2f}s")
        logger.info(f"Retrieved {len(docs)} documents")

        # TIME: Build context with trimming
        context_start = time.time()
        context = "\n\n".join([d.page_content for d in docs])
        
        # ✅ OPTIMIZATION: Aggressive context trimming
        max_context_length = 1500
        if len(context) > max_context_length:
            context = context[:max_context_length] + "..."
            logger.info(f"Context trimmed to {max_context_length} chars")
        
        context_time = time.time() - context_start
        logger.info(f"⏱️ Build context: {context_time:.2f}s")

        # TIME: Get LLM (cached)
        llm_get_start = time.time()
        llm = get_llm()
        llm_get_time = time.time() - llm_get_start
        logger.info(f"⏱️ Get LLM: {llm_get_time:.2f}s")

        # ✅ OPTIMIZATION: Concise prompt
        prompt = PromptTemplate(
            input_variables=["context", "question"],
            template=(
                "Answer based on the HR policy below. Be concise.\n\n"
                "Policy:\n{context}\n\n"
                "Question: {question}\n\n"
                "Answer:"
            ),
        )

        # TIME: LLM invocation (THE BOTTLENECK)
        llm_start = time.time()
        chain = prompt | llm | StrOutputParser()
        answer = chain.invoke({"context": context, "question": question})
        llm_time = time.time() - llm_start
        
        total_time = time.time() - total_start
        
        # Log performance breakdown
        logger.info(f"⏱️ LLM generation: {llm_time:.2f}s 🐌 (Azure API)")
        logger.info(f"⏱️ TOTAL: {total_time:.2f}s")
        logger.info(f"Answer generated successfully (length: {len(answer)} chars)")

        return {"answer": answer}
    
    except Exception as e:
        logger.error(f"Error in query_hr_documents: {e}", exc_info=True)
        raise