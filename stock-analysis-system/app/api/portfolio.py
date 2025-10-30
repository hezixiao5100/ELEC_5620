"""
Portfolio API Routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas.portfolio import Portfolio, PortfolioCreate, PortfolioUpdate, PortfolioSummary
from app.services.portfolio_service import PortfolioService
from app.services.auth_service import get_current_active_user
from app.models.user import User as UserModel

router = APIRouter()


@router.get("/", response_model=List[Portfolio])
async def get_portfolio(
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get all holdings in current user's portfolio
    """
    try:
        portfolio_service = PortfolioService(db)
        holdings = await portfolio_service.get_user_portfolio(current_user.id)
        return holdings
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/summary", response_model=PortfolioSummary)
async def get_portfolio_summary(
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get portfolio summary with total value, profit/loss, etc.
    """
    try:
        portfolio_service = PortfolioService(db)
        summary = await portfolio_service.get_portfolio_summary(current_user.id)
        return summary
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/", response_model=Portfolio, status_code=status.HTTP_201_CREATED)
async def add_holding(
    portfolio_data: PortfolioCreate,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Add a new stock holding to portfolio
    """
    try:
        portfolio_service = PortfolioService(db)
        holding = await portfolio_service.add_holding(current_user.id, portfolio_data)
        return holding
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{portfolio_id}", response_model=Portfolio)
async def update_holding(
    portfolio_id: int,
    update_data: PortfolioUpdate,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update a portfolio holding
    """
    try:
        portfolio_service = PortfolioService(db)
        holding = await portfolio_service.update_holding(current_user.id, portfolio_id, update_data)
        return holding
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{portfolio_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_holding(
    portfolio_id: int,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete a portfolio holding
    """
    try:
        portfolio_service = PortfolioService(db)
        await portfolio_service.delete_holding(current_user.id, portfolio_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
