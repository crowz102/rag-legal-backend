from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# ----- Input -----
class ChatMessageCreate(BaseModel):
    session_id: Optional[int] = None
    content: str

class QueryRequest(BaseModel):
    chat_id: str 
    input: str

# ----- Output Message -----
class Message(BaseModel):
    role: str 
    content: str
    timestamp: datetime

class ChatMessageResponse(BaseModel):
    id: int
    session_id: int
    sender: str
    content: str
    timestamp: datetime

    class Config:
        orm_mode = True

# ----- Output Session -----
class ChatSessionCreate(BaseModel):
    title: Optional[str] = "Untitled session"

class ChatSessionResponse(BaseModel):
    id: int
    user_id: int
    title: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# ----- Full Chat History -----
class ChatHistoryResponse(BaseModel):
    chat_id: int
    history: List[Message]
    created_at: datetime
    updated_at: datetime
    user_id: int

class ChatSessionSummary(BaseModel):
    id: int
    title: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
