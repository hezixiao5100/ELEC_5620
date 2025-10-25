"""
FastAPI Application Entry Point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth, stocks, portfolio, reports, alerts, admin, tasks, monitoring
from app.database import init_db
from app.config import settings
from app.core.error_handlers import setup_error_handlers
from app.core.logging import get_logger

app = FastAPI(
    title="Stock Analysis System",
    description="Intelligent stock analysis and alert system powered by AI agents",
    version="1.0.0"
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(stocks.router, prefix="/api/v1/stocks", tags=["Stocks"])
app.include_router(portfolio.router, prefix="/api/v1/portfolio", tags=["Portfolio"])
app.include_router(reports.router, prefix="/api/v1/reports", tags=["Reports"])
app.include_router(alerts.router, prefix="/api/v1/alerts", tags=["Alerts"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["Admin"])
app.include_router(tasks.router, prefix="/api/v1", tags=["Background Tasks"])
app.include_router(monitoring.router, prefix="/api/v1/monitoring", tags=["System Monitoring"])

# Setup error handlers
setup_error_handlers(app)

# Initialize logger
logger = get_logger("main")

@app.on_event("startup")
async def startup_event():
    """
    Application startup event
    """
    logger.info("Starting Stock Analysis System", extra={
        "version": "1.0.0",
        "environment": "development"
    })
    
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """
    Application shutdown event
    """
    print("🔄 Application shutting down...")

@app.get("/")
async def root():
    """
    Root endpoint
    """
    return {
        "message": "Welcome to Stock Analysis System API",
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    try:
        from sqlalchemy import text
        from app.database import SessionLocal
        
        # Check database connection
        db = SessionLocal()
        try:
            db.execute(text("SELECT 1"))
            db_status = "healthy"
        except Exception as e:
            db_status = f"unhealthy: {str(e)}"
        finally:
            db.close()
        
        # Check external APIs (simplified)
        api_status = "healthy"  # In production, check actual API endpoints
        
        overall_status = "healthy" if db_status == "healthy" and api_status == "healthy" else "unhealthy"
        
        return {
            "status": overall_status,
            "database": db_status,
            "apis": api_status,
            "timestamp": "2025-10-23T13:55:00Z"
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": "2025-10-23T13:55:00Z"
        }




