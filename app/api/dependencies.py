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
    # Generate unique request ID
    request_id = str(uuid.uuid4())[:8]
    
    token = credentials.credentials
    
    print(f"\n{'='*80}", file=sys.stderr)
    print(f"🔍 [{request_id}] NEW REQUEST TO /auth/me", file=sys.stderr)
    print(f"   Token (first 50 chars): {token[:50]}...", file=sys.stderr)
    
    payload = verify_token(token)
    if not payload:
        print(f"❌ [{request_id}] Token verification failed!", file=sys.stderr)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    token_email = payload.get("email")
    token_user_id = payload.get("user_id")
    token_jti = payload.get("jti")
    
    print(f"🔍 [{request_id}] TOKEN DECODED:", file=sys.stderr)
    print(f"   - email: {token_email}", file=sys.stderr)
    print(f"   - user_id: {token_user_id}", file=sys.stderr)
    print(f"   - jti: {token_jti}", file=sys.stderr)
    
    if not token_jti:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token format",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    print(f"🔍 [{request_id}] QUERYING DATABASE:", file=sys.stderr)
    print(f"   - Looking for email: {token_email}", file=sys.stderr)
    
    user_service = AuthService(db)
    user = user_service.user_repo.get_by_email(token_email)
    
    print(f"🔍 [{request_id}] DATABASE RETURNED:", file=sys.stderr)
    print(f"   - user_id: {user.user_id if user else 'None'}", file=sys.stderr)
    print(f"   - email: {user.email if user else 'None'}", file=sys.stderr)
    print(f"   - current_token_jti: {user.current_token_jti if user else 'None'}", file=sys.stderr)
    
    if not user:
        print(f"❌ [{request_id}] User not found!", file=sys.stderr)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    print(f"🔍 [{request_id}] SESSION VALIDATION:", file=sys.stderr)
    print(f"   - Token JTI: {token_jti}", file=sys.stderr)
    print(f"   - DB JTI: {user.current_token_jti}", file=sys.stderr)
    print(f"   - Match: {user.current_token_jti == token_jti}", file=sys.stderr)
    
    if user.current_token_jti != token_jti:
        print(f"❌ [{request_id}] JTI MISMATCH!", file=sys.stderr)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session has been invalidated. Please login again.",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    print(f"✅ [{request_id}] RETURNING USER:", file=sys.stderr)
    print(f"   - user_id: {user.user_id}", file=sys.stderr)
    print(f"   - email: {user.email}", file=sys.stderr)
    print(f"{'='*80}\n", file=sys.stderr)
    
    return user