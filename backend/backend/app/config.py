"""Application configuration loaded from environment variables."""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, PydanticBaseSettingsSource, SettingsConfigDict


def _get_env_file() -> str:
    """Locate the workspace root .env file even when the app runs from a subdirectory."""
    start = Path(__file__).resolve().parent
    for candidate in [start, *start.parents]:
        env_path = candidate / ".env"
        if env_path.exists():
            return str(env_path)
    return ".env"


class Settings(BaseSettings):
    """All secrets and user-specific details live in .env."""

    model_config = SettingsConfigDict(
        env_file=_get_env_file(),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls,
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            dotenv_settings,
            env_settings,
            file_secret_settings,
        )

    # App
    app_name: str = "Last Minute Life Saver"
    debug: bool = False
    api_v1_prefix: str = "/v1"

    # Database
    db_url: str = "sqlite:///./demo.db"

    # Redis
    redis_url: str = "redis://localhost:6379/0"
    redis_enabled: bool = False

    # Azure OpenAI / OpenAI
    openai_api_key: str = ""
    openai_api_base: str = ""
    openai_api_version: str = "2024-08-01-preview"
    openai_model: str = "gpt-4o"
    openai_temperature: float = 0.3
    openai_max_retries: int = 3
    llm_confidence_threshold: float = 0.7

    # User context
    user_email: str = "user@example.com"

    # Calendar
    calendar_provider: Literal["outlook", "google_calendar"] = "outlook"
    calendar_id: str = "primary"

    # OAuth2 - Microsoft Graph
    ms_client_id: str = ""
    ms_client_secret: str = ""
    ms_tenant_id: str = "common"
    ms_redirect_uri: str = "http://localhost:8000/v1/auth/callback/microsoft"

    # OAuth2 - Google
    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = "http://localhost:8000/v1/auth/callback/google"

    # Task source
    task_source: Literal["synthetic", "trello", "jira"] = "synthetic"
    trello_api_key: str = ""
    trello_token: str = ""
    jira_base_url: str = ""
    jira_api_token: str = ""

    # Rate limiting
    rate_limit_per_minute: int = 60

    # CORS
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]


@lru_cache
def get_settings() -> Settings:
    """Cached settings singleton."""
    return Settings()
