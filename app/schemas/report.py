"""
Report Schemas
"""
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

# TODO: Define ReportRequest schema
# class ReportRequest(BaseModel):
#     stock_id: int

# TODO: Define ReportResponse schema
# class ReportResponse(BaseModel):
#     id: int
#     user_id: int
#     stock_id: int
#     summary: str
#     risk_level: Optional[str]
#     sentiment_score: Optional[float]
#     technical_signal: Optional[str]
#     details_json: Optional[Dict[str, Any]]
#     created_at: datetime
#     
#     class Config:
#         from_attributes = True

# TODO: Define AnalysisResult schema (internal use)
# class AnalysisResult(BaseModel):
#     technical_analysis: Dict[str, Any]
#     risk_analysis: Dict[str, Any]
#     sentiment_analysis: Dict[str, Any]
#     recommendation: str


