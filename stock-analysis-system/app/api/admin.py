"""
Admin API Routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel

from app.database import get_db
from app.schemas.user import User
from app.services.auth_service import AuthService, get_current_active_user
from app.models.user import User as UserModel
from app.services.ai.langchain_service import get_current_model, set_current_model

router = APIRouter()

@router.get("/users", response_model=List[User])
async def get_all_users(
    db: Session = Depends(get_db)
):
    """
    Get all users (admin only)
    """
    try:
        auth_service = AuthService(db)
        users = await auth_service.get_all_users()
        return users
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/stats")
async def get_system_stats(
    db: Session = Depends(get_db)
):
    """
    Get system statistics
    """
    try:
        # TODO: Implement system stats
        return {"message": "System stats endpoint - not implemented yet"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Model configuration endpoints
class ModelConfigUpdate(BaseModel):
    model: str

@router.get("/config/model")
async def get_model_config(
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    Get current AI model configuration (Admin only)
    """
    # Check if user is admin
    if current_user.role.value != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can access model configuration"
        )
    
    return {
        "model": get_current_model(),
        "available_models": [
            {"value": "gpt-4o-mini", "label": "GPT-4o Mini (Fast, Recommended)"},
            {"value": "gpt-4o", "label": "GPT-4o (Powerful)"},
            {"value": "gpt-3.5-turbo", "label": "GPT-3.5 Turbo (Classic)"},
            {"value": "gpt-4-turbo", "label": "GPT-4 Turbo (Advanced)"},
            {"value": "gpt-4", "label": "GPT-4 (Premium)"}
        ]
    }

@router.put("/config/model")
async def update_model_config(
    config: ModelConfigUpdate,
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    Update AI model configuration (Admin only)
    """
    # Check if user is admin
    if current_user.role.value != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can modify model configuration"
        )
    
    if set_current_model(config.model):
        return {
            "message": "Model configuration updated successfully",
            "model": config.model
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid model name"
        )