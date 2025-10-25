"""
Alert Model
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.database import Base

class AlertType(str, enum.Enum):
    """Alert type enumeration"""
    PRICE_DROP = "price_drop"
    PRICE_SPIKE = "price_spike"
    VOLATILITY = "volatility"
    VOLUME_ANOMALY = "volume_anomaly"

class AlertStatus(str, enum.Enum):
    """Alert status enumeration"""
    PENDING = "pending"
    TRIGGERED = "triggered"
    ACKNOWLEDGED = "acknowledged"
    EXPIRED = "expired"

class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False)
    alert_type = Column(Enum(AlertType), nullable=False)
    threshold_value = Column(Float, nullable=False)
    current_value = Column(Float, nullable=True)
    message = Column(Text, nullable=False)
    status = Column(Enum(AlertStatus), default=AlertStatus.PENDING, nullable=False)
    triggered_at = Column(DateTime, nullable=True)
    acknowledged_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="alerts")
    stock = relationship("Stock", back_populates="alerts")




