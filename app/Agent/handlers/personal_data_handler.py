"""
Personal data query handler - Single Responsibility Principle
Only handles user-specific data queries using SQL database
"""

import logging
from sqlalchemy import text
from app.Agent.handlers.base_handler import BaseQueryHandler
from app.db.session import get_db

logger = logging.getLogger(__name__)


class PersonalDataQueryHandler(BaseQueryHandler):
    """Handles personal data questions using SQL database"""
    
    def can_handle(self, query_type: str) -> bool:
        return query_type == "personal_data"
    
    def handle(self, question: str, user_id: int | None = None) -> str:
        """
        Handle personal data questions using SQL database
        
        Args:
            question: Personal data question
            user_id: Required for database queries
            
        Returns:
            User's personal data from database
        """
        logger.info(f"Handling personal data query for user {user_id}: {question}")
        
        if not user_id:
            return f"**{question}**\n\nYou need to log in to access your personal data."
        
        # Check query intent
        if self._is_leave_balance_query(question):
            return self._get_leave_balance(question, user_id)
        else:
            return f"**{question}**\n\nI can help with leave balance queries. Try asking about your remaining leaves."
    
    @staticmethod
    def _is_leave_balance_query(question: str) -> bool:
        """Check if question is about leave balance"""
        keywords = ['leave', 'balance', 'remaining', 'left', 'how many', 'vacation', 'sick']
        return any(keyword in question.lower() for keyword in keywords)
    
    def _get_leave_balance(self, question: str, user_id: int) -> str:
        """Query database for leave balance"""
        db = next(get_db())
        
        try:
            result = db.execute(
                text("SELECT total_leaves, used_leaves FROM leave_balance WHERE user_id = :user_id"),
                {"user_id": user_id}
            ).fetchone()
            
            if result:
                total_leaves = result[0]
                used_leaves = int(result[1]) if result[1] else 0
                remaining_leaves = total_leaves - used_leaves
                
                return f"""**{question}**

Your Leave Balance:
- Total leaves allocated: {total_leaves}
- Leaves used: {used_leaves}
- **Leaves remaining: {remaining_leaves}**

You have {remaining_leaves} leave days available."""
            else:
                return f"**{question}**\n\nNo leave balance record found for your account."
                
        except Exception as e:
            logger.error(f"Database error: {str(e)}")
            return f"**{question}**\n\nSorry, I encountered a database error."
        finally:
            db.close()