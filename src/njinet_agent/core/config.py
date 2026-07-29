from functools import lru_cache

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    njin_secret_key: str
    njinet_backend_url: str
    redis_url: str
    database_url: str
    llm_api_key: SecretStr
    llm_model: str
    recursion_limit: int = 25
    callback_timeout: float = 10.0

    api_v1_prefix: str = "/api/v1"
    cors_origins: list[str] = []


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
