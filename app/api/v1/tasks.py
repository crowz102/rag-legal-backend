from fastapi import APIRouter
from celery.result import AsyncResult
from app.core.celery_app import celery_app

router = APIRouter(prefix="/tasks", tags=["Tasks"])

@router.get("/{task_id}")
def get_task_status(task_id: str):
    res = AsyncResult(task_id, app=celery_app)

    # Khi orchestrator trả về lỗi theo dạng dict {"error": "..."}
    if res.status == "SUCCESS" and isinstance(res.result, dict):
        answer = res.result.get("answer")
        error = res.result.get("error")
        return {
            "task_id": task_id,
            "status": res.status,
            "answer": answer,
            "error": error
        }

    return {
        "task_id": task_id,
        "status": res.status
    }
