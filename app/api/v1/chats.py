from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import httpx
import traceback

from app.core.config import get_settings  
settings = get_settings()

router = APIRouter(prefix="/chats", tags=["Chats"])

# ==== Schemas ====

class ChatHistoryItem(BaseModel):
    role: str 
    content: str

class QueryInput(BaseModel):
    question: str
    chat_history: List[ChatHistoryItem] = []

class SourceItem(BaseModel):
    source: str
    preview: str

class RAGResponse(BaseModel):
    answer: str
    sources: Optional[List[SourceItem]] = None


@router.post("/query", response_model=RAGResponse)
async def query_rag(payload: QueryInput):
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(settings.AI_API_URL, json=payload.dict())
        response.raise_for_status()

        try:
            data = response.json()
        except Exception:
            print("❌ Không parse được JSON từ AI backend:\n", traceback.format_exc())
            raise HTTPException(status_code=500, detail="Không đọc được dữ liệu trả về từ AI backend")

        print("✅ AI response JSON:", data)

        try:
            return RAGResponse(**data)
        except Exception:
            print("❌ Lỗi khi parse dữ liệu thành RAGResponse:\n", traceback.format_exc())
            raise HTTPException(status_code=500, detail="Dữ liệu trả về không đúng định dạng mong đợi")

    except httpx.HTTPStatusError as http_err:
        print("❌ HTTP status error:\n", traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Lỗi từ AI backend (status {http_err.response.status_code})")

    except Exception as e:
        print("❌ Lỗi không xác định khi gọi AI backend:\n", traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Lỗi khi gọi AI backend: {str(e)}")
