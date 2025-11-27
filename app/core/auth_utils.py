"""
Simple Authentication utilities for HRConnect
"""

import uuid
from datetime import datetime, timezone, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings
from app.core.token_blacklist import is_token_revoked

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash password"""
    return pwd_context.hash(password)


# def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> tuple[str, str]:
#     """
#     Create JWT token with unique JTI (JWT ID)
    
#     Returns:
#         tuple: (token, jti) - The encoded JWT token and its unique identifier
#     """
#     to_encode = data.copy()
    
#     # Generate unique token ID
#     jti = str(uuid.uuid4())
    
#     if expires_delta:
#         expire = datetime.utcnow() + expires_delta
#     else:
#         expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
#     to_encode.update({
#         "exp": expire,
#         "jti": jti
#     })
    
#     encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
#     return encoded_jwt, jti

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> tuple[str, str]:
    """
    Create JWT token with unique JTI (JWT ID)
    Returns:
        tuple: (token, jti) - The encoded JWT token and its unique identifier
    """
    to_encode = data.copy()
    # Generate unique token ID
    jti = str(uuid.uuid4())
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta  # Changed this line
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)  # Changed this line
    to_encode.update({
        "exp": expire,
        "jti": jti
    })
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt, jti

def verify_token(token: str) -> dict:
    """Verify JWT token and check if it is revoked"""
    if is_token_revoked(token):
        return None
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None