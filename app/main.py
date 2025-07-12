from fastapi import FastAPI
from app.core.config import get_settings

app = FastAPI()

@app.get("/ping")
def ping():
    settings = get_settings()
    return {
        "app_name": settings.APP_NAME,
        "secret_key_preview": settings.SECRET_KEY[:5] + "*****",
        "token_expiry": settings.ACCESS_TOKEN_EXPIRE_MINUTES
    }
