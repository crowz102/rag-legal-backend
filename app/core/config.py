from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional

class Settings(BaseSettings):
    # App metadata
    APP_NAME: str = "RAG Legal Backend"
    APP_HOST: str = "127.0.0.1"
    APP_PORT: int = 8000

    # Database
    DATABASE_URL: Optional[str] = None 

    #AI API
    AI_API_URL: str

    # SUMMARY TILTE API
    GROQ_API: str

    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    CHAT_MAX_SYNC_WORDS: int 
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

@lru_cache()
def get_settings():
    return Settings()


