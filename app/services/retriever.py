"""
Retriever service - Main API for querying HR documents
OPTIMIZED with LCEL chains, Azure Embeddings, and Response Caching
"""

import logging
import time
from app.services.cache import (
    get_cache_key,
    get_from_cache,
    store_in_cache,
    clear_cache,
    get_cache_stats,
    CACHE_TTL
)
from app.services.chains import rag_chain, compound_rag_chain

logger = logging.getLogger(__name__)


# ============================================
# Public API Functions
# ============================================

def query_hr_documents(question: str, k: int = 2, use_cache: bool = True):
    """
    Query HR documents using LCEL chain with response caching
    
    OPTIMIZATION: Cached responses return in <0.1s (99% faster!)
    
    Performance:
    - First query: ~13-17s (Azure embedding + LLM)
    - Cached query: <0.1s (instant!) ⚡⚡⚡
    
    Args:
        question: Single HR policy question
        k: Number of documents to retrieve
        use_cache: Enable response caching (default: True)
        
    Returns:
        dict with 'answer' key
    """
    
    # ✅ CHECK CACHE FIRST
    if use_cache:
        cache_key = get_cache_key(question)
        cached_result = get_from_cache(cache_key)
        
        if cached_result:
            logger.info(f"⚡⚡⚡ CACHE HIT - Instant response! (saved ~13s)")
            return cached_result
    
    # Cache miss - query normally
    total_start = time.time()
    
    try:
        logger.info(f"🔍 RAG query: {question}")
        
        answer = rag_chain.invoke({"question": question, "k": k})
        
        total_time = time.time() - total_start
        logger.info(f"⏱️ TOTAL: {total_time:.2f}s")
        
        result = {"answer": answer}
        
        # ✅ STORE IN CACHE
        if use_cache:
            store_in_cache(cache_key, result)
            logger.info(f"💾 Cached response (TTL: {CACHE_TTL.total_seconds()/3600:.1f}h)")
        
        return result
        
    except Exception as e:
        logger.error(f"RAG error: {str(e)}", exc_info=True)
        raise


def query_compound_policies(questions: list[str], k: int = 3, use_cache: bool = True):
    """
    Query HR documents for multiple related policy questions with caching
    
    OPTIMIZATION: Single retrieval + LLM call, with response caching
    
    Performance:
    - First compound query: ~13-15s
    - Cached compound query: <0.1s ⚡⚡⚡
    
    Args:
        questions: List of related policy questions
        k: Number of documents to retrieve
        use_cache: Enable response caching (default: True)
        
    Returns:
        dict with 'answer' key
    """
    
    # ✅ CHECK CACHE FIRST (use combined questions as key)
    if use_cache:
        combined_question = " | ".join(questions)
        cache_key = get_cache_key(combined_question)
        cached_result = get_from_cache(cache_key)
        
        if cached_result:
            logger.info(f"⚡⚡⚡ COMPOUND CACHE HIT - Instant response!")
            return cached_result
    
    # Cache miss - query normally
    total_start = time.time()
    
    try:
        logger.info(f"🔍 Compound RAG query with {len(questions)} questions")
        
        # Use compound LCEL chain
        answer = compound_rag_chain.invoke({"questions_list": questions, "k": k})
        
        total_time = time.time() - total_start
        logger.info(f"⏱️ COMPOUND TOTAL: {total_time:.2f}s")
        
        result = {"answer": answer}
        
        # ✅ STORE IN CACHE
        if use_cache:
            store_in_cache(cache_key, result)
            logger.info(f"💾 Cached compound response (TTL: {CACHE_TTL.total_seconds()/3600:.1f}h)")
        
        return result
        
    except Exception as e:
        logger.error(f"Compound RAG error: {str(e)}", exc_info=True)
        raise


# ============================================
# Utility Functions
# ============================================

def prefetch_common_queries():
    """
    Pre-cache common HR queries on startup
    
    Call this function when server starts to warm up the cache
    
    Returns:
        Number of successfully cached queries
    """
    COMMON_QUERIES = [
        "What is the policy for filing a leave?",
        "How many leave credits do I have left?",
        "When is the payout schedule / payroll release date?",
        "How do I apply for a leave?",
        "Can unused leave be converted to cash?"
    ]
    
    logger.info(f"🔄 Prefetching {len(COMMON_QUERIES)} common queries...")
    
    success_count = 0
    for query in COMMON_QUERIES:
        try:
            query_hr_documents(query, use_cache=True)
            success_count += 1
            logger.info(f"  ✅ Cached: {query}")
        except Exception as e:
            logger.warning(f"  ⚠️ Failed to cache '{query}': {e}")
    
    logger.info(f"✅ Prefetch complete: {success_count}/{len(COMMON_QUERIES)} queries cached")
    return success_count


# Export utility functions
__all__ = [
    "query_hr_documents",
    "query_compound_policies",
    "prefetch_common_queries",
    "clear_cache",
    "get_cache_stats"
]