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
    title = " ".join(words[:10]).strip(" .,:;!?-")
    return title or "Untitled"

async def generate_session_title(messages: List[str]) -> str:
    """
    Gọi GROQ để sinh tiêu đề (~10 từ). Nếu lỗi -> fallback đơn giản.
    messages: list các nội dung (ưu tiên 1-5 message đầu).
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return _simple_title_fallback(messages)

    prompt = (
        "Dưới đây là một đoạn hội thoại giữa người dùng và trợ lý AI trong lĩnh vực pháp luật.\n"
        "Hãy tạo MỘT tiêu đề ngắn gọn, tiếng Việt, khoảng 8–12 từ, phản ánh đúng nội dung trao đổi.\n"
        "Không dùng ngoặc kép, không thêm dấu chấm cuối dòng.\n"
        "Tiêu đề cần rõ ràng, súc tích, phù hợp để người dùng dễ tìm lại nội dung về sau.\n\n"
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
                    "max_tokens": 24,
                    "temperature": 0.4,
                },
            )
        resp.raise_for_status()
        data = resp.json()
        title = (data["choices"][0]["message"]["content"] or "").strip()

        title = title.strip(" \"'“”‘’")
        words = title.split()
        if len(words) > 12:
            title = " ".join(words[:12])
        if len(title) > 80:
            title = title[:80].rstrip()
        return title or _simple_title_fallback(messages)
    except Exception:
        return _simple_title_fallback(messages)
