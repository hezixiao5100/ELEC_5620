"""
Report Schemas
"""
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class ReportRequest(BaseModel):
    """Schema for requesting a report"""
    stock_id: int
    report_type: str = "analysis"

class ReportBase(BaseModel):
    """Base report schema"""
    stock_id: int
    title: str
    summary: str
    risk_level: Optional[str] = None
    sentiment_score: Optional[float] = None
    technical_signal: Optional[str] = None
    confidence_score: Optional[float] = None
    report_type: str = "analysis"

class ReportCreate(ReportBase):
    """Schema for creating a report"""
    details_json: Optional[Dict[str, Any]] = None

class Report(ReportBase):
    """Schema for report response"""
    id: int
    user_id: int
    details_json: Optional[Dict[str, Any]]
    created_at: datetime
    
    class Config:
        from_attributes = True

class AnalysisResult(BaseModel):
    """Schema for analysis result (internal use)"""
    technical_analysis: Dict[str, Any]
    risk_analysis: Dict[str, Any]
    sentiment_analysis: Dict[str, Any]
    recommendation: str
    confidence_score: float

class ReportSummary(BaseModel):
    """Schema for report summary"""
    total_reports: int
    recent_reports: int
    risk_distribution: Dict[str, int]
    sentiment_distribution: Dict[str, int]




