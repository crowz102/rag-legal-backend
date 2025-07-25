from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class SourceDocument(BaseModel):
    source: str                
    preview: str                    

class AnswerResponse(BaseModel):
    answer: str                     
    sources: Optional[List[SourceDocument]] = None 

class Message(BaseModel):
    role: str                       
    content: str
    timestamp: datetime

class ChatHistoryResponse(BaseModel):
    chat_id: str
    history: List[Message]
    created_at: datetime
    updated_at: datetime
    user_id: str

class QueryRequest(BaseModel):
    chat_id: str                   
    input: str                    
