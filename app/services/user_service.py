from sqlalchemy.orm import Session
from typing import Optional

from app.models import User

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()