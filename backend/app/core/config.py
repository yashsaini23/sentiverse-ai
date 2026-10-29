from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=True, extra="ignore")

    PROJECT_NAME: str = "SentiVerse AI API"
    VERSION: str = "2.1.0"
    ENVIRONMENT: str = "development"
    SECRET_KEY: str | None = None

    REDIS_URL: str = "redis://localhost:6379/0"
    CHROMA_DB_DIR: str = "./data/chroma"
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMOTION_MODEL: str = "SamLowe/roberta-base-go_emotions"
    OPENAI_API_KEY: str | None = None
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_TIMEOUT_SECONDS: float = 20.0
    TMDB_API_KEY: str | None = None
    RAWG_API_KEY: str | None = None
    GOOGLE_BOOKS_API_KEY: str | None = None
    RATE_LIMIT_PER_MINUTE: int = 15
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
