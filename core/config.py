from functools import lru_cache
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Habit Tracker API"
    secret_key: str = Field(..., min_length=32)
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24
    database_url: str = "sqlite:///./habit_tracker.db"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls, value: str) -> str:
        insecure_values = {
            "change-me-in-production",
            "changeme",
            "secret",
            "password",
            "default",
        }
        if value.strip().lower() in insecure_values:
            raise ValueError("secret_key is insecure; set a strong unique value via environment")
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
