"""
Stock Management API Routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.database import get_db
from app.schemas.stock import Stock, StockCreate, StockData, TrackStockRequest, TrackedStock
from app.services.stock_service import StockService
from app.services.auth_service import get_current_active_user
from app.models.user import User as UserModel

router = APIRouter()

@router.post("/track", status_code=status.HTTP_201_CREATED)
async def track_stock(
    request: TrackStockRequest,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Add a stock to user's tracking list
    """
    try:
        stock_service = StockService(db)
        result = await stock_service.track_stock(
            request.symbol, 
            current_user.id, 
            request.custom_alert_threshold,
            request.quantity,
            request.purchase_price
        )
        return {"message": f"Successfully tracking {request.symbol}", "data": result}
    except ValueError as e:
        # User-friendly error for invalid stocks
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Log and return generic error
        import logging
        logging.getLogger("stocks_api").error(f"Error tracking stock {request.symbol}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to track stock: {str(e)}")

@router.put("/track/{symbol}/threshold")
async def update_track_threshold(
    symbol: str,
    request: TrackStockRequest,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update alert threshold for a tracked stock
    """
    try:
        stock_service = StockService(db)
        await stock_service.update_track_threshold(symbol, current_user.id, request.custom_alert_threshold)
        return {"message": f"Successfully updated threshold for {symbol}"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/track/{symbol}/portfolio")
async def update_portfolio(
    symbol: str,
    quantity: float,
    purchase_price: float,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update portfolio holding for a tracked stock
    """
    try:
        from app.models.stock import Stock as StockModel
        from app.models.portfolio import Portfolio as PortfolioModel
        from sqlalchemy import and_
        
        # Get stock
        stock = db.query(StockModel).filter(StockModel.symbol == symbol.upper()).first()
        if not stock:
            raise HTTPException(status_code=404, detail=f"Stock {symbol} not found")
        
        # Get or create portfolio
        portfolio = db.query(PortfolioModel).filter(
            and_(
                PortfolioModel.user_id == current_user.id,
                PortfolioModel.stock_id == stock.id
            )
        ).first()
        
        if portfolio:
            portfolio.quantity = quantity
            portfolio.purchase_price = purchase_price
            portfolio.updated_at = datetime.utcnow()
        else:
            portfolio = PortfolioModel(
                user_id=current_user.id,
                stock_id=stock.id,
                quantity=quantity,
                purchase_price=purchase_price,
                purchase_date=datetime.utcnow()
            )
            db.add(portfolio)
        
        db.commit()
        return {"message": f"Successfully updated portfolio for {symbol}"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/track/{symbol}")
async def untrack_stock(
    symbol: str,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Remove a stock from user's tracking list
    """
    try:
        stock_service = StockService(db)
        await stock_service.untrack_stock(symbol, current_user.id)
        return {"message": f"Successfully stopped tracking {symbol}"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/tracked", response_model=List[TrackedStock])
async def get_tracked_stocks(
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get all stocks tracked by current user
    """
    try:
        stock_service = StockService(db)
        stocks = await stock_service.get_tracked_stocks(current_user.id)
        return stocks
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/search")
async def search_stocks(
    q: str,
    db: Session = Depends(get_db)
):
    """
    Search for stocks by symbol or name
    """
    try:
        stock_service = StockService(db)
        results = await stock_service.search_stocks(q)
        return {"query": q, "results": results}
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

@router.get("/{symbol}/analysis")
async def get_stock_analysis(
    symbol: str,
    db: Session = Depends(get_db)
):
    """
    Get the latest analysis report for a stock
    """
    try:
        from app.services.report_service import ReportService
        from app.models.stock import Stock as StockModel
        from sqlalchemy import desc
        
        # Get stock by symbol
        stock = db.query(StockModel).filter(StockModel.symbol == symbol.upper()).first()
        if not stock:
            raise HTTPException(status_code=404, detail=f"Stock {symbol} not found")
        
        # Get the latest report for this stock
        from app.models.report import Report as ReportModel
        latest_report = db.query(ReportModel).filter(
            ReportModel.stock_id == stock.id
        ).order_by(desc(ReportModel.created_at)).first()
        
        if not latest_report:
            return {
                "message": "No analysis report found. Please generate a report first.",
                "stock_symbol": symbol,
                "stock_name": stock.name,
                "has_report": False
            }
        
        # Return the report data
        return {
            "stock_symbol": symbol,
            "stock_name": stock.name,
            "has_report": True,
            "report": {
                "id": latest_report.id,
                "title": latest_report.title,
                "summary": latest_report.summary,
                "trading_signal": latest_report.technical_signal,
                "risk_level": latest_report.risk_level,
                "sentiment_score": latest_report.sentiment_score,
                "confidence_score": latest_report.confidence_score,
                "created_at": latest_report.created_at.isoformat()
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))




