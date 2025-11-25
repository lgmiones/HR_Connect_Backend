"""
Response formatter for personal data queries
Optimized: Direct formatting for simple queries, LLM for complex analysis
"""

import logging
from app.Agent.utils.llm_config import get_llm

logger = logging.getLogger(__name__)


def generate_history_response(question: str, history_data: list[dict]) -> str:
    """
    Generate response for leave history queries
    
    Strategy:
    - Single recent record: Show most recent only
    - All records: Show complete list
    - Date-specific: Handle date queries
    - Complex: Use LLM
    """
    if not history_data:
        return f"**{question}**\n\nYou don't have any leave request history yet."
    
    question_lower = question.lower()
    
    # ===== Check for date-specific queries =====
    import re
    has_specific_date = re.search(
        r'\b(?:january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2}(?:st|nd|rd|th)?,?\s+\d{4}|\d{1,2}[/-]\d{1,2}[/-]\d{2,4}', 
        question_lower
    )
    
    if has_specific_date:
        logger.warning("⚠️ Date-specific query detected but database only stores request dates")
        return _handle_date_query_limitation(question, history_data)
    
    # ===== Check for RECENT/LAST/LATEST (singular) =====
    recent_keywords = ['recent', 'last', 'latest', 'most recent', 'last time', 'when did', 'when was']
    is_recent_query = any(keyword in question_lower for keyword in recent_keywords)
    
    # Check if singular (not plural) and not asking for "all"
    is_plural = any(word in question_lower for word in ['requests', 'leaves', 'all', 'entries', 'list'])
    
    if is_recent_query and not is_plural:
        logger.info("⚡ Showing most recent record only")
        return _show_most_recent(question, history_data)
    
    # ===== FAST PATH: List/show all records =====
    list_keywords = ['entries', 'list', 'show all', 'give me all', 'display all', 'all my']
    
    if is_plural or any(keyword in question_lower for keyword in list_keywords):
        logger.info("⚡ Using direct formatting (no LLM)")
        return _direct_list_response(question, history_data)
    
    # ===== LLM PATH: Complex analytical queries =====
    logger.info("🤖 Using LLM for complex analysis")
    return _llm_history_response(question, history_data)


def _show_most_recent(question: str, history_data: list[dict]) -> str:
    """
    Show only the most recent record
    For queries like "my recent sick leave", "when was the last time", etc.
    
    Performance: ~0.001s
    """
    most_recent = history_data[0]  # Already sorted by date (most recent first)
    
    # Determine phrasing based on question type
    if any(phrase in question.lower() for phrase in ['when', 'last time']):
        # "When was the last time..." style questions
        response = (
            f"**{question}**\n\n"
            f"Your most recent {most_recent['type'].lower()} leave request was on "
            f"**{most_recent['date']}**.\n\n"
            f"• **Duration:** {most_recent['days']} day(s)\n"
            f"• **Reason:** {most_recent['reason']}"
        )
    else:
        # "Give me my recent..." style questions
        response = (
            f"**{question}**\n\n"
            f"Your most recent {most_recent['type'].lower()} leave request:\n\n"
            f"• **Request Date:** {most_recent['date']}\n"
            f"• **Duration:** {most_recent['days']} day(s)\n"
            f"• **Reason:** {most_recent['reason']}"
        )
    
    # Add note if there are more records
    if len(history_data) > 1:
        response += f"\n\n*You have {len(history_data)} total {most_recent['type'].lower()} leave requests on file.*"
    
    logger.info(f"✅ Generated {len(response)} char response (single record)")
    
    return response


def _direct_list_response(question: str, history_data: list[dict]) -> str:
    """
    Direct formatting for list queries showing all records
    """
    lines = [f"**{question}**\n"]
    
    for i, record in enumerate(history_data, 1):
        lines.append(
            f"\n**{i}. Request Date: {record['date']}** - {record['type']} Leave\n"
            f"   • **Duration:** {record['days']} day(s)\n"
            f"   • **Reason:** {record['reason']}"
        )
    
    total_days = sum(r['days'] for r in history_data)
    lines.append(f"\n---\n**Summary:** {len(history_data)} total requests • {total_days} days used")
    
    result = "\n".join(lines)
    logger.info(f"✅ Generated {len(result)} char response ({len(history_data)} records)")
    
    return result


def _handle_date_query_limitation(question: str, history_data: list[dict]) -> str:
    """Handle date-specific queries when we only have request dates"""
    import re
    
    question_lower = question.lower()
    
    # Extract date from question
    month_match = re.search(
        r'(january|february|march|april|may|june|july|august|september|october|november|december)\s+(\d{1,2})(?:st|nd|rd|th)?,?\s+(\d{4})', 
        question_lower
    )
    
    matching_records = []
    
    if month_match:
        month_name = month_match.group(1).capitalize()
        day = int(month_match.group(2))
        year = int(month_match.group(3))
        
        # Match against request dates (created_at)
        for record in history_data:
            record_date = record.get('date', '')
            if month_name in record_date and f" {day}," in record_date and str(year) in record_date:
                matching_records.append(record)
    
    # Build response
    if matching_records:
        lines = [
            f"**{question}**\n",
            f"\n*Note: Showing leave requests created on this date.*\n",
            f"\nFound {len(matching_records)} leave request(s):\n"
        ]
        for record in matching_records:
            lines.append(
                f"• **{record['type']} Leave** - {record['days']} day(s)\n"
                f"  Request Date: {record['date']}\n"
                f"  Reason: {record['reason']}\n"
            )
        return "\n".join(lines)
    else:
        return (
            f"**{question}**\n\n"
            f"No leave requests were created on that date.\n\n"
            f"*Note: The system tracks when leave requests were created. "
            f"To see all your leave history, ask 'Show me all my leave entries'.*"
        )


def _llm_history_response(question: str, history_data: list[dict]) -> str:
    """
    LLM-powered response for complex analytical queries
    Only used for questions that need analysis/interpretation
    """
    try:
        # Send all records for better context (they're already limited to 10 per type)
        history_text = "\n".join([
            f"{record['type']}: {record['days']}d requested on {record['date']}, Reason: {record['reason']}"
            for record in history_data
        ])
        
        logger.info(f"📝 Sending {len(history_data)} records to LLM")
        
        prompt = f"""Answer the user's question based on this leave request data:

{history_text}

Question: {question}

Instructions:
- Answer directly and specifically
- Include dates and relevant details
- Keep it brief (2-3 sentences)
- These are REQUEST dates (when leave was requested)

Your answer:"""

        llm = get_llm()
        response = llm.invoke(prompt, max_completion_tokens=200)
        
        content = response.content if hasattr(response, 'content') else str(response)
        
        # Check for empty response
        if not content or len(content.strip()) == 0:
            logger.warning("⚠️ LLM returned empty, using fallback")
            return _fallback_history_response(question, history_data)
        
        logger.info(f"✅ LLM response: {len(content)} chars")
        return f"**{question}**\n\n{content}"
        
    except Exception as e:
        logger.error(f"LLM error: {e}", exc_info=True)
        return _fallback_history_response(question, history_data)


def _fallback_history_response(question: str, history_data: list[dict]) -> str:
    """Fallback response if LLM fails - show most recent"""
    most_recent = history_data[0]
    
    lines = [
        f"**{question}**\n",
        f"\nYour most recent leave request:\n",
        f"• **{most_recent['type']} Leave** on {most_recent['date']}\n",
        f"  Duration: {most_recent['days']} day(s)\n",
        f"  Reason: {most_recent['reason']}\n"
    ]
    
    if len(history_data) > 1:
        lines.append(f"\n*You have {len(history_data)} total leave requests on file.*")
    
    return "\n".join(lines)