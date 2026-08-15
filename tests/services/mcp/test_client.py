from njinet_agent.infrastructure.mcp.client import build_headers


class FakeSettings:
    njin_secret_key = "svc-tok"


def test_headers_carry_context():
    headers = build_headers(FakeSettings(), jwt="jwt-abc")
    assert headers["njin-secret-key"] == "svc-tok"
    assert headers["Authorization"] == "Bearer jwt-abc"
