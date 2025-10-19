"""
Alert Schemas
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# TODO: Define AlertBase schema
# class AlertBase(BaseModel):
#     stock_id: int
#     alert_type: str
#     threshold_value: float

# TODO: Define AlertCreate schema
# class AlertCreate(AlertBase):
#     pass

# TODO: Define AlertResponse schema
# class AlertResponse(AlertBase):
#     id: int
#     user_id: int
#     current_value: Optional[float]
#     message: str
#     status: str
#     triggered_at: Optional[datetime]
#     created_at: datetime
#     
#     class Config:
#         from_attributes = True

# TODO: Define AlertUpdate schema
# class AlertUpdate(BaseModel):
#     status: Optional[str] = None


