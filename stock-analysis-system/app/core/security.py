"""
Security Functions (JWT, Password Hashing)
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext

# TODO: Import config
# from app.config import settings

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify password against hash
    
    Args:
        plain_password: Plain text password
        hashed_password: Hashed password
        
    Returns:
        True if password matches
    """
    # TODO: Verify password using pwd_context
    # return pwd_context.verify(plain_password, hashed_password)
    pass

def get_password_hash(password: str) -> str:
    """
    Hash password
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password
    """
    # TODO: Hash password using pwd_context
    # return pwd_context.hash(password)
    pass

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token
    
    Args:
        data: Data to encode in token
        expires_delta: Token expiration time
        
    Returns:
        JWT token string
    """
    # TODO: Copy data to encode
    # TODO: Add expiration time
    # TODO: Encode JWT token
    # TODO: Return token
    # to_encode = data.copy()
    # if expires_delta:
    #     expire = datetime.utcnow() + expires_delta
    # else:
    #     expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    # to_encode.update({"exp": expire})
    # encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    # return encoded_jwt
    pass

def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decode JWT access token
    
    Args:
        token: JWT token string
        
    Returns:
        Decoded token data or None
    """
    # TODO: Decode JWT token
    # TODO: Return payload or None if invalid
    # try:
    #     payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    #     return payload
    # except JWTError:
    #     return None
    pass







