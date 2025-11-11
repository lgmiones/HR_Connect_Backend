"""
HRConnect API - Main Application
"""

from fastapi import FastAPI
from app.api.routes import auth
from pydantic import BaseModel
from app.services.retriever import query_hr_documents

app = FastAPI(
    title="HRConnect API",
    description="Human Resource Information System",
    version="1.0.0"
)

# Include authentication routes
app.include_router(auth.router)

class ChatRequest(BaseModel):
    question: str

@app.post("/chatbot")
async def chatbot_query(request: ChatRequest):
    """
    Example:
    POST /chatbot
    {
        "question": "What is the leave policy?"
    }
    """
    response = query_hr_documents(request.question)
    return response    

@app.get("/")
def root():
    return {
        "message": "HRConnect API is running",
        "docs": "/docs"
    }
