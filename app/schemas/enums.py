from enum import Enum
from pydantic import BaseModel
from typing import Optional

class UserRole(str, Enum):
    admin = "admin"
    reviewer = "reviewer"
    uploader = "uploader"

class UserUpdate(BaseModel):
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None

class UserStatus(str, Enum):
    active = "active"
    inactive = "inactive"
    pending = "pending"
    banned = "banned"


