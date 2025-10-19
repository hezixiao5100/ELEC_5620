"""
Stock Schemas
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# TODO: Define StockBase schema
# class StockBase(BaseModel):
#     symbol: str
#     name: str
#     sector: Optional[str] = None

# TODO: Define StockCreate schema
# class StockCreate(StockBase):
#     pass

# TODO: Define StockResponse schema
# class StockResponse(StockBase):
#     id: int
#     market_cap: Optional[float]
#     created_at: datetime
#     updated_at: datetime
#     
#     class Config:
#         from_attributes = True

# TODO: Define StockDataResponse schema
# class StockDataResponse(BaseModel):
#     id: int
#     stock_id: int
#     timestamp: datetime
#     open_price: float
#     high_price: float
#     low_price: float
#     close_price: float
#     volume: int
#     adjusted_close: Optional[float]
#     
#     class Config:
#         from_attributes = True

# TODO: Define TrackStockRequest schema
# class TrackStockRequest(BaseModel):
#     symbol: str


