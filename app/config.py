from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    anthropic_api_key: str | None = None
    openai_api_key: str | None = None
    chat_provider: Literal["openai", "anthropic"] = "openai"
    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_database: str = "abc"
    mongodb_collection: str = "chatbot_test"
    openai_model: str = "gpt-4o-mini"
    anthropic_model: str = "claude-haiku-4-5"
    chat_history_limit: int = Field(default=20, ge=1, le=100)
    system_prompt: str = "You are a helpful assistant."
    session_secret_key: str | None = Field(default=None, min_length=32)
    session_cookie_secure: bool = False
    session_max_age_seconds: int = Field(default=604800, ge=300, le=2592000)
