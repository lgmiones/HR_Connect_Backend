"""
HRConnect API - Main Application
"""

from fastapi import FastAPI
from app.api.routes import auth

app = FastAPI(
    title="HRConnect API",
    description="Human Resource Information System",
    version="1.0.0"
)

# Include authentication routes
app.include_router(auth.router)


@app.get("/")
def root():
    return {
        "message": "HRConnect API is running",
        "docs": "/docs"
    }