from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    app_name: str = "Skincare Compare API"
    environment: str = "development"

    database_url: str = "sqlite:///./skincare.db"

    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    scraper_user_agent: str = (
        "SkincareCompareBot/0.1 (+https://example.com/bot; contact: admin@example.com)"
    )
    scraper_concurrency: int = 4
    scraper_rate_limit_per_host_per_minute: int = 30

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    return Settings() 