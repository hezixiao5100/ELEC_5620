"""
Stock Management API Routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas.stock import Stock, StockCreate, StockData, TrackStockRequest, TrackedStock
from app.services.stock_service import StockService

router = APIRouter()

@router.post("/track", status_code=status.HTTP_201_CREATED)
async def track_stock(
    request: TrackStockRequest,
    db: Session = Depends(get_db)
):
    """
    Add a stock to user's tracking list
    """
    try:
        stock_service = StockService(db)
        result = await stock_service.track_stock(request.symbol, request.custom_alert_threshold)
        return {"message": f"Successfully tracking {request.symbol}", "data": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/track/{symbol}")
async def untrack_stock(
    symbol: str,
    db: Session = Depends(get_db)
):
    """
    Remove a stock from user's tracking list
    """
    try:
        stock_service = StockService(db)
        await stock_service.untrack_stock(symbol)
        return {"message": f"Successfully stopped tracking {symbol}"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/tracked", response_model=List[TrackedStock])
async def get_tracked_stocks(
    db: Session = Depends(get_db)
):
    """
    Get all stocks tracked by current user
    """
    try:
        stock_service = StockService(db)
        stocks = await stock_service.get_tracked_stocks()
        return stocks
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{symbol}", response_model=Stock)
async def get_stock_info(
    symbol: str,
    db: Session = Depends(get_db)
):
    """
    Get stock information by symbol
    """
    try:
        stock_service = StockService(db)
        stock = await stock_service.get_stock_by_symbol(symbol)
        if not stock:
            raise HTTPException(status_code=404, detail="Stock not found")
        return stock
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{symbol}/data", response_model=List[StockData])
async def get_stock_data(
    symbol: str,
    period: str = "1d",  # 1d, 1w, 1m, 3m, 1y
    db: Session = Depends(get_db)
):
    """
    Get historical stock price data
    """
    try:
        stock_service = StockService(db)
        data = await stock_service.get_stock_data(symbol, period)
        return data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/search/{query}")
async def search_stocks(
    query: str,
    db: Session = Depends(get_db)
):
    """
    Search for stocks by symbol or name
    """
    try:
        stock_service = StockService(db)
        results = await stock_service.search_stocks(query)
        return {"query": query, "results": results}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))




