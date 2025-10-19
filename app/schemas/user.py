"""
User Schemas
"""
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# TODO: Define UserBase schema
# class UserBase(BaseModel):
#     username: str
#     email: EmailStr

# TODO: Define UserCreate schema (for registration)
# class UserCreate(UserBase):
#     password: str
#     role: str = "investor"

# TODO: Define UserUpdate schema
# class UserUpdate(BaseModel):
#     email: Optional[EmailStr] = None
#     alert_threshold: Optional[float] = None

# TODO: Define UserResponse schema (what API returns)
# class UserResponse(UserBase):
#     id: int
#     role: str
#     alert_threshold: float
#     created_at: datetime
#     last_login: Optional[datetime]
#     
#     class Config:
#         from_attributes = True


