# """
# LLM configuration and initialization
# """

# import os
# from dotenv import load_dotenv
# from langchain.chat_models import init_chat_model

# load_dotenv()


# def get_llm(temperature: float = 0.3):
#     """
#     Get configured LLM instance
    
#     Args:
#         temperature: Controls randomness (0.0 = deterministic, 1.0 = creative)
    
#     Returns:
#         Configured ChatGroq LLM instance
#     """
#     return init_chat_model(
#         "llama-3.1-8b-instant",
#         model_provider="groq",
#         temperature=temperature
#     )


# # Default LLM instance
# llm = get_llm()


# """
# LLM configuration and initialization
# """

# import os
# from dotenv import load_dotenv
# from langchain_openai import AzureChatOpenAI
# from app.core.config import settings

# load_dotenv()


# def get_llm(temperature: float = 0.3):
#     """
#     Get configured LLM instance (Azure OpenAI)
    
#     Args:
#         temperature: Controls randomness (0.0 = deterministic, 1.0 = creative)
    
#     Returns:
#         Configured AzureChatOpenAI LLM instance
#     """
#     return AzureChatOpenAI(
#         azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
#         azure_deployment=settings.AZURE_OPENAI_DEPLOYMENT,
#         api_key=settings.AZURE_OPENAI_API_KEY,
#         api_version=settings.AZURE_OPENAI_API_VERSION,
#         temperature=temperature
#     )


# # Default LLM instance
# llm = get_llm()


"""
LLM configuration with fallback
"""

import os
import logging
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langchain.chat_models import init_chat_model
from app.core.config import settings

load_dotenv()
logger = logging.getLogger(__name__)


def get_llm(temperature: float = 1.0):
    """
    Get configured LLM instance with fallback
    
    Priority:
    1. Azure OpenAI (if configured)
    2. Groq (fallback)
    
    Args:
        temperature: Controls randomness
    
    Returns:
        Configured LLM instance
    """
    # Try Azure OpenAI first
    if settings.AZURE_OPENAI_API_KEY and settings.AZURE_OPENAI_ENDPOINT:
        try:
            logger.info("Using Azure OpenAI")
            return AzureChatOpenAI(
                azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
                azure_deployment=settings.AZURE_OPENAI_DEPLOYMENT,
                api_key=settings.AZURE_OPENAI_API_KEY,
                api_version=settings.AZURE_OPENAI_API_VERSION,
                temperature=temperature
            )
        except Exception as e:
            logger.warning(f"Azure OpenAI failed: {e}. Falling back to Groq.")
    
    # Fallback to Groq
    if settings.GROQ_API_KEY:
        logger.info("Using Groq as fallback")
        return init_chat_model(
            "llama-3.1-8b-instant",
            model_provider="groq",
            temperature=temperature
        )
    
    raise ValueError("No LLM provider configured! Set AZURE_OPENAI_API_KEY or GROQ_API_KEY")


# Default LLM instance
llm = get_llm()
