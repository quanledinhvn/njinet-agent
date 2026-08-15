import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from njinet_agent.core.config import Settings
from njinet_agent.infrastructure.queue.arq import ArqAdminChatQueue
from njinet_agent.presentation.http.api.agent import router
from njinet_agent.presentation.http.dependencies import get_admin_chat_queue
from njinet_agent.presentation.http.exception_handlers import (
    register_exception_handlers,
)
from njinet_agent.presentation.http.security import service_auth


class FakePool:
    """Fake arq pool that records enqueued jobs."""

    def __init__(self):
        self.jobs = []

    async def enqueue_job(self, *args, **kwargs):
        self.jobs.append((args, kwargs))
        return object()


@pytest.fixture
def settings() -> Settings:
    return Settings(
        njin_secret_key="test-token",
        njinet_backend_url="http://nest:3001",
        redis_url="redis://localhost:6379",
        llm_api_key="key",
        llm_model="gpt-4o-mini",
    )


@pytest.fixture
def fake_pool() -> FakePool:
    return FakePool()


@pytest.fixture
def app(settings: Settings, fake_pool: FakePool) -> FastAPI:
    """Minimal app: v1 router only, no lifespan, so no real Redis is needed."""
    app = FastAPI()
    register_exception_handlers(app)
    app.include_router(router, prefix=settings.api_v1_prefix)

    app.dependency_overrides[get_admin_chat_queue] = lambda: ArqAdminChatQueue(
        fake_pool
    )
    app.dependency_overrides[service_auth] = lambda: None
    return app


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    return TestClient(app)
