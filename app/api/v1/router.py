from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, leave_balances, chatbot

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(leave_balances.router, prefix="/leave-balances", tags=["Leave Balances"])
api_router.include_router(chatbot.router, prefix="/chatbot", tags=["Chatbot"])