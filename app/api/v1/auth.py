from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import SessionLocal
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta

from app.schemas.auth import Token
from app.services.user_service import get_user_by_email
from app.core.security import verify_password, create_access_token, get_password_hash
from app.schemas.user import UserCreate
from app.models.user import User, Role

router = APIRouter(prefix="/auth", tags=["Auth"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    username = user.email.split("@")[0]

    existing_user = db.query(User).filter(
        (User.email == user.email) | (User.username == username)
    ).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email hoặc username đã được đăng ký")

    default_role = db.query(Role).filter(Role.name == "uploader").first()
    if not default_role:
        raise HTTPException(status_code=500, detail="Không tìm thấy role mặc định")

    hashed_pw = get_password_hash(user.password)
    new_user = User(
        username=username,
        hashed_password=hashed_pw,
        email=user.email,
        role_id=default_role.id
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "msg": "Đăng ký thành công",
        "email": new_user.email,
        "username": new_user.username
    }

@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    # form_data.username thực chất chứa email
    user = get_user_by_email(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    access_token = create_access_token(
        data={"sub": user.email, "role": user.role.name},
        expires_delta=timedelta(minutes=60)
    )
    return {"access_token": access_token, "token_type": "bearer"}
