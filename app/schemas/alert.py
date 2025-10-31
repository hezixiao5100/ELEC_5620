"""
Alert Schemas
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.alert import AlertType, AlertStatus

class AlertBase(BaseModel):
    """Base alert schema"""
    stock_id: int
    alert_type: AlertType
    threshold_value: float

class AlertCreate(AlertBase):
    """Schema for creating a new alert"""
    pass

class AlertUpdate(BaseModel):
    """Schema for updating alert"""
    status: Optional[AlertStatus] = None
    current_value: Optional[float] = None
    message: Optional[str] = None

class Alert(AlertBase):
    """Schema for alert response"""
    id: int
    user_id: int
    current_value: Optional[float]
    message: str
    status: AlertStatus
    triggered_at: Optional[datetime]
    acknowledged_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True

class AlertSummary(BaseModel):
    """Schema for alert summary"""
    total_alerts: int
    pending_alerts: int
    triggered_alerts: int
    acknowledged_alerts: int




