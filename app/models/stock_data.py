"""
Stock Data Model (Price History)
"""
from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime

# TODO: Import Base from database
# from app.database import Base

# TODO: Define StockData model
# class StockData(Base):
#     __tablename__ = "stock_data"
#     
#     id = Column(Integer, primary_key=True, index=True)
#     stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False)
#     timestamp = Column(DateTime, nullable=False, index=True)
#     open_price = Column(Float, nullable=False)
#     high_price = Column(Float, nullable=False)
#     low_price = Column(Float, nullable=False)
#     close_price = Column(Float, nullable=False)
#     volume = Column(Integer, nullable=False)
#     adjusted_close = Column(Float, nullable=True)
#     
#     # Relationships
#     # stock = relationship("Stock", back_populates="stock_data")
#     
#     # Composite index for efficient queries
#     __table_args__ = (
#         Index('idx_stock_timestamp', 'stock_id', 'timestamp'),
#     )


