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
        """Query database for leave balances based on the question"""
        db = next(get_db())
        question_lower = question.lower()
        lines = []

        try:
            # ✅ Always fetch all leave types
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

            # Then filter based on question
            if "vacation" in question_lower and vacation_result:
                remaining = vacation_result[0] - (vacation_result[1] or 0)
                lines.append(f"🏖️ Vacation: {remaining}/{vacation_result[0]} days")

            elif "sick" in question_lower and sick_result:
                remaining = sick_result[0] - (sick_result[1] or 0)
                lines.append(f"🏥 Sick: {remaining}/{sick_result[0]} days")

            elif "emergency" in question_lower and emergency_result:
                remaining = emergency_result[0] - (emergency_result[1] or 0)
                lines.append(f"🚨 Emergency: {remaining}/{emergency_result[0]} days")
            
            else:
                # ✅ Show all leave types for general queries like "how many leaves"
                if vacation_result:
                    remaining = vacation_result[0] - (vacation_result[1] or 0)
                    lines.append(f"🏖️ Vacation: {remaining}/{vacation_result[0]} days")
                if sick_result:
                    remaining = sick_result[0] - (sick_result[1] or 0)
                    lines.append(f"🏥 Sick: {remaining}/{sick_result[0]} days")
                if emergency_result:
                    remaining = emergency_result[0] - (emergency_result[1] or 0)
                    lines.append(f"🚨 Emergency: {remaining}/{emergency_result[0]} days")
            
            if not lines:
                return f"**{question}**\n\nNo leave records found for your account."
            
            return "**Your Leave Balance:**\n" + "\n".join(lines)

        except Exception as e:
            logger.error(f"Database error fetching leave balance: {e}")
            return f"**{question}**\n\nSorry, I couldn't retrieve your leave balance. Please try again later."
        finally:
            db.close()