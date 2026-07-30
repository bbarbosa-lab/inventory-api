from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Inventory API"
    environment: str = "development"
    debug: bool = True
    secret_key: str = "change-me-in-production-use-long-random-string"

    database_url: str = "postgresql+psycopg2://inventory:inventory@localhost:5432/inventory"
    redis_url: str = "redis://localhost:6379/0"

    session_cookie_name: str = "inv_session"
    session_ttl_seconds: int = 86400
    cookie_httponly: bool = True
    cookie_secure: bool = False
    cookie_samesite: str = "lax"

    rate_limit_login_ip: int = 10
    rate_limit_login_account: int = 5
    account_lockout_threshold: int = 5
    account_lockout_minutes: int = 15
    password_min_length: int = 12

    cors_origins: str = "http://localhost:8000"

    @property
    def origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
