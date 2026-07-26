from njinet_agent.services.mcp.client import build_headers


class FakeSettings:
    service_token = "svc-tok"


def test_headers_carry_context():
    headers = build_headers(
        FakeSettings(), actor_id="u-1", room_id="r-1", jwt="jwt-abc"
    )
    assert headers["X-Service-Token"] == "svc-tok"
    assert headers["X-Act-As"] == "u-1"
    assert headers["X-Room-Id"] == "r-1"
    assert headers["Authorization"] == "Bearer jwt-abc"