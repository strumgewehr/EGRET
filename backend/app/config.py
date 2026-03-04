"""
Application configuration via environment variables.
No secrets hardcoded; all loaded from env.
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Central config - validates and loads from .env."""

    # Database
    database_url: str = "postgresql://nsi_user:nsi_secure_password@localhost:5432/news_sentiment_db"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Security
    secret_key: str = "change-me-in-production"
    cors_origins: str = "http://localhost:3000"

    # Optional HuggingFace (improves rate limits for gated models)
    huggingface_token: str | None = None

    # Rate limiting
    rate_limit_requests: int = 100
    rate_limit_window_seconds: int = 60

    # Ingestion
    default_fetch_limit_per_source: int = 50
    duplicate_similarity_threshold: float = 0.85

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    return Settings()
