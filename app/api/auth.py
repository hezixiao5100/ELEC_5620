"""
Authentication API Routes
FastAPI routes for user authentication and management
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.services.auth_service import AuthService, get_auth_service, get_current_active_user
from app.schemas.auth import (
    UserCreate, UserLogin, UserResponse, Token, 
    PasswordChange, UserUpdate, RefreshTokenRequest
)
from app.models.user import User as UserModel

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Register a new user
    
    Args:
        user_data: User registration information
        auth_service: Authentication service
        
    Returns:
        Created user information
        
    Raises:
        HTTPException: If user already exists
    """
    return auth_service.register_user(user_data)

@router.post("/login", response_model=Token)
async def login_user(
    login_data: UserLogin,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Login user and return JWT tokens
    
    Args:
        login_data: User login credentials
        auth_service: Authentication service
        
    Returns:
        JWT access and refresh tokens
        
    Raises:
        HTTPException: If credentials are invalid
    """
    return auth_service.login_user(login_data)

@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Refresh access token using refresh token
    
    Args:
        refresh_data: Refresh token request
        auth_service: Authentication service
        
    Returns:
        New access token
        
    Raises:
        HTTPException: If refresh token is invalid
    """
    return auth_service.refresh_access_token(refresh_data.refresh_token)

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    Get current user information
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Current user information
    """
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        role=current_user.role,
        alert_threshold=current_user.alert_threshold,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
        last_login=current_user.last_login
    )

@router.put("/me", response_model=UserResponse)
async def update_user_profile(
    update_data: UserUpdate,
    current_user: UserModel = Depends(get_current_active_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Update current user profile
    
    Args:
        update_data: Profile update data
        current_user: Current authenticated user
        auth_service: Authentication service
        
    Returns:
        Updated user information
        
    Raises:
        HTTPException: If update fails
    """
    return auth_service.update_user_profile(current_user.id, update_data.dict(exclude_unset=True))

@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: UserModel = Depends(get_current_active_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Change user password
    
    Args:
        password_data: Password change data
        current_user: Current authenticated user
        auth_service: Authentication service
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If old password is incorrect
    """
    auth_service.change_password(
        current_user.id,
        password_data.old_password,
        password_data.new_password
    )
    return {"message": "Password changed successfully"}

@router.get("/users", response_model=List[UserResponse])
async def get_all_users(
    current_user: UserModel = Depends(get_current_active_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Get all users (Admin only)
    
    Args:
        current_user: Current authenticated user
        auth_service: Authentication service
        
    Returns:
        List of all users
        
    Raises:
        HTTPException: If user is not admin
    """
    if current_user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    users = auth_service.db.query(UserModel).all()
    return [
        UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            role=user.role,
            alert_threshold=user.alert_threshold,
            is_active=user.is_active,
            created_at=user.created_at,
            last_login=user.last_login
        )
        for user in users
    ]

@router.put("/users/{user_id}/activate")
async def toggle_user_status(
    user_id: int,
    current_user: UserModel = Depends(get_current_active_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Toggle user active status (Admin only)
    
    Args:
        user_id: User ID to toggle
        current_user: Current authenticated user
        auth_service: Authentication service
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If user is not admin or user not found
    """
    if current_user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    user = auth_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.is_active = not user.is_active
    auth_service.db.commit()
    
    status_text = "activated" if user.is_active else "deactivated"
    return {"message": f"User {status_text} successfully"}

@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    current_user: UserModel = Depends(get_current_active_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Delete user (Admin only)
    
    Args:
        user_id: User ID to delete
        current_user: Current authenticated user
        auth_service: Authentication service
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If user is not admin or trying to delete self
    """
    if current_user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    if current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    user = auth_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    auth_service.db.delete(user)
    auth_service.db.commit()
    
    return {"message": "User deleted successfully"}

@router.post("/logout")
async def logout_user(
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    Logout user (client should discard tokens)
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Success message
    """
    # In a stateless JWT system, logout is handled client-side
    # by discarding the tokens. For enhanced security, you could
    # implement a token blacklist in Redis or database.
    return {"message": "Logged out successfully"}