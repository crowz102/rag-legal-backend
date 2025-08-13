# app/tasks/document_tasks.py
from app.core.celery_app import celery_app

@celery_app.task(bind=True, name="app.tasks.document_tasks.process_document_task", max_retries=3)
def process_document_task(self, file_path: str, document_id: int):
    """
    Xử lý file upload (parse nội dung, cập nhật DB).
    """
    import traceback
    from app.database import SessionLocal
    from app.models.document import Document, DocumentStatus
    from app.services.content_service import parse_file_content

    db = None
    try:
        content = parse_file_content(file_path)

        db = SessionLocal()
        doc = db.query(Document).filter(Document.id == document_id).first()
        if not doc:
            return {"status": "skipped", "reason": "Document not found", "document_id": document_id}

        if hasattr(doc, "parsed_content"):
            doc.parsed_content = content

        if hasattr(DocumentStatus, "processed"):
            doc.status = DocumentStatus.processed
        else:
            doc.status = DocumentStatus.approved  # fallback

        db.commit()
        return {"status": "processed", "document_id": document_id}

    except Exception as e:
        print("❌ Lỗi xử lý document:", traceback.format_exc())
        raise self.retry(exc=e, countdown=10)

    finally:
        if db:
            db.close()
