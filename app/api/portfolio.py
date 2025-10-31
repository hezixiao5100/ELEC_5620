"""
Portfolio Management API Routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas.stock import TrackedStock
from app.services.stock_service import StockService

router = APIRouter()

@router.get("/", response_model=List[TrackedStock])
async def get_portfolio(
    db: Session = Depends(get_db)
):
    """
    Get user's portfolio (tracked stocks)
    """
    try:
        stock_service = StockService(db)
        stocks = await stock_service.get_tracked_stocks()
        return stocks
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/summary")
async def get_portfolio_summary(
    db: Session = Depends(get_db)
):
    """
    Get portfolio summary statistics
    """
    try:
        stock_service = StockService(db)
        summary = await stock_service.get_portfolio_summary()
        return summary
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))