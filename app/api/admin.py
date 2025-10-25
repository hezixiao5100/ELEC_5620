"""
Admin API Routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas.user import User
from app.services.auth_service import AuthService

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