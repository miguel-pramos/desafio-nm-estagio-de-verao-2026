from functools import lru_cache
from typing import Annotated, Literal

from fastapi import Depends
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Environment Configuration
    ENV: Literal["development", "production"] = "development"

    # CORS Configuration
    FRONTEND_URL: str = "http://localhost:3000"

    # Auth Configuration
    GITHUB_CLIENT_ID: str = "github-client-id"
    GITHUB_CLIENT_SECRET: str = "github-client-secret"
    JWT_SECRET: str = "jwt-secret"

    # Database Configuration
    DATABASE_URL: str = "postgresql+psycopg2://user:pass@host:5432/dbname"

    # AI Configuration
    OPENAI_API_KEY: str = "sk-****"
    OPENAI_BASE_URL: str = "https://openai-compatible-ai-provider-base-url"
    OPENAI_MODEL: str = "model-name"

    # RAG / ingestion settings
    # Provide a comma-separated list of URLs to ingest on startup, or leave blank.
    INGEST_BASE_URL: str = "https://www.comvest.unicamp.br/wp-content/uploads/2025/09/RESOLUCAO-GR-25-Retificacao.pdf"
    # When true, the app will attempt to ingest INGEST_URLS on FastAPI startup.
    INGEST_ON_STARTUP: bool = True
    # If true, force ingestion even if a chroma DB already exists.
    INGEST_FORCE: bool = False


@lru_cache
def get_settings() -> Settings:
    return Settings()


SettingsDep = Annotated[Settings, Depends(get_settings)]
