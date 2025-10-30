"""
Report Management API Routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas.report import Report, ReportRequest, ReportSummary
from app.services.report_service import ReportService
from app.services.auth_service import get_current_active_user
from app.models.user import User as UserModel

router = APIRouter()

@router.post("/generate", response_model=Report)
async def generate_report(
    request: ReportRequest,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Generate a new analysis report
    """
    try:
        report_service = ReportService(db)
        report = await report_service.generate_report(current_user.id, request.stock_id, request.report_type)
        return report
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[Report])
async def get_user_reports(
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get all reports for current user
    """
    try:
        report_service = ReportService(db)
        reports = await report_service.get_user_reports(current_user.id)
        return reports
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/summary", response_model=ReportSummary)
async def get_report_summary(
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get report summary statistics
    """
    try:
        report_service = ReportService(db)
        summary = await report_service.get_report_summary(current_user.id)
        return summary
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))