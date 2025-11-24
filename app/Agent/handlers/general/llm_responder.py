"""
LLM-based response generation for general queries
Provides natural, context-aware responses
"""

import logging
from app.Agent.utils.llm_config import get_llm

logger = logging.getLogger(__name__)


def generate_llm_response(question: str, intent: str) -> str:
    """
    Generate natural response using LLM based on intent
    
    Args:
        question: User's question
        intent: Detected intent (help, about, features, etc.)
        
    Returns:
        LLM-generated response
    """
    try:
        llm = get_llm()
        prompt = _build_prompt(question, intent)
        
        response = llm.invoke(prompt)
        content = response.content if hasattr(response, 'content') else response
        
        # Format with question header
        return f"**{question}**\n\n{content}"
        
    except Exception as e:
        logger.error(f"LLM error generating general response: {e}", exc_info=True)
        raise


def _build_prompt(question: str, intent: str) -> str:
    """Build appropriate prompt based on intent"""
    
    # Base system context
    system_context = """You are the HRConnect chatbot assistant, helping employees with HR-related queries.

HRConnect System Overview:
- A Human Resource Information System (HRIS)
- Manages attendance, leave requests, policies, and employee data
- Provides self-service portal for employees
- Integrated chatbot for quick information access

Your Capabilities:
1. Policy Information: Answer questions about company policies, guidelines, procedures
2. Personal Data: Check leave balances, attendance records, leave history
3. General Help: Provide information about HR processes and HRConnect features

Key Features:
- Leave Management: File, view, cancel leave requests; check leave balance
- Attendance: Track attendance, file modification requests
- Policies: Access company policies and procedures
- Self-Service: Employee portal for HR tasks
"""
    
    # Intent-specific instructions
    intent_instructions = {
        'help': """
The user is asking about what you can do or how you can help.

Instructions:
- Explain your main capabilities clearly and concisely
- Give 2-3 specific examples of questions they can ask
- Be friendly and encouraging
- Keep it under 100 words
- DO NOT ask follow-up questions
- End naturally after explaining capabilities
""",
        'about': """
The user is asking about HRConnect or who/what you are.

Instructions:
- Briefly explain what HRConnect is (the HRIS system)
- Explain your role as the integrated chatbot assistant
- Mention 2-3 key benefits or features
- Keep it conversational and welcoming
- Keep it under 80 words
- DO NOT ask follow-up questions
- End naturally after explaining
""",
        'features': """
The user is asking about features or functionality.

Instructions:
- List key features for employees (leave, attendance, policies)
- Optionally mention HR admin features if relevant
- Use bullet points for clarity
- Be concise but informative
- Keep it under 100 words
- DO NOT ask follow-up questions
- End naturally after listing features
""",
        'greeting': """
The user is greeting you.

Instructions:
- Respond warmly and briefly
- Offer help in a single sentence
- Keep it very short (20-30 words)
- DO NOT ask questions
- Just greet and state availability
""",
        'other': """
The user has a general question about HR or the system.

Instructions:
- Answer naturally and conversationally
- Provide complete, helpful information
- Be friendly but professional
- Keep it under 80 words
- DO NOT ask follow-up questions
- End naturally after answering
"""
    }
    
    instruction = intent_instructions.get(intent, intent_instructions['other'])
    
    return f"""{system_context}

{instruction}

User's Question: {question}

Your response:"""

def should_use_llm(intent: str) -> bool:
    """
    Determine if LLM should be used for this intent
    
    Some intents benefit more from LLM's natural language,
    others are better served by templates
    
    Args:
        intent: Detected intent
        
    Returns:
        bool: True if LLM should be used
    """
    # Always use LLM for better responses
    return True
    
    # Alternative: Use templates for some, LLM for others
    # return intent in ['other', 'greeting']  # Use LLM only for these