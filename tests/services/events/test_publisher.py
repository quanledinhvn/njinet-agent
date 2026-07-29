import json

import httpx
import pytest

from njinet_agent.services.events.publisher import send_reply


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


async def test_send_reply_posts_to_callback_url(settings, recorded_request):
    transport = make_transport(recorded_request)

    await send_reply(
        settings,
        room_id="r-1",
        agent_id="agent-1",
        agent_username="agent-bot",
        request_id="req-1",
        status="final",
        text="done",
        transport=transport,
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


async def test_send_reply_raises_on_server_error(settings, recorded_request):
    transport = make_transport(recorded_request, status_code=500)

    with pytest.raises(httpx.HTTPStatusError):
        await send_reply(
            settings,
            room_id="r-1",
            agent_id="agent-1",
            agent_username="agent-bot",
            request_id="req-1",
            status="error",
            text="boom",
            transport=transport,
        )
