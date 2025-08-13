from datetime import datetime
import httpx
from sqlalchemy.orm import Session
from app.core.config import get_settings
from app.core.celery_app import celery_app
from app.database import SessionLocal
from app.models.chat import ChatMessage

settings = get_settings()

@celery_app.task(bind=True, name="app.tasks.chat.call_ai", queue="celery", max_retries=3)
def call_ai_task(self, payload: dict):
    session_id = payload["session_id"]
    question = payload["question"]
    chat_history = payload.get("chat_history", [])

    def fetch():
        with httpx.Client(timeout=60.0) as client:
            print(f"[call_ai_task] calling AI_API_URL={settings.AI_API_URL} | session={session_id}")
            resp = client.post(settings.AI_API_URL, json={
                "question": question,
                "chat_history": chat_history
            })
            resp.raise_for_status()
            return resp.json()

    try:
        result = fetch()

        db: Session = SessionLocal()
        try:
            bot_msg = ChatMessage(
                session_id=session_id,
                sender="bot",
                content=result.get("answer", ""),
                timestamp=datetime.utcnow()
            )
            db.add(bot_msg)
            db.commit()
            print(f"[call_ai_task] saved bot message for session={session_id}")
        except Exception as db_err:
            print(f"[call_ai_task] DB ERROR: {db_err}")
            db.rollback()
            raise  # Re-raise để Celery retry nếu cần
        finally:
            db.close()

        return result

    except Exception as e:
        print(f"[call_ai_task] ERROR: {e}")
        raise self.retry(exc=e, countdown=5)