from fastapi import FastAPI, Depends, HTTPException
from app.Agent.agentic_chatbot import AgentState, hr_agent_graph
from app.api.routes import auth
from pydantic import BaseModel
from app.services.retriever import query_hr_documents
import logging
from app.api.routes.auth import get_me
from app.api.dependencies import get_current_user


logger = logging.getLogger(__name__)

app = FastAPI(
    title="HRConnect API",
    description="Human Resource Information System",
    version="1.0.0"
)

# routes
app.include_router(auth.router)

class ChatRequest(BaseModel):
    question: str

class ChatResponse(BaseModel):
    answer: str
    query_type: str | None = None
    source: str | None = None

@app.post("/chatbot", response_model=ChatResponse)
async def chatbot_query(
    request: ChatRequest,
    current_user = Depends(get_current_user)  # This requires authentication
):
    """
    Agentic chatbot with LangGraph orchestration
    """
    try:
        user_id = current_user.user_id  # This will always have a value since auth is required
        
        # Prepare initial state
        initial_state = AgentState(
            messages=[{"role": "user", "content": request.question}],
            user_id=user_id
        )
        
        # Invoke the LangGraph orchestrator
        result = hr_agent_graph.invoke(initial_state)
        
        # Extract the final response
        final_message = result["messages"][-1]
        answer = final_message["content"] if isinstance(final_message, dict) else final_message.content
        
        # Determine source for response
        query_type = result.get("query_type")
        source = "policy_documents" if query_type == "policy" else "personal_database" if query_type == "personal_data" else "general_knowledge"
        
        return ChatResponse(
            answer=answer,
            query_type=query_type,
            source=source
        )
        
    except Exception as e:
        logger.error(f"Chatbot error: {str(e)}")
        # Fallback to your existing RAG system
        try:
            rag_result = query_hr_documents(request.question)
            return ChatResponse(
                answer=rag_result["answer"],
                query_type="policy",
                source="fallback_rag"
            )
        except Exception as rag_error:
            logger.error(f"Fallback RAG also failed: {str(rag_error)}")
            raise HTTPException(status_code=500, detail="Chatbot service temporarily unavailable")
 

@app.get("/")
def root():
    return {
        "message": "HRConnect API is running",
        "docs": "/docs"
    }
