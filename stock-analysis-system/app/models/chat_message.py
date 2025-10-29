"""
Chat Message Model
存储 AI 聊天历史记录
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base


class MessageRole(str, enum.Enum):
    """消息角色"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    FUNCTION = "function"


class ChatMessage(Base):
    """聊天消息模型"""
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_id = Column(String(100), nullable=False, index=True)  # 会话 ID
    role = Column(Enum(MessageRole), nullable=False)
    content = Column(Text, nullable=False)  # 消息内容
    
    # Function call 相关
    function_name = Column(String(100), nullable=True)  # 调用的函数名
    function_args = Column(JSON, nullable=True)  # 函数参数
    function_result = Column(JSON, nullable=True)  # 函数返回结果
    
    # 额外元数据
    extra_data = Column(JSON, nullable=True)  # 如图表数据、建议等（不能用 metadata，这是保留字）
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # 关系
    user = relationship("User", back_populates="chat_messages")
    
    def __repr__(self):
        return f"<ChatMessage(id={self.id}, role={self.role}, session={self.session_id})>"

