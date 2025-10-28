"""
Report Model
"""
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base

class Report(Base):
    __tablename__ = "reports"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False)
    title = Column(String(200), nullable=False)
    summary = Column(Text, nullable=False)
    content = Column(Text, nullable=True)  # Full report content
    recommendations = Column(Text, nullable=True)  # Investment recommendations
    risk_level = Column(String(20), nullable=True)  # LOW, MEDIUM, HIGH
    sentiment_score = Column(Float, nullable=True)  # -1.0 to 1.0
    technical_signal = Column(String(20), nullable=True)  # BUY, SELL, HOLD
    confidence_score = Column(Float, nullable=True)  # 0.0 to 1.0
    details_json = Column(JSON, nullable=True)  # Store detailed analysis as JSON
    report_type = Column(String(50), default="analysis", nullable=False)  # analysis, alert, summary
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    user = relationship("User", back_populates="reports")
    stock = relationship("Stock", back_populates="reports")




