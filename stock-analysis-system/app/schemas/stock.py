"""
Stock Schemas
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class StockBase(BaseModel):
    """Base stock schema"""
    symbol: str
    name: str
    sector: Optional[str] = None
    industry: Optional[str] = None
    market_cap: Optional[float] = None
    current_price: Optional[float] = None
    currency: str = "USD"
    exchange: Optional[str] = None

class StockCreate(StockBase):
    """Schema for creating a new stock"""
    pass

class StockUpdate(BaseModel):
    """Schema for updating stock information"""
    name: Optional[str] = None
    sector: Optional[str] = None
    industry: Optional[str] = None
    market_cap: Optional[float] = None
    current_price: Optional[float] = None
    exchange: Optional[str] = None

class Stock(StockBase):
    """Schema for stock response"""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class StockDataBase(BaseModel):
    """Base stock data schema"""
    timestamp: datetime
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    volume: int
    adjusted_close: Optional[float] = None
    data_source: str = "API"

class StockDataCreate(StockDataBase):
    """Schema for creating stock data"""
    stock_id: int

class StockData(StockDataBase):
    """Schema for stock data response"""
    id: int
    stock_id: int
    
    class Config:
        from_attributes = True

class TrackStockRequest(BaseModel):
    """Schema for tracking a stock"""
    symbol: str
    custom_alert_threshold: Optional[float] = None
    # Optional portfolio information
    quantity: Optional[float] = None  # Number of shares purchased
    purchase_price: Optional[float] = None  # Purchase price per share

class TrackedStock(BaseModel):
    """Schema for tracked stock response"""
    id: int
    user_id: int
    stock_id: int
    stock: Stock
    custom_alert_threshold: Optional[float]
    is_active: str  # "Y" or "N"
    created_at: datetime
    updated_at: datetime
    
    # Portfolio information (if exists)
    portfolio: Optional[dict] = None  # Will include quantity, purchase_price, profit_loss, etc.
    
    class Config:
        from_attributes = True




