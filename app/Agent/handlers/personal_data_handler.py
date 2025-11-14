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
            return f"**{question}**\n\nI can help with leave balance queries. Try asking about your vacation, sick, or emergency leaves."
    
    @staticmethod
    def _is_leave_balance_query(question: str) -> bool:
        """Check if question is about leave balance"""
        keywords = ['leave', 'balance', 'remaining', 'left', 'how many', 'vacation', 'sick', 'emergency', 'days off']
        return any(keyword in question.lower() for keyword in keywords)
    
    def _get_leave_balance(self, question: str, user_id: int) -> str:
        """Query database for all leave balances"""
        db = next(get_db())
        
        try:
            # Query all three leave types
            vacation_result = db.execute(
                text("SELECT total_days, used_days FROM vacation_leave WHERE user_id = :user_id"),
                {"user_id": user_id}
            ).fetchone()
            
            sick_result = db.execute(
                text("SELECT total_days, used_days FROM sick_leave WHERE user_id = :user_id"),
                {"user_id": user_id}
            ).fetchone()
            
            emergency_result = db.execute(
                text("SELECT total_days, used_days FROM emergency_leave WHERE user_id = :user_id"),
                {"user_id": user_id}
            ).fetchone()
            
            # Format concise response
            lines = []
            
            # Vacation Leave
            if vacation_result:
                vacation_remaining = vacation_result[0] - (vacation_result[1] or 0)
                lines.append(f"🏖️ Vacation: {vacation_remaining}/{vacation_result[0]} days")
            
            # Sick Leave
            if sick_result:
                sick_remaining = sick_result[0] - (sick_result[1] or 0)
                lines.append(f"🏥 Sick: {sick_remaining}/{sick_result[0]} days")
            
            # Emergency Leave
            if emergency_result:
                emergency_remaining = emergency_result[0] - (emergency_result[1] or 0)
                lines.append(f"🚨 Emergency: {emergency_remaining}/{emergency_result[0]} days")
            
            if lines:
                return "**Your Leave Balance:**\n" + "\n".join(lines)
            else:
                return "No leave balance records found for your account."
                
        except Exception as e:
            logger.error(f"Database error: {str(e)}")
            return f"**{question}**\n\nSorry, I encountered a database error while retrieving your leave balance."
        finally:
            db.close()