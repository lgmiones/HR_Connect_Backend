"""
General query handler - Single Responsibility Principle
Handles general questions about the system
"""

import logging
from app.Agent.handlers.base_handler import BaseQueryHandler

logger = logging.getLogger(__name__)


class GeneralQueryHandler(BaseQueryHandler):
    """Handles general questions about HRConnect"""
    
    def can_handle(self, query_type: str) -> bool:
        return query_type == "general"
    
    def handle(self, question: str, user_id: int | None = None) -> str:
        """
        Handle general questions
        
        Args:
            question: General question about the system
            user_id: Not typically used for general queries
            
        Returns:
            General information about HRConnect
        """
        logger.info(f"Handling general query: {question}")
        
        question_lower = question.lower()
        
        # Pre-defined responses for common questions
        if "what can you do" in question_lower or "help" in question_lower:
            return self._get_help_response(question)
        elif "hrconnect" in question_lower or "what is this" in question_lower:
            return self._get_about_response(question)
        elif "feature" in question_lower:
            return self._get_features_response(question)
        else:
            return f"**{question}**\n\nI'm here to help with HR policies and your personal HR data. What would you like to know?"
    
    @staticmethod
    def _get_help_response(question: str) -> str:
        return f"""**{question}**

I'm your HRConnect assistant! I can help you with:

🔍 **Policy Information**: Answer questions about company policies, guidelines, and procedures
📊 **Personal Data**: Check your leave balances, attendance records, and leave request status
❓ **General Help**: Answer HR-related questions

Try asking me:
- "What's the leave policy?" (I'll check our policy documents)
- "How many vacation days do I have?" (I'll check your personal data)
- "Show my attendance this week" (I'll get your records)"""
    
    @staticmethod
    def _get_about_response(question: str) -> str:
        return f"""**{question}**

HRConnect is our Human Resource Information System that helps streamline HR processes including:

- Attendance tracking and time modification
- Leave management (file, view, and cancel requests)  
- Access to company policies and procedures
- Employee self-service portal

I'm the chatbot assistant integrated with HRConnect to help you access information quickly!"""
    
    @staticmethod
    def _get_features_response(question: str) -> str:
        return f"""**{question}**

Available HRConnect Features:

For Employees:
✅ File modification requests
✅ Submit leave requests  
✅ Check remaining leave balance
✅ Ask about HR policies
✅ View attendance records

For HR:
✅ Review/approve/reject requests
✅ Monitor employee attendance
✅ Dashboard analytics

You can access these through the HRConnect system or ask me for help!"""