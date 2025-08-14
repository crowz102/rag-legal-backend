from app.core.celery_app import celery_app
from app.database import SessionLocal
from app.models.document import Document, DocumentStatus
from app.services.content_service import parse_file_content

import traceback
import time

@celery_app.task(bind=True, name="app.tasks.document_tasks.process_document_task", max_retries=3)
def process_document_task(self, file_path: str, document_id: int):
    """
    Xử lý file upload (parse nội dung, cập nhật DB).
    """
    db = None
    try:
        start_time = time.time()
        print(f"[DEBUG] Starting process_document_task for document {document_id} at {start_time}")

        content = parse_file_content(file_path)
        print(f"[DEBUG] Parsed content for document {document_id}, length: {len(content) if content else 0}")

        db = SessionLocal()
        doc = db.query(Document).filter(Document.id == document_id).first()
        if not doc:
            print(f"[DEBUG] Document {document_id} not found in database")
            return {"status": "skipped", "reason": "Document not found", "document_id": document_id}

        print(f"[DEBUG] Document {document_id} current status: {doc.status}")
        print(f"[DEBUG] Available DocumentStatus values: {[member for member in DocumentStatus.__members__]}")

        if hasattr(doc, "parsed_content"):
            doc.parsed_content = content
            print(f"[DEBUG] Updated parsed_content for document {document_id}")
        else:
            print(f"[DEBUG] Document {document_id} does not have parsed_content attribute")

        print(f"[DEBUG] Document {document_id} status remains: {doc.status}")

        db.commit()
        print(f"[DEBUG] Committed document {document_id} to database, elapsed time: {time.time() - start_time}s")

        db.refresh(doc)
        print(f"[DEBUG] Document {document_id} status after commit: {doc.status}")

        return {"status": "processed", "document_id": document_id}

    except Exception as e:
        print(f"[ERROR] Lỗi xử lý document {document_id}: {traceback.format_exc()}")
        raise self.retry(exc=e, countdown=10)

    finally:
        if db:
            db.close()
            print(f"[DEBUG] Closed database session for document {document_id}")