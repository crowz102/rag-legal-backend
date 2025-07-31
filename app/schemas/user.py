from pydantic import BaseModel, EmailStr, Field, StringConstraints
from app.schemas.enums import UserRole
from typing import Optional, Annotated
import sys
import os

from app.schemas.enums import UserStatus

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class User(BaseModel):
    username: str
    email: EmailStr
    fullname: str
    phone: str
    role: UserRole | None = None

    class Config:
        use_enum_values = True
        orm_mode = True

class UserInDB(User):
    hashed_password: str

class UserCreate(BaseModel):
    email: EmailStr
    fullname: str
    phone: Optional[Annotated[str, StringConstraints(pattern=r'^\+\d{8,15}$')]] = None
    password: str = Field(min_length=6)
    status: Optional[UserStatus] = UserStatus.pending

class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    fullname: str
    phone: str
    role: UserRole | None = None
    status: UserStatus

    class Config:
        use_enum_values = True
        orm_mode = True

class UserUpdate(BaseModel):
    role: Optional[UserRole] = None
    status: Optional[UserStatus] = None 
