from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "SentiVerse AI API"
    VERSION: str = "2.1.0"
    ENVIRONMENT: str = "development"

    DATABASE_URL: str = "postgresql://user:password@localhost:5432/sentiverse"
    REDIS_URL: str = "redis://localhost:6379/0"
    CHROMA_DB_DIR: str = "./chroma_data"

    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    EMOTION_MODEL: str = "SamLowe/roberta-base-go_emotions"
    OPENAI_MODEL: str = "gpt-4o-mini"

    # Comma-separated origins; use explicit domains in production.
    CORS_ORIGINS: str = "http://localhost:3000"

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
