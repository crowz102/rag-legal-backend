from pydantic import BaseModel, EmailStr, Field
from app.schemas.enums import UserRole
from typing import Optional

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
    password: str = Field(min_lenght = 6)

class UserOut(User):
    id: int
    is_active: bool

class UserUpdate(BaseModel):
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
