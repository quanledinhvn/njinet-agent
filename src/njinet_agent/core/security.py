import secrets

from fastapi import Depends, Header, HTTPException

from njinet_agent.core.config import Settings, get_settings


def verify_service_token(token: str | None, expected: str) -> None:
    if not token or not secrets.compare_digest(token, expected):
        raise HTTPException(status_code=401, detail="invalid service token")


async def service_auth(
    x_service_token: str | None = Header(default=None),
    settings: Settings = Depends(get_settings),
) -> None:
    verify_service_token(x_service_token, settings.service_token)