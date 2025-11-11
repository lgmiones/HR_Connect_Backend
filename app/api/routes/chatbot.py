"""
Chatbot Routes
Handles HR chatbot queries
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.models.user import User
from app.api.dependencies import get_current_user
from app.services.retriever import query_hr_documents

router = APIRouter(prefix="/api/v1/chatbot", tags=["Chatbot"])


class ChatRequest(BaseModel):
    question: str


class ChatResponse(BaseModel):
    answer: str
    # sources: list = []  # Optional: uncomment when you fix source attribution


@router.post("/query", response_model=ChatResponse)
async def chat_query(
    request: ChatRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Query the HR chatbot with authenticated access.
    
    **Requires**: Valid JWT token in Authorization header
    
    **Parameters**:
    - **question**: The HR-related question to ask
    
    **Returns**:
    - **answer**: AI-generated response based on HR documents
    
    **Example**:
```json
    {
        "question": "What is the leave policy?"
    }
```
    """
    response = query_hr_documents(request.question)
    return response


# Optional: Add conversation history endpoint
@router.get("/history")
async def get_chat_history(
    current_user: User = Depends(get_current_user)
):
    """
    Get user's chat history (placeholder for future implementation)
    """
    return {
        "message": "Chat history feature coming soon",
        "user": current_user.email
    }