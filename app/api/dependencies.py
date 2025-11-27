# """
# Authentication dependencies
# """
# from fastapi import Depends, HTTPException, status, Security
# from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
# from sqlalchemy.orm import Session
# from app.db.session import get_db
# from app.models.user import User
# from app.services.auth_service import AuthService
# from app.core.auth_utils import verify_token

# # Define the security scheme
# security = HTTPBearer()


# def get_current_user(
#     credentials: HTTPAuthorizationCredentials = Security(security),
#     db: Session = Depends(get_db)
# ) -> User:
#     """
#     Get current authenticated user from JWT token
#     Also verifies this token is the current active session
#     """
#     token = credentials.credentials  # Extract the token
    
#     payload = verify_token(token)
#     if not payload:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid or expired token",
#             headers={"WWW-Authenticate": "Bearer"}
#         )
    
#     # Extract JTI from token payload
#     token_jti = payload.get("jti")
#     if not token_jti:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid token format",
#             headers={"WWW-Authenticate": "Bearer"}
#         )
    
#     user_service = AuthService(db)
#     user = user_service.user_repo.get_by_email(payload.get("email"))
    
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="User not found",
#             headers={"WWW-Authenticate": "Bearer"}
#         )
    
#     # CRITICAL CHECK: Verify this token is the current active session
#     if user.current_token_jti != token_jti:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Session has been invalidated. Please login again.",
#             headers={"WWW-Authenticate": "Bearer"}
#         )
    
#     return user



"""
Authentication dependencies
"""
import sys
import uuid  # ADD THIS
from fastapi import Depends, HTTPException, status, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User
from app.services.auth_service import AuthService
from app.core.auth_utils import verify_token

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current authenticated user from JWT token
    Also verifies this token is the current active session
    """
    token = credentials.credentials
    
    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    token_jti = payload.get("jti")
    token_user_id = payload.get("user_id")  # ✅ Get user_id instead of email
    token_email = payload.get("email")  # Keep for validation
    
    if not token_jti or not token_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token format",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # ✅ CRITICAL: Expire all before querying
    db.expire_all()
    
    user_service = AuthService(db)
    
    # ✅ Query by user_id (primary key) instead of email
    user = user_service.user_repo.get_by_id(token_user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # ✅ CRITICAL: Verify the email matches as extra security
    if user.email != token_email:
        print(f"🚨 EMAIL MISMATCH! Token: {token_email}, DB: {user.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User data mismatch - session corrupted",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # ✅ CRITICAL: Verify JTI matches
    if user.current_token_jti != token_jti:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session has been invalidated. Please login again.",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    print(f"✅ VALIDATED: {user.email} (ID: {user.user_id})")
    
    return user