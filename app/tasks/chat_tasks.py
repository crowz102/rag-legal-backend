from datetime import datetime
import httpx, traceback
from sqlalchemy.orm import Session
from celery.exceptions import MaxRetriesExceededError

from app.core.config import get_settings
from app.core.celery_app import celery_app
from app.database import SessionLocal
from app.models.chat import ChatMessage

settings = get_settings()

# ===== Helper internal =====
def _fetch_ai(payload: dict) -> dict:
    """Gọi AI API trực tiếp (có timeout)."""
    session_id = payload["session_id"]
    question = payload["question"]
    chat_history = payload.get("chat_history", [])

    try:
        # Có thể để timeout=None nếu muốn chờ vô hạn,
        # nhưng nên giới hạn (ví dụ 120s) để tránh treo worker
        with httpx.Client(timeout=120.0) as client:
            print(f"[_fetch_ai] calling AI_API_URL={settings.AI_API_URL} | session={session_id}")
            resp = client.post(settings.AI_API_URL, json={
                "question": question,
                "chat_history": chat_history
            })
            resp.raise_for_status()
            return resp.json()
    except Exception as e:
        raise RuntimeError(f"_fetch_ai failed: {e}")


# ===== Tasks độc lập (có thể test riêng) =====
@celery_app.task(bind=True, name="app.tasks.chat.fetch_ai", max_retries=3, default_retry_delay=5)
def fetch_ai_task(self, payload: dict):
    """Task chỉ gọi AI, có retry/backoff."""
    try:
        return _fetch_ai(payload)
    except Exception as exc:
        try:
            delay = (self.request.retries + 1) * 10  # backoff 10s, 20s, 30s
            raise self.retry(exc=exc, countdown=delay)
        except MaxRetriesExceededError:
            return {
                "error": "AI service unavailable after multiple retries. Please try again later.",
                "detail": str(exc),
                "trace": traceback.format_exc()
            }


@celery_app.task(bind=True, name="app.tasks.chat.save_message", max_retries=3, default_retry_delay=5)
def save_message_task(self, session_id: str, answer: str):
    """Task lưu tin nhắn bot vào DB."""
    db: Session = SessionLocal()
    try:
        bot_msg = ChatMessage(
            session_id=session_id,
            sender="bot",
            content=answer,
            timestamp=datetime.utcnow()
        )
        db.add(bot_msg)
        db.commit()
        print(f"[save_message_task] saved bot message for session={session_id}")
        return {"status": "success"}
    except Exception as db_err:
        print(f"[save_message_task] DB ERROR: {db_err}")
        db.rollback()
        raise self.retry(exc=db_err)
    finally:
        db.close()


# ===== Orchestrator (FE chỉ gọi cái này) =====
@celery_app.task(bind=True, name="app.tasks.chat.call_ai", queue="celery")
def call_ai_task(self, payload: dict):
    """Task orchestrator: gọi AI + lưu DB."""
    session_id = payload["session_id"]

    # 1) Gọi AI trực tiếp thay vì gọi task con sync
    try:
        result = _fetch_ai(payload)
    except Exception as e:
        print(f"[call_ai_task] _fetch_ai failed: {e}")
        return {"error": "AI service unavailable, please try later."}

    # 2) Lưu DB nếu có câu trả lời
    if isinstance(result, dict) and "answer" in result:
        db: Session = SessionLocal()
        try:
            bot_msg = ChatMessage(
                session_id=session_id,
                sender="bot",
                content=result["answer"],
                timestamp=datetime.utcnow()
            )
            db.add(bot_msg)
            db.commit()
            print(f"[call_ai_task] saved bot message for session={session_id}")
        except Exception as db_err:
            print(f"[call_ai_task] DB ERROR: {db_err}")
            db.rollback()
        finally:
            db.close()

    # 3) Trả kết quả về FE
    return result
