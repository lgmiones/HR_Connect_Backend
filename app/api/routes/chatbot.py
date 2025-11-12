"""
Chatbot Routes
Handles HR chatbot queries with Agentic RAG orchestration
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.models.user import User
from app.api.dependencies import get_current_user
from app.services.retriever import query_hr_documents
from app.Agent import hr_agent_graph, AgentState
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/chatbot", tags=["Chatbot"])


class ChatRequest(BaseModel):
    question: str


class ChatResponse(BaseModel):
    answer: str
    query_type: str | None = None
    source: str | None = None
    is_compound: bool = False
    num_questions: int = 1


@router.post("/query", response_model=ChatResponse)
async def chat_query(
    request: ChatRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Query the HR chatbot with Agentic RAG orchestration.
    
    **Requires**: Valid JWT token in Authorization header
    
    **Features**:
    - Routes queries between policy documents and personal employee data
    - Uses LangGraph for intelligent query classification
    - Falls back to basic RAG if agent fails
    
    **Parameters**:
    - **question**: The HR-related question to ask
    
    **Returns**:
    - **answer**: AI-generated response
    - **query_type**: Type of query (policy/personal_data/general)
    - **source**: Source of the answer
    
    **Example**:
```json
    {
        "question": "What is the leave policy?"
    }
```
    """
    try:
        user_id = current_user.user_id
        
        initial_state = AgentState(
            messages=[{"role": "user", "content": request.question}],
            user_id=user_id
        )
        
        logger.info(f"User {current_user.email} (ID: {user_id}) asked: {request.question}")
        result = hr_agent_graph.invoke(initial_state)
        
        final_message = result["messages"][-1]
        answer = final_message["content"] if isinstance(final_message, dict) else final_message.content
        
        # Extract metadata from result
        is_multiple = result.get("is_multiple", False)
        sub_queries = result.get("sub_queries", [])
        query_type = result.get("query_type", "general")  # ← Now this will work!
        
        # Map query_type to user-friendly source
        if query_type == "compound":
            source = f"multiple_sources ({len(sub_queries)} questions)"
        elif query_type == "policy":
            source = "policy_documents"
        elif query_type == "personal_data":
            source = "personal_database"
        elif query_type == "general":
            source = "general_knowledge"
        else:
            source = "unknown"
        
        logger.info(f"Query resolved - type: {query_type}, source: {source}")
        
        return ChatResponse(
            answer=answer,
            query_type=query_type,
            source=source,
            is_compound=is_multiple,
            num_questions=len(sub_queries) if sub_queries else 1
        )
        
    except Exception as e:
        logger.error(f"Agentic chatbot error for user {current_user.email}: {str(e)}")
        
        # Fallback to basic RAG
        try:
            logger.info("Falling back to basic RAG system")
            rag_result = query_hr_documents(request.question)
            return ChatResponse(
                answer=rag_result["answer"],
                query_type="policy",
                source="fallback_rag",
                is_compound=False,
                num_questions=1
            )
        except Exception as rag_error:
            logger.error(f"Fallback RAG also failed: {str(rag_error)}")
            raise HTTPException(
                status_code=500,
                detail="Chatbot service temporarily unavailable. Please try again later."
            )


@router.get("/history")
async def get_chat_history(
    current_user: User = Depends(get_current_user)
):
    """
    Get user's chat history (placeholder for future implementation)
    
    **Requires**: Valid JWT token in Authorization header
    
    **Returns**: User's conversation history
    """
    return {
        "message": "Chat history feature coming soon",
        "user": current_user.email,
        "user_id": current_user.user_id
    }


@router.get("/health")
async def chatbot_health_check(
    current_user: User = Depends(get_current_user)
):
    """
    Health check for chatbot service
    
    **Requires**: Valid JWT token in Authorization header
    """
    try:
        # Test if agent graph is available
        _ = hr_agent_graph
        return {
            "status": "healthy",
            "service": "Agentic Chatbot",
            "user": current_user.email
        }
    except Exception as e:
        logger.error(f"Chatbot health check failed: {str(e)}")
        return {
            "status": "degraded",
            "service": "Agentic Chatbot",
            "message": "Agent graph not available, using fallback RAG",
            "user": current_user.email
        }