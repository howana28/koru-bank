from functools import lru_cache
from decimal import Decimal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Koru Bank API"
    app_version: str = "2.0.0"
    app_env: str = "development"
    app_secret: str = "development-only-secret"
    database_url: str = "sqlite:///./koru_bank.db"
    cors_origins: str = "http://localhost:5173"
    ai_enabled: bool = False
    ai_provider: str = "disabled"
    ai_model: str = ""
    demo_balance: Decimal = Decimal("2430.70")
    high_value_transfer_limit: Decimal = Decimal("5000.00")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
