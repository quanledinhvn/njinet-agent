import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from njinet_agent.api.deps import get_arq_pool
from njinet_agent.api.v1.router import api_router
from njinet_agent.core.config import Settings
from njinet_agent.core.exceptions import register_exception_handlers
from njinet_agent.core.security import service_auth


class FakePool:
    """Fake arq pool that records enqueued jobs."""

    def __init__(self):
        self.jobs = []

    async def enqueue_job(self, *args, **kwargs):
        self.jobs.append((args, kwargs))
        return object()


class FakeRedis:
    """Fake Redis that records published messages."""

    def __init__(self):
        self.published = []

    async def publish(self, channel, payload):
        self.published.append((channel, payload))


@pytest.fixture
def settings() -> Settings:
    return Settings(
        service_token="test-token",
        nest_url="http://nest:3001",
        redis_url="redis://localhost:6379",
        database_url="postgresql://localhost/db",
        llm_api_key="key",
        llm_base_url="https://api.deepseek.com",
        llm_model="deepseek-chat",
    )


@pytest.fixture
def fake_pool() -> FakePool:
    return FakePool()


@pytest.fixture
def fake_redis() -> FakeRedis:
    return FakeRedis()


@pytest.fixture
def app(settings: Settings, fake_pool: FakePool) -> FastAPI:
    """Minimal app: v1 router only, no lifespan, so no real Redis is needed."""
    app = FastAPI()
    register_exception_handlers(app)
    app.include_router(api_router, prefix=settings.api_v1_prefix)

    app.dependency_overrides[get_arq_pool] = lambda: fake_pool
    app.dependency_overrides[service_auth] = lambda: None
    return app


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    return TestClient(app)
