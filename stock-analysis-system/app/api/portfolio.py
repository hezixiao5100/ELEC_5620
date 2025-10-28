"""
Portfolio Management API Routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas.stock import TrackedStock
from app.services.stock_service import StockService
from app.services.auth_service import get_current_active_user
from app.models.user import User as UserModel

router = APIRouter()

@router.get("/tracked", response_model=List[TrackedStock])
async def get_tracked_stocks(
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get user's tracked stocks
    """
    try:
        stock_service = StockService(db)
        stocks = stock_service.get_tracked_stocks_by_user(current_user.id)
        return stocks
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/summary")
async def get_portfolio_summary(
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get portfolio summary statistics
    """
    try:
        stock_service = StockService(db)
        result = await stock_service.get_portfolio_summary(current_user.id)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))