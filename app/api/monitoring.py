"""
Monitoring API Endpoints
System monitoring and health check endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any, List
from datetime import datetime, timedelta

from app.database import get_db
from app.services.monitoring_service import MonitoringService
from app.services.auth_service import get_current_active_user, require_admin
from app.models.user import User as UserModel
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger("monitoring_api")

@router.get("/health")
async def get_system_health():
    """
    Get overall system health status
    """
    try:
        monitoring_service = MonitoringService()
        health_status = monitoring_service.get_health_status()
        
        return health_status
        
    except Exception as e:
        logger.error(f"Failed to get system health: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get system health: {str(e)}"
        )

@router.get("/metrics")
async def get_system_metrics(
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    Get comprehensive system metrics (requires authentication)
    """
    try:
        monitoring_service = MonitoringService()
        metrics = monitoring_service.get_comprehensive_metrics()
        
        return metrics
        
    except Exception as e:
        logger.error(f"Failed to get system metrics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get system metrics: {str(e)}"
        )

@router.get("/metrics/system")
async def get_system_performance_metrics(
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    Get system performance metrics (CPU, memory, disk)
    """
    try:
        monitoring_service = MonitoringService()
        system_metrics = monitoring_service.system_monitor.get_system_metrics()
        
        return system_metrics
        
    except Exception as e:
        logger.error(f"Failed to get system performance metrics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get system performance metrics: {str(e)}"
        )

@router.get("/metrics/database")
async def get_database_metrics(
    current_user: UserModel = Depends(require_admin)
):
    """
    Get database performance metrics (Admin only)
    """
    try:
        monitoring_service = MonitoringService()
        db_metrics = monitoring_service.database_monitor.get_database_metrics()
        
        return db_metrics
        
    except Exception as e:
        logger.error(f"Failed to get database metrics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get database metrics: {str(e)}"
        )

@router.get("/metrics/tasks")
async def get_task_metrics(
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    Get Celery task metrics
    """
    try:
        monitoring_service = MonitoringService()
        task_metrics = monitoring_service.task_monitor.get_task_metrics()
        
        return task_metrics
        
    except Exception as e:
        logger.error(f"Failed to get task metrics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get task metrics: {str(e)}"
        )

@router.get("/metrics/business")
async def get_business_metrics(
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    Get business metrics (users, stocks, alerts, reports)
    """
    try:
        monitoring_service = MonitoringService()
        business_metrics = monitoring_service.business_monitor.get_business_metrics()
        
        return business_metrics
        
    except Exception as e:
        logger.error(f"Failed to get business metrics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get business metrics: {str(e)}"
        )

@router.get("/metrics/performance")
async def get_performance_summary(
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    Get performance summary statistics
    """
    try:
        monitoring_service = MonitoringService()
        performance_summary = monitoring_service.system_monitor.get_performance_summary()
        
        return performance_summary
        
    except Exception as e:
        logger.error(f"Failed to get performance summary: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get performance summary: {str(e)}"
        )

@router.get("/metrics/history")
async def get_metrics_history(
    hours: int = 24,
    current_user: UserModel = Depends(require_admin)
):
    """
    Get metrics history for the specified hours (Admin only)
    """
    try:
        if hours > 168:  # Limit to 1 week
            hours = 168
            
        monitoring_service = MonitoringService()
        history = monitoring_service.system_monitor.get_metrics_history(hours)
        
        return {
            "hours": hours,
            "data_points": len(history),
            "metrics": history
        }
        
    except Exception as e:
        logger.error(f"Failed to get metrics history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get metrics history: {str(e)}"
        )

@router.get("/alerts")
async def get_system_alerts(
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    Get system alerts and warnings
    """
    try:
        monitoring_service = MonitoringService()
        health_status = monitoring_service.get_health_status()
        
        alerts = []
        
        # Check for system issues
        if health_status.get("status") != "healthy":
            for issue in health_status.get("issues", []):
                alerts.append({
                    "type": "warning" if health_status.get("status") == "warning" else "critical",
                    "message": issue,
                    "timestamp": datetime.utcnow().isoformat(),
                    "category": "system"
                })
        
        # Check for high resource usage
        system_metrics = monitoring_service.system_monitor.get_system_metrics()
        
        if system_metrics["cpu"]["percent"] > 70:
            alerts.append({
                "type": "warning",
                "message": f"High CPU usage: {system_metrics['cpu']['percent']:.1f}%",
                "timestamp": datetime.utcnow().isoformat(),
                "category": "performance"
            })
        
        if system_metrics["memory"]["percent"] > 80:
            alerts.append({
                "type": "warning",
                "message": f"High memory usage: {system_metrics['memory']['percent']:.1f}%",
                "timestamp": datetime.utcnow().isoformat(),
                "category": "performance"
            })
        
        if system_metrics["disk"]["percent"] > 85:
            alerts.append({
                "type": "critical",
                "message": f"High disk usage: {system_metrics['disk']['percent']:.1f}%",
                "timestamp": datetime.utcnow().isoformat(),
                "category": "storage"
            })
        
        return {
            "alerts": alerts,
            "total_alerts": len(alerts),
            "critical_alerts": len([a for a in alerts if a["type"] == "critical"]),
            "warning_alerts": len([a for a in alerts if a["type"] == "warning"])
        }
        
    except Exception as e:
        logger.error(f"Failed to get system alerts: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get system alerts: {str(e)}"
        )

@router.get("/dashboard")
async def get_monitoring_dashboard(
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    Get monitoring dashboard data
    """
    try:
        monitoring_service = MonitoringService()
        
        # Get all metrics
        health_status = monitoring_service.get_health_status()
        system_metrics = monitoring_service.system_monitor.get_system_metrics()
        business_metrics = monitoring_service.business_monitor.get_business_metrics()
        performance_summary = monitoring_service.system_monitor.get_performance_summary()
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "health": health_status,
            "system": {
                "cpu": system_metrics["cpu"],
                "memory": system_metrics["memory"],
                "disk": system_metrics["disk"]
            },
            "business": business_metrics,
            "performance": performance_summary,
            "status": "healthy" if health_status.get("status") == "healthy" else "warning"
        }
        
    except Exception as e:
        logger.error(f"Failed to get monitoring dashboard: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get monitoring dashboard: {str(e)}"
        )
