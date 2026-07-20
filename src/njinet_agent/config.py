from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    service_token: str
    nest_url: str
    redis_url: str
    database_url: str
    llm_api_key: str
    llm_base_url: str
    llm_model: str
    recursion_limit: int = 25


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
