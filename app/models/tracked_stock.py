"""
Tracked Stock Model (Association Table)
"""
from sqlalchemy import Column, Integer, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime

# TODO: Import Base from database
# from app.database import Base

# TODO: Define TrackedStock model
# class TrackedStock(Base):
#     __tablename__ = "tracked_stocks"
#     
#     id = Column(Integer, primary_key=True, index=True)
#     user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
#     stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False)
#     created_at = Column(DateTime, default=datetime.utcnow)
#     
#     # Relationships
#     # user = relationship("User", back_populates="tracked_stocks")
#     # stock = relationship("Stock", back_populates="tracked_by")
#     
#     # Ensure a user can only track a stock once
#     __table_args__ = (
#         UniqueConstraint('user_id', 'stock_id', name='uq_user_stock'),
#     )


