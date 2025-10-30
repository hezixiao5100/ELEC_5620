"""
Alert Management API Routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas.alert import Alert, AlertCreate, AlertUpdate, AlertSummary
from app.services.alert_service import AlertService
from app.services.auth_service import get_current_active_user
from app.models.user import User as UserModel
from app.models.alert import Alert as AlertModel, AlertStatus
from datetime import datetime

router = APIRouter()

@router.get("/", response_model=List[Alert])
async def get_user_alerts(
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get all alerts for current user
    """
    try:
        alert_service = AlertService(db)
        alerts = await alert_service.get_user_alerts(current_user.id)
        return alerts
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/active", response_model=List[Alert])
async def get_active_alerts(
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get active (triggered) alerts for current user
    """
    try:
        alert_service = AlertService(db)
        alerts = await alert_service.get_active_alerts(current_user.id)
        return alerts
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/summary", response_model=AlertSummary)
async def get_alert_summary(
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get alert summary statistics
    """
    try:
        alert_service = AlertService(db)
        summary = await alert_service.get_alert_summary(current_user.id)
        return summary
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{alert_id}/acknowledge")
async def acknowledge_alert(
    alert_id: int,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Mark an alert as acknowledged
    """
    try:
        alert_service = AlertService(db)
        await alert_service.acknowledge_alert(alert_id, current_user.id)
        return {"message": "Alert acknowledged successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{alert_id}/analyze")
async def analyze_alert(
    alert_id: int,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Generate specialized analysis for a triggered alert
    """
    try:
        from app.services.smart_alert_service import SmartAlertService
        
        smart_alert_service = SmartAlertService(db)
        
        # Get the alert (allow both TRIGGERED and ACKNOWLEDGED alerts)
        alert = db.query(AlertModel).filter(
            AlertModel.id == alert_id,
            AlertModel.user_id == current_user.id,
            AlertModel.status.in_([AlertStatus.TRIGGERED, AlertStatus.ACKNOWLEDGED])
        ).first()
        
        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found or not triggered")
        
        # Generate analysis
        analysis = await smart_alert_service._generate_drop_analysis(alert, {})
        
        # Save analysis as a report
        from app.services.report_service import ReportService
        report_service = ReportService(db)
        
        # Create a specialized report for the alert analysis
        report_data = {
            "title": f"Alert Analysis: {alert.stock.symbol} Price Drop Analysis",
            "summary": analysis.get("summary", "Price drop analysis completed"),
            "content": f"""
# Alert Analysis Report for {alert.stock.symbol}

## Analysis Results
{analysis.get("technical_analysis", "Technical analysis not available")}

## Fundamental Analysis
{analysis.get("fundamental_analysis", "Fundamental analysis not available")}

## Risk Assessment
- Risk Level: {analysis.get("risk_level", "Unknown")}
- Confidence: {analysis.get("confidence", "Unknown")}

## Recommendation
{analysis.get("recommendation", "No specific recommendation")}

## Key Factors
{', '.join(analysis.get("key_factors", []))}

---
*Generated from triggered alert analysis*
            """,
            "recommendations": analysis.get("recommendation", "HOLD"),
            "risk_level": analysis.get("risk_level", "Medium"),
            "sentiment_score": analysis.get("sentiment_score", 0),
            "technical_signal": analysis.get("technical_signal", "Neutral"),
            "confidence_score": analysis.get("confidence", 5),
            "report_type": "alert_analysis"
        }
        
        # Save the report
        saved_report = await report_service.generate_report(
            user_id=current_user.id,
            stock_id=alert.stock_id,
            report_type="alert_analysis"
        )
        
        return {
            "alert_id": alert_id,
            "analysis": analysis,
            "report_id": saved_report.id,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{alert_id}/threshold")
async def update_alert_threshold(
    alert_id: int,
    new_threshold: float,
    db: Session = Depends(get_db)
):
    """
    Update alert threshold
    """
    try:
        alert_service = AlertService(db)
        alert = await alert_service.update_alert_threshold(alert_id, new_threshold)
        return {"message": "Alert threshold updated successfully", "alert": alert}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{alert_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_alert(
    alert_id: int,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete an alert
    """
    try:
        alert_service = AlertService(db)
        await alert_service.delete_alert(alert_id, current_user.id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))