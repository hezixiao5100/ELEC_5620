"""
User Model
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

# TODO: Import Base from database
# from app.database import Base

class UserRole(str, enum.Enum):
    """User role enumeration"""
    INVESTOR = "investor"
    ADVISOR = "advisor"
    ADMIN = "admin"

# TODO: Define User model
# class User(Base):
#     __tablename__ = "users"
#     
#     id = Column(Integer, primary_key=True, index=True)
#     username = Column(String(50), unique=True, index=True, nullable=False)
#     email = Column(String(100), unique=True, index=True, nullable=False)
#     password_hash = Column(String(255), nullable=False)
#     role = Column(Enum(UserRole), default=UserRole.INVESTOR, nullable=False)
#     alert_threshold = Column(Float, default=-5.0)  # Default -5% drop threshold
#     created_at = Column(DateTime, default=datetime.utcnow)
#     last_login = Column(DateTime, nullable=True)
#     
#     # Relationships
#     # tracked_stocks = relationship("TrackedStock", back_populates="user")
#     # alerts = relationship("Alert", back_populates="user")
#     # reports = relationship("Report", back_populates="user")


