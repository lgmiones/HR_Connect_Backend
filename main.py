"""
HRConnect API - Main Application
"""

from fastapi import FastAPI
from app.api.routes import auth, chatbot

app = FastAPI(
    title="HRConnect API",
    description="Human Resource Information System with Agentic RAG",
    version="1.0.0",
    swagger_ui_parameters={
        "persistAuthorization": True  # Keep authorization after page refresh
    }
)

# Include routers
app.include_router(auth.router)
app.include_router(chatbot.router)


@app.get("/")
def root():
    return {
        "message": "HRConnect API is running",
        "docs": "/docs",
        "version": "1.0.0",
        "features": [
            "JWT Authentication",
            "Agentic RAG Chatbot",
            "HR Policy Search",
            "Employee Data Access"
        ]
    }


@app.get("/health")
def health_check():
    """
    Global health check endpoint for monitoring
    """
    return {
        "status": "healthy",
        "service": "HRConnect API",
        "version": "1.0.0"
    }