from dataclasses import dataclass

import httpx

from njinet_agent.application.admin_chat import AdminChatReply, AdminChatRequest
from njinet_agent.core.config import Settings


@dataclass
class NestJsAdminChatReplySender:
    settings: Settings
    transport: httpx.AsyncBaseTransport | None = None

    async def send(self, request: AdminChatRequest, reply: AdminChatReply) -> None:
        async with httpx.AsyncClient(
            timeout=self.settings.callback_timeout, transport=self.transport
        ) as client:
            response = await client.post(
                f"{self.settings.njinet_backend_url}/internal/agent/reply",
                headers={"njin-secret-key": self.settings.njin_secret_key},
                json={
                    "roomId": request.room_id,
                    "agentId": request.agent_id,
                    "agentUsername": request.agent_username,
                    "requestId": request.request_id,
                    "status": reply.status,
                    "text": reply.text,
                },
            )
            response.raise_for_status()
