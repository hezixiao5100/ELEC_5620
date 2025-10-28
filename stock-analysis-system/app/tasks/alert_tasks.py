"""
Alert Tasks
Price alert checking and notification tasks
"""
from celery import current_task
from app.celery_app import celery_app
from app.database import SessionLocal
from app.services.alert_service import AlertService
from app.services.monitoring_service import MonitoringService
from app.models.alert import Alert as AlertModel
from app.models.tracked_stock import TrackedStock as TrackedStockModel
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

@celery_app.task(bind=True, name="app.tasks.alert_tasks.check_price_alerts")
def check_price_alerts(self):
    """
    Check for price alerts and trigger notifications
    Runs every 5 minutes
    """
    try:
        logger.info("Starting price alert checking task")
        
        db = SessionLocal()
        try:
            # Initialize services
            alert_service = AlertService(db)
            monitoring_service = MonitoringService()
            
            # Get all pending alerts (including acknowledged ones that might need re-triggering)
            pending_alerts = db.query(AlertModel).filter(
                AlertModel.status.in_(["PENDING", "ACKNOWLEDGED"])
            ).all()
            
            logger.info(f"Checking {len(pending_alerts)} pending alerts")
            
            alerts_triggered = 0
            alerts_checked = 0
            
            for i, alert in enumerate(pending_alerts):
                try:
                    # Update task progress
                    if hasattr(self, 'update_state'):
                        self.update_state(
                            state="PROGRESS",
                            meta={
                                "current_alert": f"{alert.stock.symbol} - {alert.alert_type}",
                                "progress": f"{i+1}/{len(pending_alerts)}",
                                "triggered": alerts_triggered,
                                "checked": alerts_checked
                            }
                        )
                    
                    # Get current price
                    import asyncio
                    current_price = asyncio.run(monitoring_service.get_current_price(alert.stock.symbol))
                    
                    if not current_price:
                        logger.warning(f"Could not get current price for {alert.stock.symbol}")
                        alerts_checked += 1
                        continue
                    
                    # Get baseline price from tracked stock
                    from app.models.tracked_stock import TrackedStock as TrackedStockModel
                    tracked_stock = db.query(TrackedStockModel).filter(
                        TrackedStockModel.user_id == alert.user_id,
                        TrackedStockModel.stock_id == alert.stock_id,
                        TrackedStockModel.is_active == "Y"
                    ).first()
                    
                    if not tracked_stock or not tracked_stock.baseline_price:
                        logger.warning(f"No baseline price found for {alert.stock.symbol}, using current price")
                        # If no baseline, set it to current price
                        if tracked_stock:
                            tracked_stock.baseline_price = current_price
                            db.commit()
                        alerts_checked += 1
                        continue
                    
                    # Calculate cumulative price change from baseline
                    baseline_price = tracked_stock.baseline_price
                    price_change_percent = ((current_price - baseline_price) / baseline_price) * 100
                    
                    logger.info(f"{alert.stock.symbol}: Current=${current_price:.2f}, Baseline=${baseline_price:.2f}, Change={price_change_percent:.2f}%, Threshold={alert.threshold_value}%")
                    
                    # Check if alert should be triggered
                    should_trigger = False
                    
                    if alert.alert_type == "PRICE_DROP":
                        # Check if cumulative price dropped below threshold (negative change)
                        if price_change_percent <= alert.threshold_value:
                            should_trigger = True
                            logger.info(f"Price drop condition met for {alert.stock.symbol}: {price_change_percent:.2f}% <= {alert.threshold_value}%")
                    
                    elif alert.alert_type == "PRICE_SPIKE":
                        # Check if cumulative price increased above threshold (positive change)
                        if price_change_percent >= alert.threshold_value:
                            should_trigger = True
                            logger.info(f"Price spike condition met for {alert.stock.symbol}: {price_change_percent:.2f}% >= {alert.threshold_value}%")
                    
                    elif alert.alert_type == "VOLATILITY":
                        # Check volatility (simplified - would need historical data)
                        # For now, just check if price changed significantly
                        if alert.current_value:
                            price_change = abs(current_price - alert.current_value) / alert.current_value
                            if price_change >= abs(alert.threshold_value) / 100:
                                should_trigger = True
                    
                    elif alert.alert_type == "VOLUME_ANOMALY":
                        # Check volume anomaly (would need volume data)
                        # For now, skip volume checks
                        pass
                    
                    # Cumulative trigger mechanism: count how many times condition is met
                    # Do NOT reset count when condition is not met - this makes it robust against price fluctuations
                    
                    if should_trigger:
                        # Increment cumulative trigger count
                        alert.trigger_count = (alert.trigger_count or 0) + 1
                        
                        # Record trigger event in history
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
                        
                        logger.info(f"Alert condition met for {alert.stock.symbol}: trigger_count={alert.trigger_count}/{alert.required_triggers}")
                        
                        # Check if we've reached the required trigger threshold
                        if alert.trigger_count >= alert.required_triggers:
                            # Trigger the alert based on current status
                            try:
                                if alert.status == "ACKNOWLEDGED":
                                    # If alert was previously acknowledged, reset to PENDING
                                    # This creates a "new" alert experience for the user
                                    alert.status = "PENDING"
                                    alert.current_value = current_price
                                    alert.message = f"Alert re-triggered: {alert.stock.symbol} price is ${current_price:.2f} ({price_change_percent:.2f}% from baseline ${baseline_price:.2f}). Triggered {alert.trigger_count} times."
                                    alert.triggered_at = None  # Reset trigger time
                                    alert.acknowledged_at = None  # Reset acknowledge time
                                    alert.trigger_count = 0  # Reset trigger count for next cycle
                                    alert.trigger_history = []  # Clear history
                                    db.commit()
                                    alerts_triggered += 1
                                    logger.info(f"Alert reset to PENDING for {alert.stock.symbol} (was ACKNOWLEDGED)")
                                else:
                                    # For PENDING alerts, trigger normally
                                    asyncio.run(alert_service.trigger_alert(
                                        alert_id=alert.id,
                                        current_value=current_price,
                                        message=f"Alert triggered: {alert.stock.symbol} price is ${current_price:.2f} ({price_change_percent:.2f}% from baseline ${baseline_price:.2f}). Triggered {alert.trigger_count} times."
                                    ))
                                    alert.trigger_count = 0  # Reset trigger count after successful trigger
                                    alert.trigger_history = []  # Clear history
                                    alerts_triggered += 1
                                    logger.info(f"Alert triggered for {alert.stock.symbol}")
                            except Exception as e:
                                logger.warning(f"Failed to trigger alert for {alert.stock.symbol}: {str(e)}")
                    # Note: We do NOT reset trigger_count when condition is not met
                    # This allows the system to accumulate evidence of a trend
                    # Only reset when: 1) Alert is TRIGGERED, or 2) User ACKNOWLEDGES
                    
                    # Update current value for next check
                    alert.current_value = current_price
                    alerts_checked += 1
                    
                except Exception as e:
                    logger.error(f"Error checking alert {alert.id}: {str(e)}")
                    alerts_checked += 1
                    continue
            
            # Commit changes
            db.commit()
            
            logger.info(f"Price alert checking completed. Triggered: {alerts_triggered}, Checked: {alerts_checked}")
            
            return {
                "status": "completed",
                "alerts_checked": alerts_checked,
                "alerts_triggered": alerts_triggered,
                "message": "Price alert checking completed successfully"
            }
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Price alert checking task failed: {str(e)}")
        if hasattr(self, 'update_state'):
            self.update_state(
                state="FAILURE",
                meta={"error": str(e)}
            )
        raise

@celery_app.task(bind=True, name="app.tasks.alert_tasks.send_alert_notifications")
def send_alert_notifications(self):
    """
    Send notifications for triggered alerts
    Runs every 10 minutes
    """
    try:
        logger.info("Starting alert notification task")
        
        db = SessionLocal()
        try:
            # Initialize services
            alert_service = AlertService(db)
            
            # Get triggered alerts that haven't been acknowledged
            triggered_alerts = db.query(AlertModel).filter(
                AlertModel.status == "TRIGGERED"
            ).all()
            
            logger.info(f"Processing {len(triggered_alerts)} triggered alerts")
            
            notifications_sent = 0
            failed_notifications = 0
            
            for i, alert in enumerate(triggered_alerts):
                try:
                    # Update task progress
                    if hasattr(self, 'update_state'):
                        self.update_state(
                            state="PROGRESS",
                            meta={
                                "current_alert": f"{alert.stock.symbol} - {alert.alert_type}",
                                "progress": f"{i+1}/{len(triggered_alerts)}",
                                "sent": notifications_sent,
                                "failed": failed_notifications
                            }
                        )
                    
                    # Send notification (simplified - in production would use email/SMS/push)
                    notification_sent = alert_service.send_alert_notification(
                        alert_id=alert.id,
                        user_id=alert.user_id,
                        message=alert.message
                    )
                    
                    if notification_sent:
                        notifications_sent += 1
                        logger.info(f"Notification sent for alert {alert.id}")
                    else:
                        failed_notifications += 1
                        logger.warning(f"Failed to send notification for alert {alert.id}")
                    
                except Exception as e:
                    failed_notifications += 1
                    logger.error(f"Error sending notification for alert {alert.id}: {str(e)}")
                    continue
            
            logger.info(f"Alert notification task completed. Sent: {notifications_sent}, Failed: {failed_notifications}")
            
            return {
                "status": "completed",
                "notifications_sent": notifications_sent,
                "failed_notifications": failed_notifications,
                "message": "Alert notification task completed successfully"
            }
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Alert notification task failed: {str(e)}")
        if hasattr(self, 'update_state'):
            self.update_state(
                state="FAILURE",
                meta={"error": str(e)}
            )
        raise

@celery_app.task(bind=True, name="app.tasks.alert_tasks.cleanup_expired_alerts")
def cleanup_expired_alerts(self):
    """
    Clean up expired alerts
    Runs daily at midnight
    """
    try:
        logger.info("Starting expired alert cleanup task")
        
        db = SessionLocal()
        try:
            # Initialize services
            alert_service = AlertService(db)
            
            # Get alerts that are older than 7 days and still pending
            from datetime import timedelta
            cutoff_date = datetime.utcnow() - timedelta(days=7)
            
            expired_alerts = db.query(AlertModel).filter(
                AlertModel.created_at < cutoff_date,
                AlertModel.status == "PENDING"
            ).all()
            
            logger.info(f"Found {len(expired_alerts)} expired alerts to cleanup")
            
            expired_count = 0
            
            for alert in expired_alerts:
                try:
                    # Mark alert as expired
                    alert.status = "EXPIRED"
                    expired_count += 1
                    logger.info(f"Marked alert {alert.id} as expired")
                    
                except Exception as e:
                    logger.error(f"Error expiring alert {alert.id}: {str(e)}")
                    continue
            
            # Commit changes
            db.commit()
            
            logger.info(f"Expired alert cleanup completed. Expired: {expired_count}")
            
            return {
                "status": "completed",
                "expired_alerts": expired_count,
                "message": "Expired alert cleanup completed successfully"
            }
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Expired alert cleanup task failed: {str(e)}")
        if hasattr(self, 'update_state'):
            self.update_state(
                state="FAILURE",
                meta={"error": str(e)}
            )
        raise


