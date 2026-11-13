from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://qa:qa_password@postgres:5432/qa"
    redis_url: str = "redis://redis:6379/0"
    cache_ttl_seconds: int = 3600
    retention_days: int = 30
    app_name: str = "Q&A API"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
