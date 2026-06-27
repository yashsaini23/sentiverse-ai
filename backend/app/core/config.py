from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    PROJECT_NAME: str = "SentiVerse AI API"
    VERSION: str = "2.0.0"
    ENVIRONMENT: str = "development"
    
    # Storage & State
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/sentiverse"
    REDIS_URL: str = "redis://localhost:6379/0"
    CHROMA_DB_DIR: str = "/app/chroma_data"
    
    # Model Settings
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    EMOTION_MODEL: str = "SamLowe/roberta-base-go_emotions"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache
def get_settings():
    return Settings()

settings = get_settings()