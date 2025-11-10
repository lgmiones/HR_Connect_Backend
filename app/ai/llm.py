"""
Azure OpenAI LLM Client
"""
from openai import AzureOpenAI
from typing import List, Dict, Optional
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)


class AzureLLMClient:
    """Client for Azure OpenAI Language Model"""
    
    def __init__(self):
        """Initialize Azure OpenAI client"""
        self.client = AzureOpenAI(
            api_key=settings.AZURE_OPENAI_API_KEY,
            api_version=settings.AZURE_OPENAI_API_VERSION,
            azure_endpoint=settings.AZURE_OPENAI_ENDPOINT
        )
        
        self.deployment_name = settings.AZURE_OPENAI_DEPLOYMENT_NAME
        logger.info("Azure OpenAI client initialized")
    
    def generate_response(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Generate a response from the LLM
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens in response
            
        Returns:
            Generated response text
        """
        if temperature is None:
            temperature = settings.AZURE_OPENAI_TEMPERATURE
        if max_tokens is None:
            max_tokens = settings.AZURE_OPENAI_MAX_TOKENS
        
        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            generated_text = response.choices[0].message.content
            logger.info(f"Generated response with {len(generated_text)} characters")
            
            return generated_text
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            raise
    
    def get_embeddings(self, text: str) -> List[float]:
        """
        Get embeddings for text using Azure OpenAI
        
        Args:
            text: Text to embed
            
        Returns:
            List of embedding values
        """
        try:
            response = self.client.embeddings.create(
                model=settings.AZURE_OPENAI_EMBEDDING_DEPLOYMENT,
                input=text
            )
            
            embeddings = response.data[0].embedding
            logger.info(f"Generated embeddings with dimension {len(embeddings)}")
            
            return embeddings
            
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            raise


# Global LLM client instance
_llm_client: Optional[AzureLLMClient] = None


def get_llm_client() -> AzureLLMClient:
    """
    Get or create the global LLM client instance
    
    Returns:
        AzureLLMClient instance
    """
    global _llm_client
    if _llm_client is None:
        _llm_client = AzureLLMClient()
    return _llm_client


def test_connection() -> bool:
    """
    Test Azure OpenAI connection
    
    Returns:
        True if connection successful, False otherwise
    """
    try:
        client = get_llm_client()
        response = client.generate_response(
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=10
        )
        logger.info("Azure OpenAI connection test successful")
        return True
    except Exception as e:
        logger.error(f"Azure OpenAI connection test failed: {str(e)}")
        return False
