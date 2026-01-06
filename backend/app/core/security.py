from datetime import datetime, timedelta
from typing import Optional

from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = "HS256"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


# JWT Token handling
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    # Create comprehensive JWT payload following shared types
    payload = {
        "sub": to_encode["sub"],           # User email (primary identifier)
        "user_id": str(to_encode.get("user_id", "")),  # User ID as string
        "email": to_encode["sub"],         # User email (duplicate for clarity)
        "role": to_encode["role"],         # User role
        "type": "access",                  # Token type
        "exp": expire                      # Expiration
    }
    
    encoded_jwt = jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES
        )
    
    # Create comprehensive JWT payload following shared types
    payload = {
        "sub": to_encode["sub"],           # User email (primary identifier)
        "user_id": str(to_encode.get("user_id", "")),  # User ID as string
        "email": to_encode["sub"],         # User email (duplicate for clarity) 
        "role": to_encode["role"],         # User role
        "type": "refresh",                 # Token type
        "exp": expire                      # Expiration
    }
    
    encoded_jwt = jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
