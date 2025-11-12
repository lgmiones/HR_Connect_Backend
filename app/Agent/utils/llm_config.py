"""
LLM configuration and initialization
"""

import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

load_dotenv()


def get_llm(temperature: float = 0.3):
    """
    Get configured LLM instance
    
    Args:
        temperature: Controls randomness (0.0 = deterministic, 1.0 = creative)
    
    Returns:
        Configured ChatGroq LLM instance
    """
    return init_chat_model(
        "llama-3.1-8b-instant",
        model_provider="groq",
        temperature=temperature
    )


# Default LLM instance
llm = get_llm()