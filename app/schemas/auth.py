"""
Authentication Schemas
Pydantic models for authentication requests and responses
"""
from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    """User role enumeration"""
    INVESTOR = "INVESTOR"
    ADVISOR = "ADVISOR"
    ADMIN = "ADMIN"

class UserCreate(BaseModel):
    """User registration schema"""
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    email: EmailStr = Field(..., description="Email address")
    password: str = Field(..., min_length=6, max_length=100, description="Password")
    role: UserRole = Field(default=UserRole.INVESTOR, description="User role")
    alert_threshold: Optional[float] = Field(default=10.0, ge=0, le=100, description="Alert threshold percentage")

    class Config:
        json_schema_extra = {
            "example": {
                "username": "john_doe",
                "email": "john@example.com",
                "password": "securepassword123",
                "role": "INVESTOR",
                "alert_threshold": 15.0
            }
        }

class UserLogin(BaseModel):
    """User login schema"""
    username: str = Field(..., description="Username or email")
    password: str = Field(..., description="Password")

    class Config:
        json_schema_extra = {
            "example": {
                "username": "john_doe",
                "password": "securepassword123"
            }
        }

class UserResponse(BaseModel):
    """User response schema"""
    id: int
    username: str
    email: str
    role: UserRole
    alert_threshold: Optional[float]
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime]

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "username": "john_doe",
                "email": "john@example.com",
                "role": "INVESTOR",
                "alert_threshold": 15.0,
                "is_active": True,
                "created_at": "2025-10-23T02:00:00Z",
                "last_login": "2025-10-23T02:30:00Z"
            }
        }

class Token(BaseModel):
    """JWT token response schema"""
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 1800
            }
        }

class TokenData(BaseModel):
    """Token payload data"""
    sub: Optional[str] = None
    username: Optional[str] = None
    role: Optional[str] = None
    exp: Optional[datetime] = None
    type: Optional[str] = None

class PasswordChange(BaseModel):
    """Password change schema"""
    old_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=6, max_length=100, description="New password")

    class Config:
        json_schema_extra = {
            "example": {
                "old_password": "oldpassword123",
                "new_password": "newpassword456"
            }
        }

class UserUpdate(BaseModel):
    """User profile update schema"""
    email: Optional[EmailStr] = Field(None, description="New email address")
    alert_threshold: Optional[float] = Field(None, ge=0, le=100, description="New alert threshold")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "newemail@example.com",
                "alert_threshold": 20.0
            }
        }

class RefreshTokenRequest(BaseModel):
    """Refresh token request schema"""
    refresh_token: str = Field(..., description="Valid refresh token")

    class Config:
        json_schema_extra = {
            "example": {
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }