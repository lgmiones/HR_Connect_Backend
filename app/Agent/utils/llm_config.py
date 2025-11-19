"""
LLM configuration with fallback - OPTIMIZED
"""

import os
import logging
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langchain.chat_models import init_chat_model
from app.core.config import settings

load_dotenv()
logger = logging.getLogger(__name__)

# Singleton cache for LLM instances
_llm_cache = {}


def get_llm(temperature: float = 1.0):  # ✅ Back to 1.0 (model requirement)
    """
    Get configured LLM instance with fallback (SINGLETON PATTERN)
    
    OPTIMIZATION: Reuses same instance instead of creating new ones each time
    
    Priority:
    1. Azure OpenAI (if configured)
    2. Groq (fallback)
    
    Args:
        temperature: Controls randomness (default: 1.0 for Azure compatibility)
    
    Returns:
        Configured LLM instance
    """
    # Check cache first
    cache_key = f"azure_{temperature}"
    if cache_key in _llm_cache:
        return _llm_cache[cache_key]
    
    # Try Azure OpenAI first
    if settings.AZURE_OPENAI_API_KEY and settings.AZURE_OPENAI_ENDPOINT:
        try:
            logger.info(f"Initializing Azure OpenAI (temperature={temperature})")
            llm_instance = AzureChatOpenAI(
                azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
                azure_deployment=settings.AZURE_OPENAI_DEPLOYMENT,
                api_key=settings.AZURE_OPENAI_API_KEY,
                api_version=settings.AZURE_OPENAI_API_VERSION,
                temperature=temperature,
                timeout=30,
                max_retries=1
            )
            # Cache the instance
            _llm_cache[cache_key] = llm_instance
            logger.info("✅ Azure OpenAI initialized and cached")
            return llm_instance
        except Exception as e:
            logger.warning(f"Azure OpenAI failed: {e}. Falling back to Groq.")
    
    # Fallback to Groq
    if settings.GROQ_API_KEY:
        logger.info(f"Using Groq as fallback (temperature={temperature})")
        llm_instance = init_chat_model(
            "llama-3.1-8b-instant",
            model_provider="groq",
            temperature=temperature,
            timeout=15,
            max_retries=1
        )
        _llm_cache[cache_key] = llm_instance
        return llm_instance
    
    raise ValueError("No LLM provider configured! Set AZURE_OPENAI_API_KEY or GROQ_API_KEY")


# Default LLM instance (created once, reused everywhere)
llm = get_llm()  # ✅ Use default temperature=1.0
logger.info("🚀 Default LLM initialized")