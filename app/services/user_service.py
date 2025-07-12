from typing import Optional
from app.schemas.user import UserInDB
from app.core.security import get_password_hash

_fake_users_db = {
    "admin": {
        "username": "admin",
        "hashed_password": get_password_hash("admin123"),
        "role": "admin"
    }
}

def get_user_by_username(username: str) -> Optional[UserInDB]:
    user = _fake_users_db.get(username)
    if user:
        return UserInDB(**user)
    return None
