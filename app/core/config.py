from pydantic_settings import BaseSettings 
from functools import lru_cache

class Settings(BaseSettings):
    APP_NAME: str = "RAG Legal Backend"
    APP_HOST: str = "127.0.0.1"
    APP_PORT: int = 8000

    DATABASE_URL: str = "" 
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
