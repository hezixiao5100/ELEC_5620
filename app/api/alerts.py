"""
Alert Management API Routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas.alert import Alert, AlertCreate, AlertUpdate, AlertSummary
from app.services.alert_service import AlertService

router = APIRouter()

@router.get("/", response_model=List[Alert])
async def get_user_alerts(
    db: Session = Depends(get_db)
):
    """
    Get all alerts for current user
    """
    try:
        alert_service = AlertService(db)
        alerts = await alert_service.get_user_alerts()
        return alerts
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/active", response_model=List[Alert])
async def get_active_alerts(
    db: Session = Depends(get_db)
):
    """
    Get active (triggered) alerts for current user
    """
    try:
        alert_service = AlertService(db)
        alerts = await alert_service.get_active_alerts()
        return alerts
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/summary", response_model=AlertSummary)
async def get_alert_summary(
    db: Session = Depends(get_db)
):
    """
    Get alert summary statistics
    """
    try:
        alert_service = AlertService(db)
        summary = await alert_service.get_alert_summary()
        return summary
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{alert_id}/acknowledge")
async def acknowledge_alert(
    alert_id: int,
    db: Session = Depends(get_db)
):
    """
    Mark an alert as acknowledged
    """
    try:
        alert_service = AlertService(db)
        await alert_service.acknowledge_alert(alert_id)
        return {"message": "Alert acknowledged successfully"}
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
    db: Session = Depends(get_db)
):
    """
    Delete an alert
    """
    try:
        alert_service = AlertService(db)
        await alert_service.delete_alert(alert_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))




