import json

import httpx
import pytest

from njinet_agent.application.admin_chat import AdminChatReply, AdminChatRequest
from njinet_agent.infrastructure.callbacks.nestjs import NestJsAdminChatReplySender


@pytest.fixture
def recorded_request() -> dict:
    return {}


def make_transport(
    recorded_request: dict, status_code: int = 200
) -> httpx.MockTransport:
    def handler(request: httpx.Request) -> httpx.Response:
        recorded_request["url"] = str(request.url)
        recorded_request["headers"] = request.headers
        recorded_request["json"] = json.loads(request.content)
        return httpx.Response(status_code)

    return httpx.MockTransport(handler)


async def test_sender_posts_to_callback_url(settings, recorded_request):
    sender = NestJsAdminChatReplySender(settings, make_transport(recorded_request))

    await sender.send(
        AdminChatRequest("r-1", "agent-1", "agent-bot", "hi", "jwt", "req-1"),
        AdminChatReply(text="done"),
    )

    expected_url = f"{settings.njinet_backend_url}/internal/agent/reply"
    assert recorded_request["url"] == expected_url
    assert recorded_request["headers"]["njin-secret-key"] == settings.njin_secret_key
    assert recorded_request["json"] == {
        "roomId": "r-1",
        "agentId": "agent-1",
        "agentUsername": "agent-bot",
        "requestId": "req-1",
        "status": "final",
        "text": "done",
    }


async def test_sender_raises_on_server_error(settings, recorded_request):
    sender = NestJsAdminChatReplySender(
        settings, make_transport(recorded_request, status_code=500)
    )

    with pytest.raises(httpx.HTTPStatusError):
        await sender.send(
            AdminChatRequest("r-1", "agent-1", "agent-bot", "hi", "jwt", "req-1"),
            AdminChatReply(status="error", text="boom"),
        )


async def test_admin_chat_sender_uses_request_metadata(settings, recorded_request):
    sender = NestJsAdminChatReplySender(settings, make_transport(recorded_request))
    request = AdminChatRequest("r-1", "agent-1", "agent-bot", "hi", "jwt", "req-1")

    await sender.send(request, AdminChatReply(text="done"))

    assert recorded_request["json"] == {
        "roomId": "r-1",
        "agentId": "agent-1",
        "agentUsername": "agent-bot",
        "requestId": "req-1",
        "status": "final",
        "text": "done",
    }
