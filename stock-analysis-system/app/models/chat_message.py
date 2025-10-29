"""
Chat Message Model
Store AI chat history
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base


class MessageRole(str, enum.Enum):
    """Message role"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    FUNCTION = "function"


class ChatMessage(Base):
    """Chat message model"""
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_id = Column(String(100), nullable=False, index=True)  # Session ID
    role = Column(Enum(MessageRole), nullable=False)
    content = Column(Text, nullable=False)  # Message content
    
    # Function call related
    function_name = Column(String(100), nullable=True)  # Called function name
    function_args = Column(JSON, nullable=True)  # Function arguments
    function_result = Column(JSON, nullable=True)  # Function return result
    
    # Extra metadata (cannot use 'metadata' reserved by SQLAlchemy)
    extra_data = Column(JSON, nullable=True)  # e.g., chart data, recommendations
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationship
    user = relationship("User", back_populates="chat_messages")
    
    def __repr__(self):
        return f"<ChatMessage(id={self.id}, role={self.role}, session={self.session_id})>"

