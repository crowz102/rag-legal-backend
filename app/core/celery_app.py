from celery import Celery
from app.core.config import get_settings

settings = get_settings()

BROKER_URL = getattr(settings, "CELERY_BROKER_URL", None) or "amqp://guest:guest@localhost:5672//"
RESULT_BACKEND = getattr(settings, "CELERY_RESULT_BACKEND", None) or "redis://localhost:6379/0"

print(f"[Celery] broker={BROKER_URL} backend={RESULT_BACKEND}")

celery_app = Celery(
    "rag_legal_backend",
    broker=BROKER_URL,
    backend=RESULT_BACKEND,
)

celery_app.autodiscover_tasks(["app.tasks"])

celery_app.conf.update(
    task_track_started=True,
    result_expires=3600,
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="Asia/Ho_Chi_Minh",
    task_default_queue="celery",
    worker_hijack_root_logger=False,
    task_always_eager=False,
    worker_send_task_events=True, 
    task_send_sent_event=True,     
)