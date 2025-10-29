"""
Chat API Endpoints
AI 分析助手的 API 接口
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List
import json
import logging
from datetime import datetime
import uuid

from app.database import get_db
from app.models.user import User
from app.models.chat_message import ChatMessage as ChatMessageModel, MessageRole
from app.schemas.chat import (
    ChatMessageRequest,
    ChatMessageResponse,
    ChatSessionResponse,
    ChatHistoryResponse
)
from app.services.ai.langchain_service import get_chat_service
from app.services.auth_service import get_current_active_user

logger = logging.getLogger(__name__)
router = APIRouter(tags=["AI Chat"])  # prefix 在 main.py 中已经设置为 /chat


@router.post("/message", response_model=ChatMessageResponse)
async def send_message(
    request: ChatMessageRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    发送消息给 AI（非流式）
    """
    try:
        chat_service = get_chat_service()
        
        # 保存用户消息
        user_message = ChatMessageModel(
            user_id=current_user.id,
            session_id=request.session_id,
            role=MessageRole.USER,
            content=request.message,
            created_at=datetime.utcnow()
        )
        db.add(user_message)
        db.commit()
        
        # 调用 LangChain Agent
        result = await chat_service.chat(
            user_input=request.message,
            session_id=request.session_id,
            user_id=current_user.id
        )
        
        if result["status"] == "error":
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("error", "Unknown error")
            )
        
        # 保存 AI 响应
        ai_message = ChatMessageModel(
            user_id=current_user.id,
            session_id=request.session_id,
            role=MessageRole.ASSISTANT,
            content=result["response"],
            extra_data={"intermediate_steps": result.get("intermediate_steps", [])},
            created_at=datetime.utcnow()
        )
        db.add(ai_message)
        db.commit()
        
        return ChatMessageResponse(
            role="assistant",
            content=result["response"],
            function_name=None,
            function_args=None,
            metadata={"intermediate_steps": result.get("intermediate_steps", [])},
            created_at=ai_message.created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Send message error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process message: {str(e)}"
        )


@router.post("/stream")
async def stream_message(
    request: ChatMessageRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    发送消息给 AI（流式响应 - Server-Sent Events）
    """
    try:
        chat_service = get_chat_service()
        
        # 保存用户消息
        user_message = ChatMessageModel(
            user_id=current_user.id,
            session_id=request.session_id,
            role=MessageRole.USER,
            content=request.message,
            created_at=datetime.utcnow()
        )
        db.add(user_message)
        db.commit()
        
        # 流式响应生成器
        async def event_generator():
            full_response = ""
            try:
                # 发送开始信号
                yield f"data: {json.dumps({'type': 'start', 'content': ''})}\n\n"
                
                # 流式获取响应
                async for chunk in chat_service.chat_stream(
                    user_input=request.message,
                    session_id=request.session_id,
                    user_id=current_user.id
                ):
                    full_response += chunk
                    yield f"data: {json.dumps({'type': 'content', 'content': chunk})}\n\n"
                
                # 保存完整的 AI 响应到数据库
                ai_message = ChatMessageModel(
                    user_id=current_user.id,
                    session_id=request.session_id,
                    role=MessageRole.ASSISTANT,
                    content=full_response,
                    created_at=datetime.utcnow()
                )
                db.add(ai_message)
                db.commit()
                
                # 发送完成信号
                yield f"data: {json.dumps({'type': 'done', 'content': ''})}\n\n"
                
            except Exception as e:
                logger.error(f"Stream error: {str(e)}")
                yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"
        
        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"  # 禁用 nginx 缓冲
            }
        )
        
    except Exception as e:
        logger.error(f"Stream message error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to stream message: {str(e)}"
        )


@router.get("/sessions", response_model=List[ChatSessionResponse])
async def get_sessions(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取用户的所有会话列表
    """
    try:
        # 查询用户的所有会话
        sessions = db.query(
            ChatMessageModel.session_id,
            db.func.count(ChatMessageModel.id).label("message_count"),
            db.func.max(ChatMessageModel.created_at).label("last_message_at"),
            db.func.min(ChatMessageModel.created_at).label("first_message_at")
        ).filter(
            ChatMessageModel.user_id == current_user.id
        ).group_by(
            ChatMessageModel.session_id
        ).order_by(
            db.func.max(ChatMessageModel.created_at).desc()
        ).all()
        
        return [
            ChatSessionResponse(
                session_id=s.session_id,
                message_count=s.message_count,
                last_message_at=s.last_message_at,
                first_message_at=s.first_message_at
            )
            for s in sessions
        ]
        
    except Exception as e:
        logger.error(f"Get sessions error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch sessions"
        )


@router.get("/sessions/{session_id}", response_model=ChatHistoryResponse)
async def get_session_history(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取指定会话的历史消息
    """
    try:
        messages = db.query(ChatMessageModel).filter(
            ChatMessageModel.user_id == current_user.id,
            ChatMessageModel.session_id == session_id
        ).order_by(
            ChatMessageModel.created_at.asc()
        ).all()
        
        return ChatHistoryResponse(
            session_id=session_id,
            messages=[
                ChatMessageResponse(
                    role=msg.role.value,
                    content=msg.content,
                    function_name=msg.function_name,
                    function_args=msg.function_args,
                    metadata=msg.extra_data,
                    created_at=msg.created_at
                )
                for msg in messages
            ]
        )
        
    except Exception as e:
        logger.error(f"Get session history error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch session history"
        )


@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    删除指定会话
    """
    try:
        # 删除数据库中的消息
        db.query(ChatMessageModel).filter(
            ChatMessageModel.user_id == current_user.id,
            ChatMessageModel.session_id == session_id
        ).delete()
        db.commit()
        
        # 清除内存中的会话历史
        chat_service = get_chat_service()
        chat_service.clear_session(session_id)
        
        return {"message": "Session deleted successfully"}
        
    except Exception as e:
        logger.error(f"Delete session error: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete session"
        )


@router.post("/sessions/new")
async def create_new_session(
    current_user: User = Depends(get_current_active_user)
):
    """
    创建新会话（返回新的 session_id）
    """
    session_id = f"session_{uuid.uuid4().hex[:16]}"
    return {"session_id": session_id}

