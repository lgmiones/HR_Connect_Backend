"""
Response templates for general queries
Fallback responses when LLM is not available
"""


def get_help_template(question: str) -> str:
    """Template response for help queries"""
    return f"""**{question}**

I'm your HRConnect assistant! I can help you with:

🔍 **Policy Information**: Answer questions about company policies, guidelines, and procedures
📊 **Personal Data**: Check your leave balances, attendance records, and leave request status
❓ **General Help**: Answer HR-related questions

Try asking me:
- "What's the leave policy?" (I'll check our policy documents)
- "How many vacation days do I have?" (I'll check your personal data)
- "What leaves did I take last month?" (I'll show your history)"""


def get_about_template(question: str) -> str:
    """Template response for about queries"""
    return f"""**{question}**

HRConnect is our Human Resource Information System that helps streamline HR processes including:

- Attendance tracking and time modification
- Leave management (file, view, and cancel requests)  
- Access to company policies and procedures
- Employee self-service portal

I'm the chatbot assistant integrated with HRConnect to help you access information quickly!"""


def get_features_template(question: str) -> str:
    """Template response for features queries"""
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


def get_greeting_template(question: str) -> str:
    """Template response for greetings"""
    return f"""Hello! I'm your HRConnect assistant. 

I can help you with:
- Company policies and procedures
- Your leave balance and history
- HR-related questions

What would you like to know?"""


def get_default_template(question: str) -> str:
    """Default template for unrecognized queries"""
    return f"**{question}**\n\nI'm here to help with HR policies and your personal HR data. What would you like to know?"