# """
# HRConnect API - Main Application
# """

# from fastapi import FastAPI
# from app.api.routes import auth
# from pydantic import BaseModel
# from app.services.retriever import query_hr_documents

# app = FastAPI(
#     title="HRConnect API",
#     description="Human Resource Information System",
#     version="1.0.0"
# )

# # Include authentication routes
# app.include_router(auth.router)

# class ChatRequest(BaseModel):
#     question: str

# @app.post("/chatbot")
# async def chatbot_query(request: ChatRequest):
#     """
#     Example:
#     POST /chatbot
#     {
#         "question": "What is the leave policy?"
#     }
#     """
#     response = query_hr_documents(request.question)
#     return response    

# @app.get("/")
# def root():
#     return {
#         "message": "HRConnect API is running",
#         "docs": "/docs"
#     }


"""
HRConnect API - Main Application
"""

from fastapi import FastAPI, Depends
from app.api.routes import auth
from pydantic import BaseModel
from app.services.retriever import query_hr_documents
from app.api.dependencies import get_current_user
from app.models.user import User

app = FastAPI(
    title="HRConnect API",
    description="Human Resource Information System",
    version="1.0.0",
    swagger_ui_parameters={
        "persistAuthorization": True  # Keep authorization after page refresh
    }
)

# Include authentication routes
app.include_router(auth.router)

class ChatRequest(BaseModel):
    question: str

@app.post("/chatbot")
async def chatbot_query(
    request: ChatRequest,
    current_user: User = Depends(get_current_user)  # ← Authentication required
):
    """
    Query the HR chatbot with authenticated access only.
    
    Requires: Valid JWT token in Authorization header
    
    Example:
    POST /chatbot
    Headers: Authorization: Bearer <your_jwt_token>
    Body:
    {
        "question": "What is the leave policy?"
    }
    """
    response = query_hr_documents(request.question)
    
    # Optional: You can also track which user asked what question
    # logger.info(f"User {current_user.email} asked: {request.question}")
    
    return response

@app.get("/")
def root():
    return {
        "message": "HRConnect API is running",
        "docs": "/docs"
    }