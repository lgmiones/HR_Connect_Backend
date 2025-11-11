import os
import logging
from dotenv import load_dotenv
from typing import Annotated, Literal
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain.chat_models import init_chat_model
from pydantic import BaseModel, Field
from sqlalchemy import text

from app.db.session import get_db
from app.services.retriever import query_hr_documents, get_vectorstore

load_dotenv()
logger = logging.getLogger(__name__)

llm = init_chat_model(
    "llama-3.1-8b-instant",
    model_provider="groq"
)

class QueryClassifier(BaseModel):
    query_type: Literal["policy", "personal_data", "general"] = Field(
        ...,
        description="Classify the query type: 'policy' for company policies (use vector DB), 'personal_data' for user-specific data (use SQL DB), 'general' for other questions"
    )

# agent state
class AgentState(BaseModel):
    messages: Annotated[list, add_messages]
    query_type: str | None = None
    next: str | None = None
    user_id: int | None = None

# Nodes
def classify_query(state: AgentState):
    """Classify the user query to determine which database to use"""
    last_message = state.messages[-1]
    
    # Use structured output for classification
    classifier_llm = llm.with_structured_output(QueryClassifier)
    
    result = classifier_llm.invoke([
        {
            "role": "system", 
            "content": """Classify the user's HR-related question into one of these categories:
            
            - 'policy': Questions about company policies, guidelines, rules, procedures, HR manuals, policy documents
              Examples: "What is the leave policy?", "What are the overtime rules?", "Tell me about holiday pay", 
                        "What's the company policy on remote work?", "Explain the attendance guidelines"
            
            - 'personal_data': Questions requiring personal data from SQL database, user-specific information
              Examples: "How many leaves do I have?", "Show my attendance", "My leave status", 
                        "How many vacation days are left?", "What's my attendance this week?"
            
            - 'general': Other HR-related questions that don't require specific policies or personal data
              Examples: "What is HRConnect?", "How can you help me?", "What features are available?"
            
            Be strict about classification. Only use 'personal_data' if it clearly requires database lookup of user-specific information.
            Only use 'policy' if it's about company rules, policies, or guidelines.
            """
        },
        {"role": "user", "content": last_message.content}
    ])
    
    logger.info(f"Query classified as: {result.query_type}")
    return {"query_type": result.query_type}

def router(state: AgentState):
    query_type = state.query_type or "general"

    if query_type == "policy":
        return {"next": "vector_db_query"}
    elif query_type == "personal_data":
        return {"next": "sql_db_query"}
    else:
        return {"next": "general_assistant"}

# use RAG system for policy queries    
def vector_db_query(state: AgentState):
    last_message = state.messages[-1]
    question = last_message.content

    logger.info("Using existing RAG system for policy query")
    rag_result = query_hr_documents(question)
    
    return {
        "messages": [{"role": "assistant", "content": rag_result["answer"]}]
    }

# sql query for personal data
def sql_db_query(state: AgentState):
    """Query SQL database for personal data - FOCUSED ON LEAVE BALANCE ONLY"""
    last_message = state.messages[-1]
    question = last_message.content.lower()
    
    if not state.user_id:
        return {
            "messages": [{"role": "assistant", "content": "I need you to log in to access your personal data. Please authenticate first."}]
        }
    
    db = next(get_db())
    
    try:
        # Leave balance queries - FOCUS ONLY ON THIS
        if any(term in question for term in ['leave', 'vacation', 'sick', 'balance', 'remaining', 'how many']):
            result = db.execute(
                text("SELECT total_leaves, used_leaves FROM leave_balance WHERE user_id = :user_id"),
                {"user_id": state.user_id}
            ).fetchone()
            
            if result:
                total_leaves = result[0]
                used_leaves = int(result[1]) if result[1] else 0
                remaining_leaves = total_leaves - used_leaves
                
                response_content = f"""Your Leave Balance:
• Total leaves allocated: {total_leaves}
• Leaves used: {used_leaves}
• Leaves remaining: {remaining_leaves}

You have {remaining_leaves} leaves available for use."""
            else:
                response_content = "No leave balance record found for your account. Please contact HR to set up your leave balance."
        
        # Remove attendance and leave status queries for now since we're focusing on leave_balance
        else:
            response_content = "I can help you check your leave balance. Try asking: 'How many leaves do I have?' or 'What's my leave balance?'"
            
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        response_content = "Sorry, I encountered an error accessing your leave balance data. Please try again later."
    finally:
        db.close()
    
    return {
        "messages": [{"role": "assistant", "content": response_content}]
    }

# general assistant
def general_assistant(state: AgentState):
    last_message = state.messages[-1]
    
    general_responses = {
        "what can you do": """I'm your HRConnect assistant! I can help you with:

🔍 **Policy Information**: Answer questions about company policies, guidelines, and procedures
📊 **Personal Data**: Check your leave balances, attendance records, and leave request status
❓ **General Help**: Answer HR-related questions

Try asking me:
- "What's the leave policy?" (I'll check our policy documents)
- "How many vacation days do I have?" (I'll check your personal data)
- "Show my attendance this week" (I'll get your records)""",

        "hrconnect": """HRConnect is our Human Resource Information System that helps streamline HR processes including:

• Attendance tracking and time modification
• Leave management (file, view, and cancel requests)  
• Access to company policies and procedures
• Employee self-service portal

I'm the chatbot assistant integrated with HRConnect to help you access information quickly!""",

        "features": """Available HRConnect Features:

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
    }
    
    question_lower = last_message.content.lower()
    response_content = "I'm here to help with HR-related questions! "
    
    # Check for matching general questions
    for key, response in general_responses.items():
        if key in question_lower:
            response_content = response
            break
    else:
        # Default general response
        response_content += "You can ask me about company policies or your personal HR data. What would you like to know?"
    
    return {
        "messages": [{"role": "assistant", "content": response_content}]
    }

# Build the graph
def create_agentic_orchestrator():
    graph_builder = StateGraph(AgentState)

    # Add nodes
    graph_builder.add_node("classifier", classify_query)
    graph_builder.add_node("router", router)
    graph_builder.add_node("vector_db_query", vector_db_query)
    graph_builder.add_node("sql_db_query", sql_db_query)      
    graph_builder.add_node("general_assistant", general_assistant)

    # Build the workflow: START → classifier → router → appropriate database → END
    graph_builder.add_edge(START, "classifier")
    graph_builder.add_edge("classifier", "router")
    
    # Conditional routing from router
    graph_builder.add_conditional_edges(
        "router",
        lambda state: state.next,
        {
            "vector_db_query": "vector_db_query",  
            "sql_db_query": "sql_db_query",       
            "general_assistant": "general_assistant"
        }
    )
    
    graph_builder.add_edge("vector_db_query", END)
    graph_builder.add_edge("sql_db_query", END)
    graph_builder.add_edge("general_assistant", END)

    return graph_builder.compile()

hr_agent_graph = create_agentic_orchestrator()