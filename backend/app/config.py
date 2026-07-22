"""Application settings loaded from environment variables."""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Typed application configuration.

    Values are read from the environment (and a local `.env` file if present).
    Only the fields needed for Week 1 are required; the rest are placeholders
    that later weeks (AI provider, payments, web3) will start using.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Core
    app_env: str = "local"
    log_level: str = "info"

    # Database (PostgreSQL + pgvector; self-hosted / Docker)
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/great_energy_field"
    database_url_sync: str = (
        "postgresql+psycopg://postgres:postgres@localhost:5432/great_energy_field"
    )

    # Auth (FastAPI-native JWT; the backend both issues and verifies tokens)
    jwt_secret_key: str = "dev-insecure-change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440

    # CORS: comma-separated origins
    cors_origins: str = "http://localhost:3000"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance."""
    return Settings()
