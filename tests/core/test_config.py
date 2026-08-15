import pytest
from pydantic import ValidationError

from njinet_agent.core.config import Settings


def test_settings_loads_from_env():
    settings = Settings(
        _env_file=None,
        njin_secret_key="tok",
        njinet_backend_url="http://nest:3001",
        redis_url="redis://localhost:6379",
        llm_api_key="key",
        llm_model="gpt-4o-mini",
    )
    assert settings.recursion_limit == 25


def test_settings_missing_required_raises():
    with pytest.raises(ValidationError):
        Settings(_env_file=None)
