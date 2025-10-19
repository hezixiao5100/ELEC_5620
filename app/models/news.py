"""
News Model
"""
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

# TODO: Import Base from database
# from app.database import Base

# TODO: Define News model
# class News(Base):
#     __tablename__ = "news"
#     
#     id = Column(Integer, primary_key=True, index=True)
#     stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False)
#     title = Column(String(255), nullable=False)
#     content = Column(Text, nullable=True)
#     source = Column(String(100), nullable=True)
#     published_at = Column(DateTime, nullable=False, index=True)
#     sentiment_score = Column(Float, nullable=True)  # -1.0 to 1.0
#     relevance_score = Column(Float, nullable=True)  # 0.0 to 1.0
#     created_at = Column(DateTime, default=datetime.utcnow)
#     
#     # Relationships
#     # stock = relationship("Stock", back_populates="news")


