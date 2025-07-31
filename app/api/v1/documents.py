from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.document import Document, DocumentStatus

from app.schemas.document import DocumentOut
from app.core.dependencies import get_current_user
from app.models.user import User
from typing import List

import os
import shutil
import uuid

router = APIRouter(prefix="/documents", tags=["Documents"])

UPLOAD_DIR = os.path.join("rag-legal-backend", "uploads")

def is_uploader(user: User = Depends(get_current_user)):
    if user.role.name.lower() != "uploader":
        raise HTTPException(status_code=403, detail="Uploaders only")
    return user

def is_reviewer(user: User = Depends(get_current_user)):
    if user.role.name.lower() != "reviewer":
        raise HTTPException(status_code=403, detail="Reviewers only")
    return user

@router.post("/upload", response_model=DocumentOut)
def upload_document(
    file: UploadFile = File(...),
    issuer_agency: str = Form(...),
    document_type: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    os.makedirs(UPLOAD_DIR, exist_ok=True) 

    file_ext = os.path.splitext(file.filename)[1]
    file_id = uuid.uuid4().hex
    saved_filename = f"{file_id}{file_ext}"
    saved_path = os.path.join(UPLOAD_DIR, saved_filename)

    print("🔍 Upload path:", saved_path)

    with open(saved_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    new_doc = Document(
        uploader_id=current_user.id,
        filename=file.filename,
        type=file_ext,
        doc_url=saved_path,
        issuer_agency=issuer_agency,
        document_type=document_type,
        status=DocumentStatus.pending
    )
    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)
    return new_doc

@router.get("/pending", response_model=List[DocumentOut])
def get_pending_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(is_reviewer),
):
    return db.query(Document).filter(Document.status == DocumentStatus.pending).all()

@router.get("/{doc_id}/preview")
def preview_document(
    doc_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(is_reviewer),  # chỉ reviewer mới xem
):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    file_path = doc.doc_url

    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="File not found on disk")

    return FileResponse(
        path=file_path,
        filename=doc.filename,
        media_type="application/pdf" if file_path.endswith(".pdf") else "application/octet-stream"
    )

@router.put("/{doc_id}/approve", response_model=DocumentOut)
def approve_document(
    doc_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(is_reviewer),
):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc or doc.status != DocumentStatus.pending:
        raise HTTPException(status_code=404, detail="Document not found or not pending")
    doc.status = DocumentStatus.approved
    doc.reviewer_id = current_user.id
    db.commit()
    db.refresh(doc)
    return doc

@router.put("/{doc_id}/reject", response_model=DocumentOut)
def reject_document(
    doc_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(is_reviewer),
):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc or doc.status != DocumentStatus.pending:
        raise HTTPException(status_code=404, detail="Document not found or not pending")
    doc.status = DocumentStatus.rejected
    doc.reviewer_id = current_user.id
    db.commit()
    db.refresh(doc)
    return doc
