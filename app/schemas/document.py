from pydantic import BaseModel
from typing import Optional
from enum import Enum

class DocumentStatus(str, Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"

class DocumentCreate(BaseModel):
    issuer_agency: str
    document_type: str

class DocumentOut(BaseModel):
    id: int
    uploader_id: int
    reviewer_id: Optional[int] 
    status: str
    type: str
    filename: str
    issuer_agency: str
    document_type: str

    class Config:
        orm_mode = True