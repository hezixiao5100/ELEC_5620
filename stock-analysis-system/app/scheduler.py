"""
Background Task Scheduler using APScheduler
Simple and reliable alternative to Celery
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime
import logging

from app.database import SessionLocal
from app.services.alert_service import AlertService
from app.services.monitoring_service import MonitoringService
from app.models.alert import Alert as AlertModel
from app.models.tracked_stock import TrackedStock as TrackedStockModel

logger = logging.getLogger(__name__)

# Global scheduler instance
scheduler = AsyncIOScheduler()


async def check_price_alerts():
    """
    Check for price alerts and update trigger counts
    Runs every 1 minute
    """
    try:
        logger.info("🔥 Starting price alert check with cumulative trigger_count logic")
        
        db = SessionLocal()
        try:
            # Initialize services
            alert_service = AlertService(db)
            monitoring_service = MonitoringService()
            
            # Get all pending/acknowledged alerts
            alerts = db.query(AlertModel).filter(
                AlertModel.status.in_(["pending", "acknowledged"])
            ).all()
            
            logger.info(f"Checking {len(alerts)} alerts")
            
            alerts_checked = 0
            alerts_triggered = 0
            
            for alert in alerts:
                try:
                    # Get tracked stock info
                    tracked_stock = db.query(TrackedStockModel).filter(
                        TrackedStockModel.user_id == alert.user_id,
                        TrackedStockModel.stock_id == alert.stock_id,
                        TrackedStockModel.is_active == 'Y'
                    ).first()
                    
                    if not tracked_stock:
                        continue
                    
                    # Get current price
                    current_price = await monitoring_service.get_current_price(alert.stock.symbol)
                    if current_price is None:
                        logger.warning(f"Could not get price for {alert.stock.symbol}")
                        continue
                    
                    # Get baseline price
                    baseline_price = tracked_stock.baseline_price
                    if not baseline_price:
                        tracked_stock.baseline_price = current_price
                        db.commit()
                        continue
                    
                    # Calculate cumulative change from baseline
                    price_change_percent = ((current_price - baseline_price) / baseline_price) * 100
                    
                    logger.info(f"{alert.stock.symbol}: Current=${current_price:.2f}, Baseline=${baseline_price:.2f}, Change={price_change_percent:.2f}%, Threshold={alert.threshold_value}%")
                    
                    # Check if alert should be triggered
                    should_trigger = False
                    
                    if alert.alert_type.value == "price_drop":  # AlertType enum value is lowercase with underscore
                        if price_change_percent <= alert.threshold_value:
                            should_trigger = True
                            logger.info(f"✓ {alert.stock.symbol} meets condition: {price_change_percent:.2f}% <= {alert.threshold_value}%")
                    
                    if should_trigger:
                        # Increment trigger count
                        alert.trigger_count = (alert.trigger_count or 0) + 1
                        
                        # Record trigger event
                        import json
                        trigger_history = alert.trigger_history if alert.trigger_history else []
                        if isinstance(trigger_history, str):
                            trigger_history = json.loads(trigger_history)
                        
                        trigger_event = {
                            "timestamp": datetime.utcnow().isoformat(),
                            "price": float(current_price),
                            "change_percent": float(price_change_percent),
                            "baseline_price": float(baseline_price)
                        }
                        trigger_history.append(trigger_event)
                        alert.trigger_history = trigger_history
                        
                        logger.info(f"📊 {alert.stock.symbol} trigger_count: {alert.trigger_count}/{alert.required_triggers}")
                        
                        # Check if reached threshold
                        if alert.trigger_count >= alert.required_triggers:
                            if alert.status.value == "acknowledged":
                                # Reset to PENDING
                                alert.status = "pending"
                                alert.current_value = current_price
                                alert.message = f"Alert re-triggered: {alert.stock.symbol} price is ${current_price:.2f} ({price_change_percent:.2f}% from baseline)"
                                alert.triggered_at = None
                                alert.acknowledged_at = None
                                alert.trigger_count = 0
                                alert.trigger_history = []
                                alerts_triggered += 1
                                logger.info(f"🔔 Alert reset to PENDING for {alert.stock.symbol}")
                            else:
                                # Trigger alert
                                await alert_service.trigger_alert(
                                    alert_id=alert.id,
                                    current_value=current_price,
                                    message=f"Alert triggered: {alert.stock.symbol} price is ${current_price:.2f} ({price_change_percent:.2f}% from baseline)"
                                )
                                alert.trigger_count = 0
                                alert.trigger_history = []
                                alerts_triggered += 1
                                logger.info(f"🚨 Alert TRIGGERED for {alert.stock.symbol}")
                    
                    # Update current value
                    alert.current_value = current_price
                    
                    # IMPORTANT: Commit after each alert
                    db.commit()
                    
                    alerts_checked += 1
                    
                except Exception as e:
                    logger.error(f"Error checking alert for {alert.stock.symbol}: {str(e)}")
                    db.rollback()
                    continue
            
            logger.info(f"✅ Alert check completed: {alerts_checked} checked, {alerts_triggered} triggered")
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"❌ Error in check_price_alerts: {str(e)}", exc_info=True)


def start_scheduler():
    """Start the background scheduler"""
    try:
        # Add alert checking job (every 1 minute)
        scheduler.add_job(
            check_price_alerts,
            trigger=IntervalTrigger(minutes=1),
            id='check_price_alerts',
            name='Check price alerts',
            replace_existing=True
        )
        
        scheduler.start()
        logger.info("✅ APScheduler started successfully")
        
    except Exception as e:
        logger.error(f"❌ Failed to start scheduler: {str(e)}")


def stop_scheduler():
    """Stop the background scheduler"""
    try:
        if scheduler.running:
            scheduler.shutdown()
            logger.info("✅ APScheduler stopped successfully")
    except Exception as e:
        logger.error(f"❌ Error stopping scheduler: {str(e)}")

