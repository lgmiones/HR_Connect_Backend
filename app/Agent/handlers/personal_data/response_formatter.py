"""
Response formatter for personal data queries
Uses LLM to generate natural language responses
"""

import logging
from app.Agent.utils.llm_config import get_llm

logger = logging.getLogger(__name__)


def generate_history_response(question: str, history_data: list[dict]) -> str:
    """
    Use LLM to generate natural language response for leave history
    
    Args:
        question: User's original question
        history_data: List of leave history records
        
    Returns:
        Natural language response formatted by LLM
    """
    try:
        # Format history data for LLM
        history_text = "\n".join([
            f"- {record['type']} Leave: {record['days']} day(s) on {record['date']}, Reason: {record['reason']}"
            for record in history_data
        ])
        
        # Create prompt for LLM
        prompt = _build_history_prompt(question, history_text)
        
        # Generate response using LLM
        llm = get_llm()
        response = llm.invoke(prompt)
        
        # Format with question header
        return f"**{question}**\n\n{response.content if hasattr(response, 'content') else response}"
        
    except Exception as e:
        logger.error(f"LLM error generating history response: {e}", exc_info=True)
        
        # Fallback: Return structured list if LLM fails
        return _fallback_history_response(question, history_data)


def _build_history_prompt(question: str, history_text: str) -> str:
    """Build the LLM prompt for history response generation"""
    return f"""You are an HR assistant. Answer the user's question about their leave history based on the data provided.

User's Question: {question}

User's Leave History (most recent first):
{history_text}

Instructions:
- Answer the user's specific question naturally and conversationally
- Be concise but informative
- Use bullet points if listing multiple items
- If the user asked about a specific type of leave, focus on that
- If the user asked about recent leaves, mention the most recent ones
- Include relevant details like dates, days taken, and reasons when appropriate

Your response:"""


def _fallback_history_response(question: str, history_data: list[dict]) -> str:
    """
    Fallback response if LLM fails
    Returns structured list of history
    """
    lines = [f"**{question}**\n", "**Your Leave History:**\n"]
    
    for record in history_data[:5]:  # Show top 5
        lines.append(f"• {record['type']} - {record['days']} day(s) on {record['date']}")
        lines.append(f"  Reason: {record['reason']}")
    
    return "\n".join(lines)