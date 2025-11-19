"""
Response caching service for RAG queries
Handles in-memory cache with TTL
"""

import logging
import hashlib
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# ============================================
# Cache Storage (In-Memory)
# ============================================

_rag_cache = {}
_cache_timestamps = {}
CACHE_TTL = timedelta(hours=1)  # Cache for 1 hour


# ============================================
# Cache Key Generation
# ============================================

def get_cache_key(question: str) -> str:
    """
    Generate cache key from question (case-insensitive)
    
    Args:
        question: Query string
        
    Returns:
        MD5 hash of normalized question
    """
    return hashlib.md5(question.lower().strip().encode()).hexdigest()


# ============================================
# Cache Operations
# ============================================

def get_from_cache(cache_key: str) -> dict | None:
    """
    Get cached response if valid
    
    Args:
        cache_key: Cache key hash
        
    Returns:
        Cached result dict or None if expired/missing
    """
    if cache_key in _rag_cache:
        # Check if cache is still valid
        if datetime.now() - _cache_timestamps[cache_key] < CACHE_TTL:
            return _rag_cache[cache_key]
        else:
            # Expired, remove from cache
            logger.debug(f"Cache expired for key: {cache_key[:8]}...")
            del _rag_cache[cache_key]
            del _cache_timestamps[cache_key]
    return None


def store_in_cache(cache_key: str, result: dict):
    """
    Store result in cache with timestamp
    
    Args:
        cache_key: Cache key hash
        result: Result dict to cache
    """
    _rag_cache[cache_key] = result
    _cache_timestamps[cache_key] = datetime.now()
    logger.debug(f"Stored in cache: {cache_key[:8]}...")


def clear_cache():
    """Clear all cached responses (admin function)"""
    global _rag_cache, _cache_timestamps
    count = len(_rag_cache)
    _rag_cache = {}
    _cache_timestamps = {}
    logger.info(f"🗑️ Cache cleared ({count} entries removed)")


def clear_expired():
    """Remove only expired entries from cache"""
    now = datetime.now()
    expired_keys = [
        key for key, timestamp in _cache_timestamps.items()
        if now - timestamp >= CACHE_TTL
    ]
    
    for key in expired_keys:
        del _rag_cache[key]
        del _cache_timestamps[key]
    
    if expired_keys:
        logger.info(f"🗑️ Removed {len(expired_keys)} expired cache entries")


# ============================================
# Cache Statistics
# ============================================

def get_cache_stats() -> dict:
    """
    Get cache statistics
    
    Returns:
        Dict with cache metrics
    """
    return {
        "cache_size": len(_rag_cache),
        "cache_ttl_hours": CACHE_TTL.total_seconds() / 3600,
        "total_keys": len(_rag_cache),
        "sample_keys": list(_rag_cache.keys())[:5]  # First 5 keys
    }


def get_cache_hit_rate() -> dict:
    """
    Get cache hit rate (requires tracking hits/misses)
    Note: This is a placeholder for future implementation
    """
    return {
        "hits": 0,  # TODO: Implement hit tracking
        "misses": 0,  # TODO: Implement miss tracking
        "hit_rate": 0.0
    }