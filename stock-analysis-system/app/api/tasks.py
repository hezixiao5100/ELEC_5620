"""
Task Management API
Endpoints for managing background tasks
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime

from app.database import get_db
from app.services.auth_service import get_current_active_user, require_admin
from app.models.user import User as UserModel
from app.celery_app import celery_app
from app.tasks.monitoring_tasks import monitor_stock_prices, monitor_market_conditions, health_check
from app.tasks.data_update_tasks import update_stock_data, update_news_data, cleanup_old_data
from app.tasks.report_tasks import generate_daily_reports, generate_weekly_summary, generate_market_report
from app.tasks.alert_tasks import check_price_alerts, send_alert_notifications, cleanup_expired_alerts

router = APIRouter(tags=["Background Tasks"])

@router.get("/status")
async def get_task_status(
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    Get overall task system status
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Task system status information
    """
    try:
        # Get Celery worker status
        inspect = celery_app.control.inspect()
        
        # Get active tasks
        active_tasks = inspect.active()
        
        # Get scheduled tasks
        scheduled_tasks = inspect.scheduled()
        
        # Get registered tasks
        registered_tasks = inspect.registered()
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "active_tasks": len(active_tasks) if active_tasks else 0,
            "scheduled_tasks": len(scheduled_tasks) if scheduled_tasks else 0,
            "registered_tasks": len(registered_tasks) if registered_tasks else 0,
            "workers": list(active_tasks.keys()) if active_tasks else [],
            "message": "Task system is operational"
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e),
            "message": "Task system is not operational"
        }

@router.get("/monitoring/trigger")
async def trigger_monitoring_tasks(
    current_user: UserModel = Depends(require_admin)
):
    """
    Manually trigger monitoring tasks (Admin only)
    
    Args:
        current_user: Current authenticated admin user
        
    Returns:
        Task trigger results
    """
    try:
        # Trigger stock price monitoring
        price_task = monitor_stock_prices.delay()
        
        # Trigger market conditions monitoring
        market_task = monitor_market_conditions.delay()
        
        # Trigger health check
        health_task = health_check.delay()
        
        return {
            "status": "triggered",
            "tasks": {
                "stock_monitoring": price_task.id,
                "market_monitoring": market_task.id,
                "health_check": health_task.id
            },
            "message": "Monitoring tasks triggered successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to trigger monitoring tasks: {str(e)}"
        )

@router.get("/data/trigger")
async def trigger_data_update_tasks(
    current_user: UserModel = Depends(require_admin)
):
    """
    Manually trigger data update tasks (Admin only)
    
    Args:
        current_user: Current authenticated admin user
        
    Returns:
        Task trigger results
    """
    try:
        # Trigger stock data update
        stock_task = update_stock_data.delay()
        
        # Trigger news data update
        news_task = update_news_data.delay()
        
        return {
            "status": "triggered",
            "tasks": {
                "stock_data_update": stock_task.id,
                "news_data_update": news_task.id
            },
            "message": "Data update tasks triggered successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to trigger data update tasks: {str(e)}"
        )

@router.get("/reports/trigger")
async def trigger_report_tasks(
    current_user: UserModel = Depends(require_admin)
):
    """
    Manually trigger report generation tasks (Admin only)
    
    Args:
        current_user: Current authenticated admin user
        
    Returns:
        Task trigger results
    """
    try:
        # Trigger daily report generation
        daily_task = generate_daily_reports.delay()
        
        # Trigger weekly summary
        weekly_task = generate_weekly_summary.delay()
        
        # Trigger market report
        market_task = generate_market_report.delay()
        
        return {
            "status": "triggered",
            "tasks": {
                "daily_reports": daily_task.id,
                "weekly_summary": weekly_task.id,
                "market_report": market_task.id
            },
            "message": "Report generation tasks triggered successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to trigger report tasks: {str(e)}"
        )

@router.get("/alerts/trigger")
async def trigger_alert_tasks(
    current_user: UserModel = Depends(require_admin)
):
    """
    Manually trigger alert tasks (Admin only)
    
    Args:
        current_user: Current authenticated admin user
        
    Returns:
        Task trigger results
    """
    try:
        # Trigger price alert checking
        alert_task = check_price_alerts.delay()
        
        # Trigger notification sending
        notification_task = send_alert_notifications.delay()
        
        return {
            "status": "triggered",
            "tasks": {
                "price_alerts": alert_task.id,
                "notifications": notification_task.id
            },
            "message": "Alert tasks triggered successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to trigger alert tasks: {str(e)}"
        )

@router.get("/task/{task_id}")
async def get_task_result(
    task_id: str,
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    Get result of a specific task
    
    Args:
        task_id: Task ID to check
        current_user: Current authenticated user
        
    Returns:
        Task result information
    """
    try:
        # Get task result from Celery
        result = celery_app.AsyncResult(task_id)
        
        if result.state == "PENDING":
            return {
                "task_id": task_id,
                "state": "PENDING",
                "message": "Task is still running"
            }
        elif result.state == "SUCCESS":
            return {
                "task_id": task_id,
                "state": "SUCCESS",
                "result": result.result,
                "message": "Task completed successfully"
            }
        elif result.state == "FAILURE":
            return {
                "task_id": task_id,
                "state": "FAILURE",
                "error": str(result.result),
                "message": "Task failed"
            }
        else:
            return {
                "task_id": task_id,
                "state": result.state,
                "message": f"Task is in {result.state} state"
            }
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get task result: {str(e)}"
        )

@router.get("/cleanup/trigger")
async def trigger_cleanup_tasks(
    current_user: UserModel = Depends(require_admin)
):
    """
    Manually trigger cleanup tasks (Admin only)
    
    Args:
        current_user: Current authenticated admin user
        
    Returns:
        Task trigger results
    """
    try:
        # Trigger data cleanup
        cleanup_task = cleanup_old_data.delay()
        
        # Trigger expired alert cleanup
        alert_cleanup_task = cleanup_expired_alerts.delay()
        
        return {
            "status": "triggered",
            "tasks": {
                "data_cleanup": cleanup_task.id,
                "alert_cleanup": alert_cleanup_task.id
            },
            "message": "Cleanup tasks triggered successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to trigger cleanup tasks: {str(e)}"
        )

@router.get("/stats")
async def get_task_statistics(
    current_user: UserModel = Depends(require_admin)
):
    """
    Get task execution statistics (Admin only)
    
    Args:
        current_user: Current authenticated admin user
        
    Returns:
        Task statistics
    """
    try:
        # Get task statistics from Celery
        inspect = celery_app.control.inspect()
        
        # Get worker statistics
        stats = inspect.stats()
        
        # Get active tasks by type
        active_tasks = inspect.active()
        
        # Count tasks by type
        task_counts = {}
        if active_tasks:
            for worker, tasks in active_tasks.items():
                for task in tasks:
                    task_name = task.get('name', 'unknown')
                    task_counts[task_name] = task_counts.get(task_name, 0) + 1
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "workers": len(stats) if stats else 0,
            "active_tasks": sum(len(tasks) for tasks in active_tasks.values()) if active_tasks else 0,
            "task_breakdown": task_counts,
            "worker_stats": stats,
            "message": "Task statistics retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get task statistics: {str(e)}"
        )


