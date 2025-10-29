"""
Chat Pydantic Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class ChatMessageRequest(BaseModel):
    """聊天消息请求"""
    message: str = Field(..., description="用户输入的消息")
    session_id: str = Field(..., description="会话 ID")


class ChatMessageResponse(BaseModel):
    """聊天消息响应"""
    role: str = Field(..., description="消息角色：user/assistant")
    content: str = Field(..., description="消息内容")
    function_name: Optional[str] = Field(None, description="调用的函数名")
    function_args: Optional[Dict[str, Any]] = Field(None, description="函数参数")
    metadata: Optional[Dict[str, Any]] = Field(None, description="额外元数据")
    created_at: datetime = Field(..., description="创建时间")
    
    class Config:
        from_attributes = True


class ChatSessionResponse(BaseModel):
    """会话响应"""
    session_id: str
    message_count: int
    last_message_at: Optional[datetime]
    first_message_at: Optional[datetime]


class ChatHistoryResponse(BaseModel):
    """会话历史响应"""
    session_id: str
    messages: List[ChatMessageResponse]
    
    class Config:
        from_attributes = True


class StreamChunk(BaseModel):
    """流式响应数据块"""
    content: Optional[str] = None
    function_call: Optional[Dict[str, Any]] = None
    done: bool = False
    error: Optional[str] = None

