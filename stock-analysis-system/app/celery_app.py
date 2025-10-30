"""
Celery Application Configuration
Background task processing for stock analysis system
"""
from celery import Celery
from celery.schedules import crontab
from app.config import settings

# Create Celery instance
celery_app = Celery(
    "stock_analysis",
    broker=f"redis://localhost:6379/0",
    backend=f"redis://localhost:6379/0",
    include=[
        "app.tasks.monitoring_tasks",
        "app.tasks.data_update_tasks", 
        "app.tasks.report_tasks",
        "app.tasks.alert_tasks",
        "app.tasks.smart_alert_tasks"
    ]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    result_expires=3600,  # 1 hour
)

# Periodic task schedule
celery_app.conf.beat_schedule = {
    # High frequency: Monitor stock prices every 15 minutes
    "monitor-stock-prices": {
        "task": "app.tasks.monitoring_tasks.monitor_stock_prices",
        "schedule": crontab(minute="*/15"),  # Every 15 minutes
    },
    
    # Medium frequency: Update stock data every hour
    "update-stock-data": {
        "task": "app.tasks.data_update_tasks.update_stock_data",
        "schedule": crontab(minute=0),  # Every hour at minute 0
    },
    
    # Low frequency: Generate daily reports at 6 AM
    "generate-daily-reports": {
        "task": "app.tasks.report_tasks.generate_daily_reports",
        "schedule": crontab(hour=6, minute=0),  # 6:00 AM daily
    },
    
    # Check alerts every 1 minute for fast response
    "check-price-alerts": {
        "task": "app.tasks.alert_tasks.check_price_alerts",
        "schedule": crontab(minute="*/1"),  # Every 1 minute
    },
    
    # Smart alert checking every 15 minutes
    "check-smart-alerts": {
        "task": "app.tasks.smart_alert_tasks.check_smart_alerts",
        "schedule": crontab(minute="*/15"),  # Every 15 minutes
    },
    
    # Update news data every 2 hours
    "update-news-data": {
        "task": "app.tasks.data_update_tasks.update_news_data",
        "schedule": crontab(minute=0, hour="*/2"),  # Every 2 hours
    },
    
    # Clean up old data weekly
    "cleanup-old-data": {
        "task": "app.tasks.data_update_tasks.cleanup_old_data",
        "schedule": crontab(hour=2, minute=0, day_of_week=1),  # Monday 2:00 AM
    },
    
    # System monitoring tasks
    "collect-system-metrics": {
        "task": "app.tasks.monitoring_tasks.collect_system_metrics",
        "schedule": crontab(minute="*/5"),  # Every 5 minutes
    },
    "collect-database-metrics": {
        "task": "app.tasks.monitoring_tasks.collect_database_metrics",
        "schedule": crontab(minute="*/10"),  # Every 10 minutes
    },
    "collect-business-metrics": {
        "task": "app.tasks.monitoring_tasks.collect_business_metrics",
        "schedule": crontab(minute="*/15"),  # Every 15 minutes
    },
    "check-system-health": {
        "task": "app.tasks.monitoring_tasks.check_system_health",
        "schedule": crontab(minute="*/2"),  # Every 2 minutes
    },
    "generate-monitoring-report": {
        "task": "app.tasks.monitoring_tasks.generate_monitoring_report",
        "schedule": crontab(minute=0, hour="*"),  # Every hour
    },
    "cleanup-old-metrics": {
        "task": "app.tasks.monitoring_tasks.cleanup_old_metrics",
        "schedule": crontab(minute=0, hour=2),  # Daily at 2 AM
    },
}

# Task routing
celery_app.conf.task_routes = {
    "app.tasks.monitoring_tasks.*": {"queue": "monitoring"},
    "app.tasks.data_update_tasks.*": {"queue": "data_update"},
    "app.tasks.report_tasks.*": {"queue": "reports"},
    "app.tasks.alert_tasks.*": {"queue": "alerts"},
    "app.tasks.smart_alert_tasks.*": {"queue": "smart_alerts"},
}

# Error handling
celery_app.conf.task_acks_late = True
celery_app.conf.worker_disable_rate_limits = False
celery_app.conf.task_reject_on_worker_lost = True

if __name__ == "__main__":
    celery_app.start()
