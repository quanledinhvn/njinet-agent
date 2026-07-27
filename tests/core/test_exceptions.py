from fastapi import FastAPI
from fastapi.testclient import TestClient

from njinet_agent.core.exceptions import (
    AgentError,
    EnqueueError,
    register_exception_handlers,
)


def make_client(exc: Exception, raise_server_exceptions: bool = True) -> TestClient:
    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/boom")
    async def boom():
        raise exc

    return TestClient(app, raise_server_exceptions=raise_server_exceptions)


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


def test_unexpected_error_returns_structured_body():
    client = make_client(RuntimeError("boom"), raise_server_exceptions=False)

    resp = client.get("/boom")

    assert resp.status_code == 500
    assert resp.json() == {
        "error": {"code": "internal_error", "message": "internal server error"}
    }


def test_unexpected_error_hides_details(caplog):
    client = make_client(
        RuntimeError("redis://user:secret@host"), raise_server_exceptions=False
    )

    resp = client.get("/boom")

    assert "secret" not in resp.text
    assert "redis://user:secret@host" in caplog.text


def test_unknown_route_returns_structured_body():
    app = FastAPI()
    register_exception_handlers(app)

    resp = TestClient(app).get("/khong-ton-tai")

    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "http_error"
