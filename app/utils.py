# app/utils.py
from typing import List
import os, re
import httpx
from groq import Groq

GROQ_API_URL = os.getenv("GROQ_API")
GROQ_MODEL = os.getenv("GROQ_MODEL", "qwen/qwen3-32b") 

def _simple_title_fallback(messages: List[str]) -> str:
    text = " ".join(messages)[:200]
    text = re.sub(r"\[(.*?)\]\((.*?)\)", r"\1", text)
    text = re.sub(r"\s+", " ", text).strip()
    words = text.split()
    title = " ".join(words[:8]).strip(" .,:;!?-")
    return title or "Untitled"

async def generate_session_title(messages: List[str]) -> str:
    """
    Gọi GROQ để sinh tiêu đề (< 8 từ). Nếu lỗi -> fallback đơn giản.
    messages: list các nội dung (ưu tiên 1-3 message đầu).
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return _simple_title_fallback(messages)

    prompt = (
        "Dưới đây là đoạn hội thoại giữa người dùng và trợ lý AI.\n"
        "Hãy tạo MỘT tiêu đề ngắn gọn, tự nhiên, tiếng Việt, tối đa 8 từ, "
        "không dùng ngoặc kép, không thêm dấu chấm cuối.\n\n"
        f"Nội dung:\n{chr(10).join(messages[:5])}\n\n"
        "Tiêu đề:"
    )

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(
                GROQ_API_URL,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": GROQ_MODEL,
                    "messages": [
                        {"role": "system", "content": "Bạn là AI chuyên đặt tiêu đề ngắn gọn cho hội thoại."},
                        {"role": "user", "content": prompt},
                    ],
                    "max_tokens": 16,
                    "temperature": 0.4,
                },
            )
        resp.raise_for_status()
        data = resp.json()
        title = (data["choices"][0]["message"]["content"] or "").strip()

        title = title.strip(" \"'“”‘’")
        words = title.split()
        if len(words) > 8:
            title = " ".join(words[:8])
        if len(title) > 60:
            title = title[:60].rstrip()
        return title or _simple_title_fallback(messages)
    except Exception:
        return _simple_title_fallback(messages)
