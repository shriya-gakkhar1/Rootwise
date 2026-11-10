"""Application configuration loaded from environment variables."""

from urllib.parse import urlparse

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings for the backend."""

    database_url: str
    env: str = "development"

    model_config = SettingsConfigDict(env_file=".env", env_prefix="", extra="ignore")

    @model_validator(mode="after")
    def validate_production_configuration(self) -> "Settings":
        """Reject known development-only configuration in production."""
        if self.env.lower() in {"production", "prod"}:
            parsed_url = urlparse(self.database_url)
            if parsed_url.password in {"rootwise", "rootwise-dev", "change-me"}:
                raise ValueError("production must not use a development database password")
            if parsed_url.hostname in {"localhost", "127.0.0.1", "::1"}:
                raise ValueError("production must not use a loopback database host")
        return self


def get_settings() -> Settings:
    """Build settings from the process environment and optional .env file."""
    return Settings()
