"""
Smart Alert Tasks
Intelligent alert triggering with pattern analysis
"""
from celery import current_task
from app.celery_app import celery_app
from app.database import SessionLocal
from app.services.smart_alert_service import SmartAlertService
import logging

logger = logging.getLogger(__name__)

@celery_app.task(bind=True, name="app.tasks.smart_alert_tasks.check_smart_alerts")
def check_smart_alerts(self):
    """
    Check for alerts using smart triggering logic
    Runs every 15 minutes
    """
    import asyncio
    
    async def _check_smart_alerts():
        try:
            logger.info("Starting smart alert checking task")
            
            db = SessionLocal()
            try:
                # Initialize smart alert service
                smart_alert_service = SmartAlertService(db)
                
                # Check alerts with smart logic
                stats = await smart_alert_service.check_smart_alerts()
                
                logger.info(f"Smart alert checking completed: {stats}")
                
                return {
                    "status": "completed",
                    "stats": stats
                }
                
            finally:
                db.close()
            
        except Exception as e:
            logger.error(f"Error in smart alert checking task: {str(e)}")
            if hasattr(self, 'update_state'):
                self.update_state(
                    state="FAILURE",
                    meta={"error": str(e)}
                )
            raise
    
    # Run the async function
    return asyncio.run(_check_smart_alerts())
