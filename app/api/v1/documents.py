from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.document import Document, DocumentStatus

from app.schemas.document import DocumentOut
from app.core.dependencies import get_current_user
from app.models.user import User
from typing import List
from app.services.content_service import parse_file_content, convert_doc_to_pdf

import os, tempfile, mimetypes
from pathlib import Path
from app.core.celery_app import celery_app
from app.tasks.document_tasks import process_document_task

router = APIRouter(prefix="/documents", tags=["Documents"])

UPLOAD_DIR = os.path.join("rag-legal-backend", "uploads")


# -------------------- DEPENDENCIES -------------------- #
def is_uploader(user: User = Depends(get_current_user)):
    if not user or not user.role or user.role.name.lower() != "uploader":
        raise HTTPException(status_code=403, detail="Uploaders only")
    return user


def is_reviewer(user: User = Depends(get_current_user)):
    if not user or not user.role or user.role.name.lower() != "reviewer":
        raise HTTPException(status_code=403, detail="Reviewers only")
    return user


# -------------------- UPLOAD -------------------- #
@router.post("/upload", response_model=DocumentOut)
def upload_document(
    file: UploadFile = File(...),
    issuer_agency: str = Form(...),
    document_type: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    file_content = file.file.read(MAX_FILE_SIZE + 1)
    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File size exceeds 10MB limit")

    new_doc = Document(
        uploader_id=current_user.id,
        filename=file.filename,
        type=os.path.splitext(file.filename)[1],
        file_content=file_content if len(file_content) <= MAX_FILE_SIZE else None,
        issuer_agency=issuer_agency,
        document_type=document_type,
        status=DocumentStatus.pending,
    )
    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)

    temp_file_path = os.path.join(tempfile.gettempdir(), f"{new_doc.id}_{file.filename}")
    with open(temp_file_path, "wb") as f:
        f.write(file_content)

    # Gửi task xử lý document
    process_document_task.delay(temp_file_path, new_doc.id)

    return new_doc


# -------------------- PENDING -------------------- #
@router.get("/pending", response_model=List[DocumentOut])
def get_pending_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(is_reviewer),
):
    return db.query(Document).filter(Document.status == DocumentStatus.pending).all()


# -------------------- PREVIEW -------------------- #
@router.get("/{doc_id}/preview")
async def preview_document(
    doc_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(is_reviewer),
):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    file_content = doc.file_content
    if not file_content:
        raise HTTPException(status_code=404, detail="File content not found")

    temp_file_path = tempfile.NamedTemporaryFile(delete=False, suffix=doc.type).name
    converted_path = None
    try:
        with open(temp_file_path, 'wb') as temp_file:
            temp_file.write(file_content)
            temp_file.flush()
            os.fsync(temp_file.fileno())

        if doc.type.lower() == ".doc":
            converted_path = convert_doc_to_pdf(Path(temp_file_path))
            if not converted_path or not converted_path.exists():
                raise HTTPException(status_code=500, detail="Could not convert .doc to PDF")
            file_path = converted_path
        else:
            file_path = temp_file_path

        if not os.path.exists(file_path):
            raise HTTPException(status_code=500, detail=f"File not found at {file_path} before sending")

        mime_type, _ = mimetypes.guess_type(file_path)
        if not mime_type:
            mime_type = "application/octet-stream"

        async def cleanup():
            for path in [temp_file_path, converted_path]:
                if path and os.path.exists(path):
                    os.unlink(path)

        return FileResponse(
            path=file_path,
            filename=doc.filename,
            media_type=mime_type,
            background=cleanup
        )

    except Exception as e:
        for path in [temp_file_path, converted_path]:
            if path and os.path.exists(path):
                os.unlink(path)
        raise


# -------------------- APPROVE -------------------- #
@router.put("/{doc_id}/approve", response_model=DocumentOut)
def approve_document(
    doc_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(is_reviewer),
):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc or doc.status != DocumentStatus.pending:
        raise HTTPException(status_code=404, detail="Document not found or not pending")

    # Debug
    print(f"[DEBUG] Approving document {doc.id} by reviewer {current_user.id} ({current_user.role.name})")

    doc.status = DocumentStatus.approved
    doc.reviewer_id = current_user.id

    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


# -------------------- REJECT -------------------- #
@router.put("/{doc_id}/reject", response_model=DocumentOut)
def reject_document(
    doc_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(is_reviewer),
):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc or doc.status != DocumentStatus.pending:
        raise HTTPException(status_code=404, detail="Document not found or not pending")

    # Debug
    print(f"[DEBUG] Rejecting document {doc.id} by reviewer {current_user.id} ({current_user.role.name})")

    doc.status = DocumentStatus.rejected
    doc.reviewer_id = current_user.id

    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc
