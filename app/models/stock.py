"""
Stock Model
"""
from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

# TODO: Import Base from database
# from app.database import Base

# TODO: Define Stock model
# class Stock(Base):
#     __tablename__ = "stocks"
#     
#     id = Column(Integer, primary_key=True, index=True)
#     symbol = Column(String(10), unique=True, index=True, nullable=False)
#     name = Column(String(100), nullable=False)
#     sector = Column(String(50), nullable=True)
#     market_cap = Column(Float, nullable=True)
#     created_at = Column(DateTime, default=datetime.utcnow)
#     updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
#     
#     # Relationships
#     # stock_data = relationship("StockData", back_populates="stock")
#     # news = relationship("News", back_populates="stock")
#     # tracked_by = relationship("TrackedStock", back_populates="stock")
#     # alerts = relationship("Alert", back_populates="stock")
#     # reports = relationship("Report", back_populates="stock")


