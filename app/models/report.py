"""
Report Model
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

# TODO: Import Base from database
# from app.database import Base

# TODO: Define Report model
# class Report(Base):
#     __tablename__ = "reports"
#     
#     id = Column(Integer, primary_key=True, index=True)
#     user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
#     stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False)
#     summary = Column(Text, nullable=False)
#     risk_level = Column(String(20), nullable=True)  # LOW, MEDIUM, HIGH
#     sentiment_score = Column(Float, nullable=True)
#     technical_signal = Column(String(20), nullable=True)  # BUY, SELL, HOLD
#     details_json = Column(JSON, nullable=True)  # Store detailed analysis as JSON
#     created_at = Column(DateTime, default=datetime.utcnow, index=True)
#     
#     # Relationships
#     # user = relationship("User", back_populates="reports")
#     # stock = relationship("Stock", back_populates="reports")


