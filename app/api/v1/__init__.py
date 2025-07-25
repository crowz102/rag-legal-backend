from fastapi import APIRouter
from . import auth, users

router = APIRouter()
router.include_router(auth.router, prefix="/auth")
router.include_router(users.router)
