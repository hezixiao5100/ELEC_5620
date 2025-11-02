"""
User Schemas
"""
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from app.models.user import UserRole

class UserBase(BaseModel):
    """Base user schema"""
    username: str
    email: EmailStr
    role: UserRole = UserRole.INVESTOR
    alert_threshold: float = -5.0

class UserCreate(UserBase):
    """Schema for creating a new user"""
    password: str

class UserUpdate(BaseModel):
    """Schema for updating user information"""
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    alert_threshold: Optional[float] = None

class UserInDB(UserBase):
    """Schema for user data in database"""
    id: int
    is_active: str
    created_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class User(UserBase):
    """Schema for user response (API response)"""
    id: int
    is_active: bool  # Converted from "Y"/"N" string to boolean
    created_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    """Schema for user login"""
    username: str
    password: str




