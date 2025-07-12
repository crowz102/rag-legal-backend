from pydantic import BaseModel

class User(BaseModel):
    username: str
    role: str

class UserInDB(User):
    hashed_password: str
