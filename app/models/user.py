from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.database import Base
import enum
from app.schemas.enums import UserStatus

class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)

    users = relationship("User", back_populates="role")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    fullname = Column(String(100), nullable=False)
    phone = Column(String(50), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    status = Column(Enum(UserStatus), default=UserStatus.active)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)

    role = relationship("Role", back_populates="users")
    chat_sessions = relationship("ChatSession", back_populates="user", cascade="all, delete-orphan")
