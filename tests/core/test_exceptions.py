from fastapi import FastAPI
from fastapi.testclient import TestClient

from njinet_agent.core.exceptions import (
    AgentError,
    EnqueueError,
    register_exception_handlers,
)


def make_client(exc: Exception) -> TestClient:
    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/boom")
    async def boom():
        raise exc

    return TestClient(app)


def test_agent_error_returns_structured_body():
    resp = make_client(AgentError("something broke")).get("/boom")

    assert resp.status_code == 500
    assert resp.json() == {
        "error": {"code": "agent_error", "message": "something broke"}
    }


def test_enqueue_error_returns_503():
    resp = make_client(EnqueueError("redis down")).get("/boom")

    assert resp.status_code == 503
    assert resp.json() == {"error": {"code": "enqueue_failed", "message": "redis down"}}


def test_unknown_route_returns_structured_body():
    app = FastAPI()
    register_exception_handlers(app)

    resp = TestClient(app).get("/khong-ton-tai")

    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "http_error"
