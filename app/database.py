"""
Database Connection and Session Management
Optimized for production use with connection pooling and transaction management
"""
from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from contextlib import contextmanager
from typing import Generator
import logging

from app.config import settings
from app.core.logging import get_logger

logger = get_logger("database")

# Create database engine with optimized connection pooling
engine = create_engine(
    settings.DATABASE_URL,
    # Connection pool settings
    poolclass=QueuePool,
    pool_size=20,  # Number of connections to maintain in pool
    max_overflow=30,  # Additional connections that can be created
    pool_pre_ping=True,  # Validate connections before use
    pool_recycle=3600,  # Recycle connections every hour
    pool_timeout=30,  # Timeout for getting connection from pool
    
    # Performance settings
    echo=settings.DEBUG,  # Show SQL queries in debug mode
    echo_pool=settings.DEBUG,  # Show pool events in debug mode
    
    # Connection settings
    connect_args={
        "charset": "utf8mb4",
        "autocommit": False,
    }
)

# Create SessionLocal class with optimized settings
SessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine,
    expire_on_commit=False  # Keep objects accessible after commit
)

# Create Base class for models
Base = declarative_base()

# Add connection pool event listeners for monitoring
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Set database connection parameters"""
    if "mysql" in str(engine.url):
        with dbapi_connection.cursor() as cursor:
            cursor.execute("SET SESSION sql_mode = 'STRICT_TRANS_TABLES,NO_ZERO_DATE,NO_ZERO_IN_DATE,ERROR_FOR_DIVISION_BY_ZERO'")
            cursor.execute("SET SESSION time_zone = '+00:00'")

@event.listens_for(engine, "checkout")
def receive_checkout(dbapi_connection, connection_record, connection_proxy):
    """Log when a connection is checked out from the pool"""
    logger.debug("Connection checked out from pool")

@event.listens_for(engine, "checkin")
def receive_checkin(dbapi_connection, connection_record):
    """Log when a connection is checked in to the pool"""
    logger.debug("Connection checked in to pool")

def get_db() -> Generator[Session, None, None]:
    """
    Dependency function to get database session with proper error handling
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

@contextmanager
def get_db_session():
    """
    Context manager for database sessions with automatic transaction handling
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        logger.error(f"Database transaction error: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

@contextmanager
def get_db_session_readonly():
    """
    Context manager for read-only database sessions
    """
    db = SessionLocal()
    try:
        # Set session to read-only mode
        from sqlalchemy import text
        db.execute(text("SET SESSION TRANSACTION READ ONLY"))
        yield db
    except Exception as e:
        logger.error(f"Read-only database session error: {str(e)}")
        raise
    finally:
        db.close()

def init_db():
    """
    Initialize database tables with proper error handling
    """
    try:
        logger.info("Initializing database tables...")
        
        # Import all models to register them
        from app.models import user, stock, stock_data, tracked_stock, alert, report, news
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        logger.info("Database tables initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        raise

def get_connection_pool_status():
    """
    Get current connection pool status for monitoring
    """
    pool = engine.pool
    return {
        "pool_size": pool.size(),
        "checked_in": pool.checkedin(),
        "checked_out": pool.checkedout(),
        "overflow": pool.overflow(),
        "invalid": 0,  # QueuePool doesn't have invalid() method
    }




