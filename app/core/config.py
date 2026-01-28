"""
Application configuration module.
Loads settings from environment variables.
"""
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    app_name: str = Field(default="Kinorium Scraper API", alias="APP_NAME")
    debug: bool = Field(default=True, alias="DEBUG")
    host: str = Field(default="0.0.0.0", alias="HOST")
    port: int = Field(default=8000, alias="PORT")

    database_url: str = Field(
        default="sqlite+aiosqlite:///./scraper.db",
        alias="DATABASE_URL"
    )

    request_timeout: int = Field(default=30, alias="REQUEST_TIMEOUT")
    browser_timeout: int = Field(default=60000, alias="BROWSER_TIMEOUT")
    headless_mode: bool = Field(default=True, alias="HEADLESS_MODE")

    base_url: str = Field(default="https://ua.kinorium.com", alias="BASE_URL")

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
