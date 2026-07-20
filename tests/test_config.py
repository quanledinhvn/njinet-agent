from njinet_agent.config import Settings

import pytest
from pydantic import ValidationError


def test_settings_loads_from_env():
    settings = Settings(
        service_token="tok",
        nest_url="http://nest:3001",
        redis_url="redis://localhost:6379",
        database_url="postgresql://localhost/db",
        llm_api_key="key",
        llm_base_url="https://api.deepseek.com",
        llm_model="deepseek-chat",
    )
    assert settings.recursion_limit == 25


def test_settings_missing_required_raises():
    with pytest.raises(ValidationError):
        Settings(_env_file=None)
