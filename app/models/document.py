from sqlalchemy import Column, Integer, String, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.database import Base
from sqlalchemy.dialects.postgresql import BYTEA
import enum

class DocumentStatus(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    uploader_id = Column(Integer, ForeignKey("users.id"))
    reviewer_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    filename = Column(String, nullable=False)
    file_content = Column(BYTEA, nullable=True)
    status = Column(Enum(DocumentStatus), default=DocumentStatus.pending)
    type = Column(String, nullable=True)
    issuer_agency = Column(String, nullable=True)
    document_type = Column(String, nullable=True)

    uploader = relationship("User", foreign_keys=[uploader_id])
    reviewer = relationship("User", foreign_keys=[reviewer_id])