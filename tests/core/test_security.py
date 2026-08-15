import pytest
from fastapi import HTTPException

from njinet_agent.presentation.http.security import verify_service_token


def test_accepts_matching_token():
    verify_service_token("secret", "secret")


@pytest.mark.parametrize("token", [None, "", "wrong"])
def test_rejects_bad_token(token):
    with pytest.raises(HTTPException) as exc:
        verify_service_token(token, "secret")

    assert exc.value.status_code == 401
