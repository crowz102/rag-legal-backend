from fastapi import APIRouter, Depends
from app.core.dependencies import require_role
from app.schemas.user import UserRole
from app.models.user import Role
from app.core.security import oauth2_scheme

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import models
from app.schemas.user import UserOut, UserUpdate
from app.database import get_db

from app.core.dependencies import require_role, require_admin
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/users", tags=["Admin"])

@router.get("/me")
def get_my_info(user = Depends(require_role(UserRole.admin, UserRole.reviewer, UserRole.uploader))):
    return {"msg": f"Hello, {user.username}! You are a(n) {user.role}."}

@router.get("/admin/protected")
def admin_only_route(user = Depends(require_role(UserRole.admin))):
    return {"msg": f"Welcome admin {user.username}!"}

# --------------------- CRUD User for Admin --------------------------------
@router.get("/", response_model=list[UserOut])
def read_users(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin),
):
    users = (
        db.query(models.User)
        .join(Role)
        .filter(Role.name != "admin")
        .all()
    )
    return [
        UserOut(
            id=u.id,
            username=u.username,
            fullname=u.fullname,
            phone=u.phone,
            email=u.email,
            role=UserRole(u.role.name.lower()),
            status=u.status.value
        )
        for u in users
    ]


@router.patch("/{user_id}", response_model=UserOut)
def update_user(
    user_id: int,
    update_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin),
):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.role.name.lower() == "admin":
        raise HTTPException(status_code=403, detail="Cannot modify admin account")

    if update_data.role:
        role_obj = db.query(Role).filter(Role.name == update_data.role.value).first()
        if not role_obj:
            raise HTTPException(status_code=400, detail="Invalid role")
        user.role = role_obj
    if update_data.status is not None:
        user.status = update_data.status

    db.commit()
    db.refresh(user)
    return UserOut(
        id=user.id,
        username=user.username,
        email=user.email,
        fullname=user.fullname,
        phone=user.phone,
        role=UserRole(user.role.name.lower()),
        status=user.status.value
    )


@router.delete("/{user_id}", status_code=204)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin),
):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.role.name.lower() == "admin":
        raise HTTPException(status_code=403, detail="Cannot delete admin account")

    db.delete(user)
    db.commit()
