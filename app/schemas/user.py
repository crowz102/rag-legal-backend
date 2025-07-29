from pydantic import BaseModel, EmailStr, Field, StringConstraints
from app.schemas.enums import UserRole
from typing import Optional, Annotated

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class User(BaseModel):
    username: str
    email: EmailStr
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
    password: str = Field(min_lenght=6)

class UserOut(User):
    id: int
    is_active: bool

class UserUpdate(BaseModel):
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
