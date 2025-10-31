"""
Monitoring Tasks
System monitoring and health check tasks
"""
from celery import current_task
from app.celery_app import celery_app
from app.database import get_db_session
from app.services.monitoring_service import MonitoringService
from app.services.alert_service import AlertService
from app.agents.agent_manager import AgentManager
from app.core.logging import get_logger
import time

logger = get_logger("monitoring_tasks")

@celery_app.task(bind=True, name="app.tasks.monitoring_tasks.monitor_stock_prices")
def monitor_stock_prices(self):
    """
    Monitor stock prices and check for alerts
    Runs every 15 minutes
    """
    try:
        logger.info("Starting stock price monitoring task")
        
        with get_db_session() as db:
            # Initialize services
            monitoring_service = MonitoringService()
            alert_service = AlertService(db)
            
            # Get all tracked stocks
            tracked_stocks = monitoring_service.get_all_tracked_stocks()
            logger.info(f"Monitoring {len(tracked_stocks)} tracked stocks")
            
            # Check each tracked stock
            alerts_triggered = 0
            for tracked_stock in tracked_stocks:
                try:
                    # Get current price
                    current_price = monitoring_service.get_current_price(tracked_stock.stock.symbol)
                    
                    if current_price:
                        # Check for price alerts
                        triggered_alerts = alert_service.check_price_alerts(
                            user_id=tracked_stock.user_id,
                            stock_id=tracked_stock.stock_id,
                            current_price=current_price
                        )
                        
                        alerts_triggered += len(triggered_alerts)
                        
                        # Update task progress
                        self.update_state(
                            state="PROGRESS",
                            meta={
                                "current": tracked_stock.stock.symbol,
                                "price": current_price,
                                "alerts": alerts_triggered
                            }
                        )
                        
                except Exception as e:
                    logger.error(f"Error monitoring {tracked_stock.stock.symbol}: {str(e)}")
                    continue
            
            logger.info(f"Monitoring completed. {alerts_triggered} alerts triggered")
            
            return {
                "status": "completed",
                "stocks_monitored": len(tracked_stocks),
                "alerts_triggered": alerts_triggered,
                "message": "Stock monitoring completed successfully"
            }
            
    except Exception as e:
        logger.error(f"Stock monitoring task failed: {str(e)}")
        self.update_state(
            state="FAILURE",
            meta={"error": str(e)}
        )
        raise

@celery_app.task(bind=True, name="app.tasks.monitoring_tasks.monitor_market_conditions")
def monitor_market_conditions(self):
    """
    Monitor overall market conditions
    Runs every hour
    """
    try:
        logger.info("Starting market conditions monitoring")
        
        with get_db_session() as db:
            # Initialize services
            monitoring_service = MonitoringService()
            agent_manager = AgentManager(db)
            
            # Get market overview
            market_data = monitoring_service.get_market_overview()
            
            # Analyze market sentiment
            sentiment_analysis = monitoring_service.analyze_market_sentiment()
            
            # Update task progress
            self.update_state(
                state="PROGRESS",
                meta={
                    "market_condition": market_data.get("condition", "unknown"),
                    "sentiment_score": sentiment_analysis.get("score", 0),
                    "volatility": market_data.get("volatility", 0)
                }
            )
            
            logger.info("Market conditions monitoring completed")
            
            return {
                "status": "completed",
                "market_condition": market_data.get("condition"),
                "sentiment_score": sentiment_analysis.get("score"),
                "volatility": market_data.get("volatility"),
                "message": "Market monitoring completed successfully"
            }
            
    except Exception as e:
        logger.error(f"Market monitoring task failed: {str(e)}")
        self.update_state(
            state="FAILURE",
            meta={"error": str(e)}
        )
        raise

@celery_app.task(bind=True, name="app.tasks.monitoring_tasks.health_check")
def health_check(self):
    """
    System health check
    Runs every 5 minutes
    """
    try:
        logger.info("Starting system health check")
        
        with get_db_session() as db:
            # Check database connection
            from sqlalchemy import text
            db.execute(text("SELECT 1"))
            db_status = "healthy"
        
        # Check external APIs (simplified)
        api_status = "healthy"  # In production, check actual API endpoints
        
        # Update task progress
        self.update_state(
            state="PROGRESS",
            meta={
                "database": db_status,
                "apis": api_status,
                "timestamp": "now"
            }
        )
        
        overall_status = "healthy" if db_status == "healthy" and api_status == "healthy" else "unhealthy"
        
        logger.info(f"Health check completed: {overall_status}")
        return {
            "status": "completed",
            "overall_health": overall_status,
            "database": db_status,
            "apis": api_status,
            "message": f"System health check completed: {overall_status}"
        }
    except Exception as e:
        logger.error(f"Health check task failed: {str(e)}", exc_info=True)
        self.update_state(
            state="FAILURE",
            meta={"error": str(e)}
        )
        raise

@celery_app.task(bind=True, name="app.tasks.monitoring_tasks.collect_system_metrics")
def collect_system_metrics(self):
    """
    Collect system performance metrics
    Runs every 5 minutes
    """
    try:
        logger.info("Starting system metrics collection")
        
        with get_db_session() as db:
            monitoring_service = MonitoringService()
            
            # Get system metrics
            system_metrics = monitoring_service.system_monitor.get_system_metrics()
            
            # Get performance summary
            performance_summary = monitoring_service.system_monitor.get_performance_summary()
            
            # Update task progress
            self.update_state(
                state="PROGRESS",
                meta={
                    "cpu_percent": system_metrics["cpu"]["percent"],
                    "memory_percent": system_metrics["memory"]["percent"],
                    "disk_percent": system_metrics["disk"]["percent"]
                }
            )
            
            logger.info(f"System metrics collected: CPU {system_metrics['cpu']['percent']}%, Memory {system_metrics['memory']['percent']}%")
            
            return {
                "status": "completed",
                "cpu_percent": system_metrics["cpu"]["percent"],
                "memory_percent": system_metrics["memory"]["percent"],
                "disk_percent": system_metrics["disk"]["percent"],
                "performance_summary": performance_summary,
                "message": "System metrics collection completed successfully"
            }
            
    except Exception as e:
        logger.error(f"System metrics collection failed: {str(e)}")
        self.update_state(
            state="FAILURE",
            meta={"error": str(e)}
        )
        raise

@celery_app.task(bind=True, name="app.tasks.monitoring_tasks.collect_database_metrics")
def collect_database_metrics(self):
    """
    Collect database performance metrics
    Runs every 10 minutes
    """
    try:
        logger.info("Starting database metrics collection")
        
        with get_db_session() as db:
            monitoring_service = MonitoringService()
            
            # Get database metrics
            db_metrics = monitoring_service.database_monitor.get_database_metrics()
            
            # Update task progress
            self.update_state(
                state="PROGRESS",
                meta={
                    "pool_size": db_metrics["connection_pool"]["pool_size"],
                    "checked_out": db_metrics["connection_pool"]["checked_out"],
                    "db_size_mb": db_metrics["database_size"]["size_mb"]
                }
            )
            
            logger.info(f"Database metrics collected: Pool {db_metrics['connection_pool']['checked_out']}/{db_metrics['connection_pool']['pool_size']}")
            
            return {
                "status": "completed",
                "connection_pool": db_metrics["connection_pool"],
                "database_size": db_metrics["database_size"],
                "table_statistics": db_metrics["table_statistics"],
                "message": "Database metrics collection completed successfully"
            }
            
    except Exception as e:
        logger.error(f"Database metrics collection failed: {str(e)}")
        self.update_state(
            state="FAILURE",
            meta={"error": str(e)}
        )
        raise

@celery_app.task(bind=True, name="app.tasks.monitoring_tasks.collect_business_metrics")
def collect_business_metrics(self):
    """
    Collect business metrics
    Runs every 15 minutes
    """
    try:
        logger.info("Starting business metrics collection")
        
        with get_db_session() as db:
            monitoring_service = MonitoringService()
            
            # Get business metrics
            business_metrics = monitoring_service.business_monitor.get_business_metrics()
            
            # Update task progress
            self.update_state(
                state="PROGRESS",
                meta={
                    "users": business_metrics["users"]["total"],
                    "stocks": business_metrics["stocks"]["total"],
                    "alerts": business_metrics["alerts"]["total"]
                }
            )
            
            logger.info(f"Business metrics collected: {business_metrics['users']['total']} users, {business_metrics['stocks']['total']} stocks")
            
            return {
                "status": "completed",
                "users": business_metrics["users"],
                "stocks": business_metrics["stocks"],
                "alerts": business_metrics["alerts"],
                "reports": business_metrics["reports"],
                "message": "Business metrics collection completed successfully"
            }
            
    except Exception as e:
        logger.error(f"Business metrics collection failed: {str(e)}")
        self.update_state(
            state="FAILURE",
            meta={"error": str(e)}
        )
        raise

@celery_app.task(bind=True, name="app.tasks.monitoring_tasks.check_system_health")
def check_system_health(self):
    """
    Check overall system health
    Runs every 2 minutes
    """
    try:
        logger.info("Starting system health check")
        
        with get_db_session() as db:
            monitoring_service = MonitoringService()
            
            # Get health status
            health_status = monitoring_service.get_health_status()
            
            # Update task progress
            self.update_state(
                state="PROGRESS",
                meta={
                    "status": health_status["status"],
                    "issues_count": len(health_status.get("issues", [])),
                    "cpu_percent": health_status.get("system", {}).get("cpu_percent", 0),
                    "memory_percent": health_status.get("system", {}).get("memory_percent", 0)
                }
            )
            
            # Log health issues if any
            if health_status["status"] != "healthy":
                logger.warning(f"System health issues detected: {health_status.get('issues', [])}")
            else:
                logger.info("System health check passed")
            
            return {
                "status": "completed",
                "health_status": health_status["status"],
                "issues": health_status.get("issues", []),
                "system_metrics": health_status.get("system", {}),
                "message": f"System health check completed: {health_status['status']}"
            }
            
    except Exception as e:
        logger.error(f"System health check failed: {str(e)}")
        self.update_state(
            state="FAILURE",
            meta={"error": str(e)}
        )
        raise

@celery_app.task(bind=True, name="app.tasks.monitoring_tasks.generate_monitoring_report")
def generate_monitoring_report(self):
    """
    Generate comprehensive monitoring report
    Runs every hour
    """
    try:
        logger.info("Starting monitoring report generation")
        
        with get_db_session() as db:
            monitoring_service = MonitoringService()
            
            # Get comprehensive metrics
            comprehensive_metrics = monitoring_service.get_comprehensive_metrics()
            
            # Get health status
            health_status = monitoring_service.get_health_status()
            
            # Update task progress
            self.update_state(
                state="PROGRESS",
                meta={
                    "system_status": health_status["status"],
                    "cpu_percent": comprehensive_metrics["system"]["cpu"]["percent"],
                    "memory_percent": comprehensive_metrics["system"]["memory"]["percent"],
                    "users": comprehensive_metrics["business"]["users"]["total"]
                }
            )
            
            logger.info("Monitoring report generated successfully")
            
            return {
                "status": "completed",
                "report_timestamp": comprehensive_metrics["timestamp"],
                "health_status": health_status,
                "system_metrics": comprehensive_metrics["system"],
                "database_metrics": comprehensive_metrics["database"],
                "business_metrics": comprehensive_metrics["business"],
                "message": "Monitoring report generated successfully"
            }
            
    except Exception as e:
        logger.error(f"Monitoring report generation failed: {str(e)}")
        self.update_state(
            state="FAILURE",
            meta={"error": str(e)}
        )
        raise

@celery_app.task(bind=True, name="app.tasks.monitoring_tasks.cleanup_old_metrics")
def cleanup_old_metrics(self):
    """
    Cleanup old monitoring metrics
    Runs daily at 2 AM
    """
    try:
        logger.info("Starting old metrics cleanup")
        
        # This would typically clean up old metrics from a time-series database
        # For now, we'll just clean up the in-memory metrics history
        monitoring_service = MonitoringService()
        
        # Keep only last 24 hours of metrics
        old_count = len(monitoring_service.system_monitor.metrics_history)
        monitoring_service.system_monitor.metrics_history = monitoring_service.system_monitor.get_metrics_history(24)
        cleaned_count = old_count - len(monitoring_service.system_monitor.metrics_history)
        
        logger.info(f"Cleaned up {cleaned_count} old metrics entries")
        
        return {
            "status": "completed",
            "cleaned_entries": cleaned_count,
            "remaining_entries": len(monitoring_service.system_monitor.metrics_history),
            "message": f"Cleaned up {cleaned_count} old metrics entries"
        }
        
    except Exception as e:
        logger.error(f"Old metrics cleanup failed: {str(e)}")
        self.update_state(
            state="FAILURE",
            meta={"error": str(e)}
        )
        raise