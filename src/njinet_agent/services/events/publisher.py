from typing import Literal

import httpx

from njinet_agent.core.config import Settings


async def send_reply(
    settings: Settings,
    *,
    room_id: str,
    agent_id: str,
    agent_username: str,
    request_id: str,
    status: Literal["final", "error"],
    text: str,
) -> None:
    async with httpx.AsyncClient(timeout=settings.callback_timeout) as client:
        resp = await client.post(
            f"{settings.njinet_backend_url}/internal/agent/reply",
            headers={"njin-secret-key": settings.njin_secret_key},
            json={
                "roomId": room_id,
                "agentId": agent_id,
                "agentUsername": agent_username,
                "requestId": request_id,
                "status": status,
                "text": text,
            },
        )
        resp.raise_for_status()
