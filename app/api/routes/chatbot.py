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
#for CHATBOT HISTORY
from sqlalchemy.orm import Session
from app.db.session import get_db
from typing import Optional
from app.services.chatbot_service import ChatbotService

import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/chatbot", tags=["Chatbot"])


class ChatRequest(BaseModel):
    question: str
    conversation_id: Optional[int] = None # Optional: link to existing conversation

class ChatResponse(BaseModel):
    answer: str
    query_type: str | None = None
    source: str | None = None
    is_compound: bool = False
    num_questions: int = 1
    conversation_id: int
    message_id: int


@router.post("/query", response_model=ChatResponse)
async def chat_query(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
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

        # Create or get conversation
        if request.conversation_id:
            # Verify user owns this conversation
            conversation = ChatbotService.get_conversation(
                db, 
                request.conversation_id, 
                user_id
            )
            if not conversation:
                raise HTTPException(
                    status_code=404,
                    detail="Conversation not found"
                )
        else:
            # Create new conversation
            conversation = ChatbotService.create_conversation(
                db,
                user_id,
                title=f"Query: {request.question[:50]}..."
            )
        
        # Store user question
        user_message = ChatbotService.add_message(
            db,
            conversation.conversation_id,
            request.question
        )
        
        # Process with agent
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

        # Store bot response
        bot_message = ChatbotService.add_message(
            db,
            conversation.conversation_id,
            answer
        )
        
        logger.info(f"Query resolved - type: {query_type}, source: {source}")
        
        return ChatResponse(
            answer=answer,
            query_type=query_type,
            source=source,
            is_compound=is_multiple,
            num_questions=len(sub_queries) if sub_queries else 1,
            conversation_id=conversation.conversation_id,
            message_id=bot_message.message_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Agentic chatbot error for user {current_user.email}: {str(e)}")
        
        # Fallback to basic RAG
        try:
            logger.info("Falling back to basic RAG system")
            rag_result = query_hr_documents(request.question)

            # Store fallback response
            bot_message = ChatbotService.add_message(
                db,
                conversation.conversation_id,
                rag_result["answer"]
            )

            return ChatResponse(
                answer=rag_result["answer"],
                query_type="policy",
                source="fallback_rag",
                is_compound=False,
                num_questions=1,
                conversation_id=conversation.conversation_id,
                message_id=bot_message.message_id
            )
        except Exception as rag_error:
            logger.error(f"Fallback RAG also failed: {str(rag_error)}")
            raise HTTPException(
                status_code=500,
                detail="Chatbot service temporarily unavailable. Please try again later."
            )


@router.get("/history")
async def get_chat_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's chat history - all conversations
    
    **Requires**: Valid JWT token in Authorization header
    
    **Returns**: User's conversation history
    """
    try:
        conversations = ChatbotService.get_user_conversations(
            db,
            current_user.user_id
        )
        return {
            "user": current_user.email,
            "user_id": current_user.user_id,
            "conversations": conversations,
            "total_conversations": len(conversations)
        }
    except Exception as e:
        logger.error(f"Error retrieving chat history for user {current_user.email}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve chat history"
        )


@router.get("/history/{conversation_id}")
async def get_conversation_detail(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific conversation with all messages
    
    **Requires**: Valid JWT token in Authorization header
    
    **Parameters**:
    - **conversation_id**: ID of the conversation to retrieve
    
    **Returns**: Conversation details with all messages
    """
    try:
        conversation = ChatbotService.get_conversation(
            db,
            conversation_id,
            current_user.user_id
        )
        
        if not conversation:
            raise HTTPException(
                status_code=404,
                detail="Conversation not found"
            )
        
        messages = ChatbotService.get_conversation_messages(
            db,
            conversation_id
        )
        
        return {
            "conversation_id": conversation.conversation_id,
            "user_id": conversation.user_id,
            "title": conversation.title,
            "created_at": conversation.created_at,
            "updated_at": conversation.updated_at,
            "messages": messages,
            "total_messages": len(messages)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving conversation {conversation_id} for user {current_user.email}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve conversation"
        )


@router.delete("/history/{conversation_id}")
async def delete_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a conversation and all its messages
    
    **Requires**: Valid JWT token in Authorization header
    
    **Parameters**:
    - **conversation_id**: ID of the conversation to delete
    """
    try:
        success = ChatbotService.delete_conversation(
            db,
            conversation_id,
            current_user.user_id
        )
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail="Conversation not found"
            )
        
        logger.info(f"User {current_user.email} deleted conversation {conversation_id}")
        return {"message": "Conversation deleted successfully", "conversation_id": conversation_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting conversation {conversation_id} for user {current_user.email}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to delete conversation"
        )



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