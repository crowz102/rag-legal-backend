from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
import httpx, traceback
from datetime import datetime

from app.core.config import get_settings
from app.database import get_db
from app.models.chat import ChatSession, ChatMessage
from app.models.user import User
from app.core.dependencies import get_current_user

from app.schemas.chat import ChatSessionSummary

settings = get_settings()
router = APIRouter(prefix="/chat", tags=["Chats"])

# ==== Schemas ====

class ChatHistoryItem(BaseModel):
    role: str 
    content: str

class QueryInput(BaseModel):
    question: str
    chat_history: List[ChatHistoryItem] = []

class RAGResponse(BaseModel):
    answer: str

class ChatMessageCreate(BaseModel):
    session_id: Optional[int] = None
    content: str

class ChatMessageResponse(BaseModel):
    session_id: int
    sender: str
    content: str
    timestamp: datetime

class FullChatMessage(BaseModel):
    sender: str
    content: str
    timestamp: datetime

# ==== AI Backend Call ====

async def call_rag_backend(payload: QueryInput) -> RAGResponse:
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(settings.AI_API_URL, json=payload.dict())
        response.raise_for_status()
        data = response.json()
        return RAGResponse(**data)
    except Exception:
        print("❌ Lỗi khi gọi AI backend:\n", traceback.format_exc())
        raise HTTPException(status_code=500, detail="Lỗi kết nối AI backend")

# ==== POST /chat/ - Gửi tin nhắn và lưu DB + gọi AI ====

@router.post("/", response_model=ChatMessageResponse)
async def chat(
    message_in: ChatMessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Nếu chưa có session_id thì tạo session mới
    if not message_in.session_id:
        session = ChatSession(user_id=current_user.id, title="Untitled")
        db.add(session)
        db.commit()
        db.refresh(session)
    else:
        session = db.query(ChatSession).filter_by(id=message_in.session_id, user_id=current_user.id).first()
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

    # Lưu tin nhắn người dùng
    user_msg = ChatMessage(
        session_id=session.id,
        sender="user",
        content=message_in.content,
        timestamp=datetime.utcnow()
    )
    db.add(user_msg)
    db.commit()
    db.refresh(user_msg)

    # Gọi AI
    rag_input = QueryInput(question=message_in.content)
    rag_response = await call_rag_backend(rag_input)

    # Lưu tin nhắn bot
    bot_msg = ChatMessage(
        session_id=session.id,
        sender="bot",
        content=rag_response.answer,
        timestamp=datetime.utcnow()
    )
    db.add(bot_msg)
    db.commit()
    db.refresh(bot_msg)

    return ChatMessageResponse(
        session_id=session.id,
        sender="bot",
        content=bot_msg.content,
        timestamp=bot_msg.timestamp
    )

@router.get("/sessions", response_model=List[ChatSessionSummary])
def list_chat_sessions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    sessions = db.query(ChatSession)\
        .filter_by(user_id=current_user.id)\
        .order_by(ChatSession.updated_at.desc())\
        .all()
    
    return sessions

# ==== GET /chat/session/{session_id} - Lấy toàn bộ tin nhắn ====

@router.get("/session/{session_id}", response_model=List[FullChatMessage])
async def get_chat_history(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    session = db.query(ChatSession).filter_by(id=session_id, user_id=current_user.id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    messages = db.query(ChatMessage)\
        .filter_by(session_id=session_id)\
        .order_by(ChatMessage.timestamp.asc())\
        .all()

    return [
        FullChatMessage(
            sender=msg.sender,
            content=msg.content,
            timestamp=msg.timestamp
        ) for msg in messages
    ]


