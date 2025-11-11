
from fastapi import APIRouter, Depends, status, Header, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.schemas.auth_schemas import UserRegister, UserLogin, Token, UserResponse
from app.services.auth_service import AuthService
from app.api.dependencies import get_current_user, security
from app.core.token_blacklist import add_to_blacklist

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    """Dependency to get AuthService instance"""
    return AuthService(db)


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(
    user_data: UserRegister,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Register a new user
    
    - **email**: User's email (must be unique)
    - **password**: User's password
    """
    new_user = auth_service.register_user(user_data)
    return new_user


@router.post("/login", response_model=Token)
def login(
    credentials: UserLogin,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Login with email and password
    
    Returns JWT access token
    """
    token = auth_service.authenticate_user(credentials)
    return token


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """
    Get current authenticated user's profile
    
    Requires valid JWT token in Authorization header
    """
    return current_user

@router.post("/logout", status_code=status.HTTP_200_OK)
def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security)  
):
    """
    Logout the current user by revoking their token
    
    Requires valid JWT token in Authorization header
    """
    token = credentials.credentials  # Extract the actual token
    add_to_blacklist(token)
    
    return {"message": "Successfully logged out"}