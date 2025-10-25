#!/usr/bin/env python3
"""
Database Initialization Script
Run this script to create all database tables
"""
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import init_db, engine
from app.config import settings

def main():
    """Initialize the database with all tables"""
    print("🚀 Initializing database...")
    print(f"Database URL: {settings.DATABASE_URL}")
    
    try:
        # Create all tables
        init_db()
        print("✅ Database tables created successfully!")
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute("SELECT 1")
            print("✅ Database connection test successful!")
            
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

