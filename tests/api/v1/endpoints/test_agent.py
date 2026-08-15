import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from njinet_agent.core.config import get_settings
from njinet_agent.infrastructure.queue.arq import ArqAdminChatQueue
from njinet_agent.presentation.http.api.agent import router
from njinet_agent.presentation.http.dependencies import get_admin_chat_queue
from njinet_agent.presentation.http.exception_handlers import (
    register_exception_handlers,
)

INVOKE_URL = "/api/v1/agent/invoke"

PAYLOAD = {
    "roomId": "r",
    "text": "hi",
    "actorId": "u",
    "agentId": "room-admin",
    "agentUsername": "agent-bot",
    "requestId": "req-1",
    "jwt": "j",
}


def test_invoke_returns_accepted_shape(client):
    resp = client.post(INVOKE_URL, json=PAYLOAD)

    assert resp.status_code == 200
    assert resp.json() == {"status": "accepted", "runId": "req-1"}


def test_invoke_enqueues_job(client, fake_pool):
    client.post(INVOKE_URL, json=PAYLOAD)

    assert len(fake_pool.jobs) == 1
    args, kwargs = fake_pool.jobs[0]
    assert args[0] == "run_admin_chat_job"
    assert kwargs["_job_id"] == "room:r:req-1"


def test_invoke_rejects_invalid_body(client):
    resp = client.post(INVOKE_URL, json={"roomId": "r"})

    assert resp.status_code == 422
    assert resp.json()["error"]["code"] == "validation_error"


def test_invoke_rejects_missing_agent_id(client):
    payload = {k: v for k, v in PAYLOAD.items() if k != "agentId"}
    resp = client.post(INVOKE_URL, json=payload)

    assert resp.status_code == 422
    assert resp.json()["error"]["code"] == "validation_error"


@pytest.fixture
def auth_client(settings, fake_pool) -> TestClient:
    """App keeping the real service_auth, to exercise the auth layer."""
    app = FastAPI()
    register_exception_handlers(app)
    app.include_router(router, prefix=settings.api_v1_prefix)
    app.dependency_overrides[get_admin_chat_queue] = lambda: ArqAdminChatQueue(
        fake_pool
    )
    app.dependency_overrides[get_settings] = lambda: settings
    return TestClient(app)


@pytest.mark.parametrize("headers", [{}, {"njin-secret-key": "wrong"}])
def test_invoke_requires_valid_service_token(auth_client, fake_pool, headers):
    resp = auth_client.post(INVOKE_URL, json=PAYLOAD, headers=headers)

    assert resp.status_code == 401
    assert fake_pool.jobs == []


def test_invoke_accepts_valid_service_token(auth_client, settings):
    resp = auth_client.post(
        INVOKE_URL, json=PAYLOAD, headers={"njin-secret-key": settings.njin_secret_key}
    )

    assert resp.status_code == 200
