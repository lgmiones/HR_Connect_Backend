"""
HRConnect API - Main Application
"""

from fastapi import FastAPI
from app.api.routes import auth, chatbot
from app.api.routes import emergency_leave, vacation_leave, sick_leave
import logging
import sys

# ✅ Configure logging BEFORE anything else
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(name)s:%(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="HRConnect API",
    description="Human Resource Information System with Agentic RAG",
    version="1.0.0",
    swagger_ui_parameters={
        "persistAuthorization": True
    }
)

# Include routers
app.include_router(auth.router)
app.include_router(chatbot.router)
app.include_router(emergency_leave.router)
app.include_router(vacation_leave.router)
app.include_router(sick_leave.router)


@app.on_event("startup")
async def startup_event():
    """Warm up models on server startup"""
    logger.info("🚀 Starting server warmup...")
    
    try:
        # Preload vectorstore and embeddings
        from app.services.retriever import get_vectorstore
        logger.info("Loading vectorstore...")
        get_vectorstore()
        logger.info("✅ Vectorstore preloaded")
        
        # Preload LLM
        from app.Agent.utils.llm_config import get_llm
        logger.info("Loading LLM...")
        get_llm()
        logger.info("✅ LLM preloaded")
        
        logger.info("🎉 Server warmup complete!")
    except Exception as e:
        logger.error(f"❌ Warmup failed: {e}", exc_info=True)


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
    """Global health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "service": "HRConnect API",
        "version": "1.0.0"
    }